from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os


class Shuffle(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shuffle_enabled = False

    def on_ready(self) -> None:
        self._update_icon()

    def on_key_down(self) -> None:
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            backend.toggle_shuffle()
            # Toggle local state for immediate feedback
            self._shuffle_enabled = not self._shuffle_enabled
            self._update_icon()

    def _update_icon(self) -> None:
        """Update the button icon based on shuffle state."""
        if self._shuffle_enabled:
            icon_name = "shuffle_on.png"
        else:
            icon_name = "shuffle.png"

        icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        if os.path.exists(icon_path):
            self.set_media(media_path=icon_path, size=0.75)
        else:
            # Fallback: use label with indicator
            label = "SHUF" if not self._shuffle_enabled else "[SHUF]"
            self.set_label(label, position="center")

    def on_tick(self) -> None:
        """Periodically sync state with YTMD."""
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            state = backend.get_state()
            if state and "player" in state:
                queue = state["player"].get("queue", {})
                was_enabled = self._shuffle_enabled
                # Note: YTMD API may not expose shuffle state directly in queue
                # This is a placeholder for when the state is available
                if "shuffle" in queue:
                    self._shuffle_enabled = queue.get("shuffle", False)
                    if was_enabled != self._shuffle_enabled:
                        self._update_icon()
