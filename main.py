# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import actions
from .actions.SimpleAction.SimpleAction import SimpleAction

class PluginTemplate(PluginBase):
    def __init__(self):
        super().__init__()

        ## Register actions
        self.simple_action_holder = ActionHolder(
            plugin_base = self,
            action_base = SimpleAction,
            action_id = "dev_vo1dstarr_YTMD-StreamController::SimpleAction", # Change this to your own plugin id
            action_name = "Simple Action",
        )
        self.add_action_holder(self.simple_action_holder)

        # Register plugin
        self.register(
            plugin_name = "YTMD-StreamController",
            github_repo = "https://github.com/vo1dstarr/YTMD-StreamController",
            plugin_version = "0.0.1",
            app_version = "1.1.1-alpha"
        )
