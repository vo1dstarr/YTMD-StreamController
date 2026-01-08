import requests
from typing import Optional, Any, Callable
from loguru import logger


class YTMDBackend:
    """Backend client for YouTube Music Desktop App Companion Server API v1."""

    APP_ID = "streamcontroller-ytmd"
    APP_NAME = "StreamController YTMD Plugin"
    APP_VERSION = "1.0.0"

    def __init__(self, plugin_base):
        self.plugin_base = plugin_base
        self._token: Optional[str] = None
        self._state_callbacks: list[Callable] = []
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from plugin storage."""
        settings = self.plugin_base.get_settings()
        self._host = settings.get("host", "localhost")
        self._port = settings.get("port", 9863)
        self._token = settings.get("token")

    def _save_settings(self) -> None:
        """Save settings to plugin storage."""
        settings = self.plugin_base.get_settings()
        settings["host"] = self._host
        settings["port"] = self._port
        settings["token"] = self._token
        self.plugin_base.set_settings(settings)

    @property
    def base_url(self) -> str:
        """Get the base API URL."""
        return f"http://{self._host}:{self._port}/api/v1"

    @property
    def is_authenticated(self) -> bool:
        """Check if we have a valid token."""
        return self._token is not None

    def set_connection(self, host: str, port: int) -> None:
        """Update connection settings."""
        self._host = host
        self._port = port
        self._save_settings()

    def request_auth_code(self) -> Optional[str]:
        """
        Request an authentication code from YTMD.
        Returns the code if successful, None otherwise.
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/requestcode",
                json={
                    "appId": self.APP_ID,
                    "appName": self.APP_NAME,
                    "appVersion": self.APP_VERSION
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("code")
        except requests.RequestException as e:
            logger.error(f"YTMD: Failed to request auth code: {e}")
            return None

    def exchange_code_for_token(self, code: str) -> bool:
        """
        Exchange the auth code for a token.
        User must approve in YTMD app within 30 seconds.
        Returns True if successful.
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/request",
                json={
                    "appId": self.APP_ID,
                    "code": code
                },
                timeout=35  # 30s user approval + buffer
            )
            response.raise_for_status()
            data = response.json()
            self._token = data.get("token")
            if self._token:
                self._save_settings()
                return True
            return False
        except requests.RequestException as e:
            logger.error(f"YTMD: Failed to exchange code for token: {e}")
            return False

    def authenticate(self) -> tuple[bool, str]:
        """
        Perform full authentication flow.
        Returns (success, message) tuple.
        """
        code = self.request_auth_code()
        if not code:
            return False, "Failed to get auth code. Is YTMD running?"

        # User needs to approve in YTMD app
        success = self.exchange_code_for_token(code)
        if success:
            return True, "Authentication successful!"
        return False, "Authentication failed. Did you approve in YTMD?"

    def clear_auth(self) -> None:
        """Clear stored authentication token."""
        self._token = None
        self._save_settings()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> Optional[Any]:
        """Make an authenticated API request."""
        if not self._token:
            logger.warning("YTMD: Not authenticated")
            return None

        try:
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers={"Authorization": self._token},
                json=json_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.RequestException as e:
            logger.error(f"YTMD: API request failed: {e}")
            return None

    def get_state(self) -> Optional[dict]:
        """Get current player state."""
        return self._make_request("GET", "/state")

    def send_command(self, command: str, data: Any = None) -> bool:
        """
        Send a command to YTMD.

        Commands:
        - playPause, play, pause, next, previous
        - volumeUp, volumeDown, setVolume (data: 0-100), mute, unmute
        - shuffle, repeatMode (data: 0=None, 1=All, 2=One)
        - toggleLike, toggleDislike
        """
        payload = {"command": command}
        if data is not None:
            payload["data"] = data

        result = self._make_request("POST", "/command", payload)
        return result is not None or True  # Command endpoints may return empty

    def play_pause(self) -> bool:
        """Toggle play/pause."""
        return self.send_command("playPause")

    def next_track(self) -> bool:
        """Skip to next track."""
        return self.send_command("next")

    def previous_track(self) -> bool:
        """Go to previous track."""
        return self.send_command("previous")

    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        volume = max(0, min(100, volume))
        return self.send_command("setVolume", volume)

    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode."""
        return self.send_command("shuffle")

    def set_repeat_mode(self, mode: int) -> bool:
        """Set repeat mode (0=None, 1=All, 2=One)."""
        mode = max(0, min(2, mode))
        return self.send_command("repeatMode", mode)

    def register_state_callback(self, callback: Callable[[dict], None]) -> None:
        """Register a callback for state updates."""
        self._state_callbacks.append(callback)

    def unregister_state_callback(self, callback: Callable[[dict], None]) -> None:
        """Unregister a state callback."""
        if callback in self._state_callbacks:
            self._state_callbacks.remove(callback)

    def notify_state_update(self, state: dict) -> None:
        """Notify all registered callbacks of a state update."""
        for callback in self._state_callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"YTMD: State callback error: {e}")
