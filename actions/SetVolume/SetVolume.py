from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class SetVolume(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ready(self) -> None:
        self._update_display()

    def _get_volume(self) -> int:
        """Get the configured volume level."""
        settings = self.get_settings()
        return settings.get("volume", 50)

    def _update_display(self) -> None:
        """Update the button display with volume level."""
        volume = self._get_volume()

        icon_path = os.path.join(self.plugin_base.PATH, "assets", "volume.png")
        if os.path.exists(icon_path):
            self.set_media(media_path=icon_path, size=0.75)

        self.set_label(f"{volume}%", position="bottom")

    def on_key_down(self) -> None:
        backend = self.plugin_base.backend
        if backend.is_authenticated:
            volume = self._get_volume()
            backend.set_volume(volume)

    def get_config_rows(self) -> list:
        """Return configuration rows for this action."""
        self.volume_scale = Adw.ActionRow(title="Volume Level")
        self.volume_scale.set_subtitle("Set the target volume (0-100)")

        # Create scale widget
        scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0, 100, 5
        )
        scale.set_value(self._get_volume())
        scale.set_hexpand(True)
        scale.set_valign(Gtk.Align.CENTER)
        scale.set_size_request(200, -1)
        scale.set_draw_value(True)
        scale.connect("value-changed", self._on_volume_changed)

        self.volume_scale.add_suffix(scale)

        return [self.volume_scale]

    def _on_volume_changed(self, scale: Gtk.Scale) -> None:
        """Handle volume slider change."""
        volume = int(scale.get_value())
        settings = self.get_settings()
        settings["volume"] = volume
        self.set_settings(settings)
        self._update_display()
