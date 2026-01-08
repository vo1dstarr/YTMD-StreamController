import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main import YTMDPlugin


class PluginSettings:
    """Settings UI for YTMD plugin authentication and connection."""

    def __init__(self, plugin_base: "YTMDPlugin"):
        self.plugin_base = plugin_base

    def get_settings_area(self) -> Adw.PreferencesGroup:
        """Build and return the settings UI."""
        group = Adw.PreferencesGroup()
        group.set_title("YouTube Music Desktop")
        group.set_description("Configure connection to YTMD Companion Server")

        # Host entry
        self.host_row = Adw.EntryRow(title="Host")
        self.host_row.set_text(self._get_setting("host", "localhost"))
        self.host_row.connect("changed", self._on_host_changed)
        group.add(self.host_row)

        # Port entry
        self.port_row = Adw.EntryRow(title="Port")
        self.port_row.set_text(str(self._get_setting("port", 9863)))
        self.port_row.connect("changed", self._on_port_changed)
        group.add(self.port_row)

        # Status row
        self.status_row = Adw.ActionRow(title="Status")
        self._update_status_label()
        group.add(self.status_row)

        # Auth button row
        auth_row = Adw.ActionRow(title="Authentication")
        auth_row.set_subtitle("Authenticate with YTMD app")

        self.auth_button = Gtk.Button(label="Authenticate")
        self.auth_button.set_valign(Gtk.Align.CENTER)
        self.auth_button.add_css_class("suggested-action")
        self.auth_button.connect("clicked", self._on_auth_clicked)
        auth_row.add_suffix(self.auth_button)

        self.disconnect_button = Gtk.Button(label="Disconnect")
        self.disconnect_button.set_valign(Gtk.Align.CENTER)
        self.disconnect_button.add_css_class("destructive-action")
        self.disconnect_button.connect("clicked", self._on_disconnect_clicked)
        auth_row.add_suffix(self.disconnect_button)

        group.add(auth_row)

        self._update_button_visibility()
        return group

    def _get_setting(self, key: str, default):
        """Get a setting value."""
        settings = self.plugin_base.get_settings()
        return settings.get(key, default)

    def _set_setting(self, key: str, value) -> None:
        """Set a setting value."""
        settings = self.plugin_base.get_settings()
        settings[key] = value
        self.plugin_base.set_settings(settings)

    def _on_host_changed(self, entry: Adw.EntryRow) -> None:
        """Handle host change."""
        self._set_setting("host", entry.get_text())
        if hasattr(self.plugin_base, 'backend'):
            self.plugin_base.backend._host = entry.get_text()

    def _on_port_changed(self, entry: Adw.EntryRow) -> None:
        """Handle port change."""
        try:
            port = int(entry.get_text())
            self._set_setting("port", port)
            if hasattr(self.plugin_base, 'backend'):
                self.plugin_base.backend._port = port
        except ValueError:
            pass

    def _update_status_label(self) -> None:
        """Update the status display."""
        if self.plugin_base.backend and self.plugin_base.backend.is_authenticated:
            self.status_row.set_subtitle("Connected")
            self.status_row.remove_css_class("error")
            self.status_row.add_css_class("success")
        else:
            self.status_row.set_subtitle("Not connected")
            self.status_row.remove_css_class("success")
            self.status_row.add_css_class("error")

    def _update_button_visibility(self) -> None:
        """Update which buttons are visible."""
        is_auth = self.plugin_base.backend and self.plugin_base.backend.is_authenticated
        self.auth_button.set_visible(not is_auth)
        self.disconnect_button.set_visible(is_auth)

    def _on_auth_clicked(self, button: Gtk.Button) -> None:
        """Handle authenticate button click."""
        button.set_sensitive(False)
        button.set_label("Waiting for approval...")

        def do_auth():
            success, message = self.plugin_base.backend.authenticate()
            GLib.idle_add(self._on_auth_complete, success, message)

        thread = threading.Thread(target=do_auth, daemon=True)
        thread.start()

    def _on_auth_complete(self, success: bool, message: str) -> None:
        """Handle authentication completion."""
        self.auth_button.set_sensitive(True)
        self.auth_button.set_label("Authenticate")
        self._update_status_label()
        self._update_button_visibility()

        if success:
            self.status_row.set_subtitle(message)
        else:
            self.status_row.set_subtitle(f"Error: {message}")

    def _on_disconnect_clicked(self, button: Gtk.Button) -> None:
        """Handle disconnect button click."""
        self.plugin_base.backend.clear_auth()
        self._update_status_label()
        self._update_button_visibility()
