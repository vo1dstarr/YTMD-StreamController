from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os


class NextTrack(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "next.png")
        if os.path.exists(icon_path):
            self.set_media(media_path=icon_path, size=0.75)
        else:
            self.set_label(">>", position="center")

    def on_key_down(self) -> None:
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            backend.next_track()
