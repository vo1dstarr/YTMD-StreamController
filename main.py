# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import plugin components
from .backend import YTMDBackend
from .settings import PluginSettings

# Import actions
from .actions.PlayPause.PlayPause import PlayPause
from .actions.NextTrack.NextTrack import NextTrack
from .actions.SetVolume.SetVolume import SetVolume
from .actions.Shuffle.Shuffle import Shuffle
from .actions.Repeat.Repeat import Repeat


class YTMDPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        # Enable plugin settings
        self.has_plugin_settings = True

        # Initialize backend
        self.backend = YTMDBackend(self)

        # Initialize settings manager
        self._settings_manager = PluginSettings(self)

        # Register actions
        self.play_pause_holder = ActionHolder(
            plugin_base=self,
            action_base=PlayPause,
            action_id="dev_vo1dstarr_ytmd::PlayPause",
            action_name="Play/Pause",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.play_pause_holder)

        self.next_track_holder = ActionHolder(
            plugin_base=self,
            action_base=NextTrack,
            action_id="dev_vo1dstarr_ytmd::NextTrack",
            action_name="Next Track",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.next_track_holder)

        self.set_volume_holder = ActionHolder(
            plugin_base=self,
            action_base=SetVolume,
            action_id="dev_vo1dstarr_ytmd::SetVolume",
            action_name="Set Volume",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.set_volume_holder)

        self.shuffle_holder = ActionHolder(
            plugin_base=self,
            action_base=Shuffle,
            action_id="dev_vo1dstarr_ytmd::Shuffle",
            action_name="Shuffle",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.shuffle_holder)

        self.repeat_holder = ActionHolder(
            plugin_base=self,
            action_base=Repeat,
            action_id="dev_vo1dstarr_ytmd::Repeat",
            action_name="Repeat",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED,
            },
        )
        self.add_action_holder(self.repeat_holder)

        # Register plugin
        self.register(
            plugin_name="YTMD Controller",
            github_repo="https://github.com/vo1dstarr/YTMD-StreamController",
            plugin_version="1.0.0",
            app_version="1.5.0"
        )

    def get_settings_area(self):
        """Return the plugin settings UI."""
        return self._settings_manager.get_settings_area()
