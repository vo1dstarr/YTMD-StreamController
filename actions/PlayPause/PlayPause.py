from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os


class PlayPause(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_playing = False

    def on_ready(self) -> None:
        self._update_icon()

    def on_key_down(self) -> None:
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            backend.play_pause()
            # Toggle local state for immediate feedback
            self._is_playing = not self._is_playing
            self._update_icon()

    def _update_icon(self) -> None:
        """Update the button icon based on play state."""
        if self._is_playing:
            icon_name = "pause.png"
        else:
            icon_name = "play.png"

        icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if os.path.exists(icon_path):
            self.set_media(media_path=icon_path, size=0.75)
        else:
            # Fallback: use label if icon missing
            label = "||" if self._is_playing else ">"
            self.set_label(label, position="center")

    def on_tick(self) -> None:
        """Periodically sync state with YTMD."""
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            state = backend.get_state()
            if state and "player" in state:
                # trackState: -1=Unknown, 0=Paused, 1=Playing, 2=Buffering
                track_state = state["player"].get("trackState", -1)
                was_playing = self._is_playing
                self._is_playing = track_state == 1
                if was_playing != self._is_playing:
                    self._update_icon()
