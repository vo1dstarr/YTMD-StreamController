from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os


class Repeat(ActionBase):
    # Repeat modes: 0=None, 1=All, 2=One
    REPEAT_NONE = 0
    REPEAT_ALL = 1
    REPEAT_ONE = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._repeat_mode = self.REPEAT_NONE

    def on_ready(self) -> None:
        self._update_icon()

    def on_key_down(self) -> None:
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            # Cycle through modes: None -> All -> One -> None
            next_mode = (self._repeat_mode + 1) % 3
            backend.set_repeat_mode(next_mode)
            self._repeat_mode = next_mode
            self._update_icon()

    def _update_icon(self) -> None:
        """Update the button icon based on repeat mode."""
        icon_map = {
            self.REPEAT_NONE: "repeat_off.png",
            self.REPEAT_ALL: "repeat_all.png",
            self.REPEAT_ONE: "repeat_one.png",
        }
        label_map = {
            self.REPEAT_NONE: "RPT",
            self.REPEAT_ALL: "[ALL]",
            self.REPEAT_ONE: "[ONE]",
        }

        icon_name = icon_map.get(self._repeat_mode, "repeat_off.png")
        icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)

        if os.path.exists(icon_path):
            self.set_media(media_path=icon_path, size=0.75)
        else:
            # Fallback: use label
            label = label_map.get(self._repeat_mode, "RPT")
            self.set_label(label, position="center")

    def on_tick(self) -> None:
        """Periodically sync state with YTMD."""
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            state = backend.get_state()
            if state and "player" in state:
                queue = state["player"].get("queue", {})
                # repeatMode: 0=None, 1=All, 2=One
                if "repeatMode" in queue:
                    old_mode = self._repeat_mode
                    self._repeat_mode = queue.get("repeatMode", 0)
                    if old_mode != self._repeat_mode:
                        self._update_icon()
