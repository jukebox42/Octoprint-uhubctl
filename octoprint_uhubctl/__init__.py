# coding=utf-8
from __future__ import absolute_import, unicode_literals
from json import dumps

import octoprint.plugin
from octoprint.server import user_permission
from octoprint.events import Events
import subprocess

# === Constants ===

PLUGIN_NAME = "uhubctl"
EVENT_PREFIX = "plugin_{}_".format(PLUGIN_NAME)
DEFAULT_PATH = "/home/john/uhubctl" # /home/pi/uhubctl
DEFAULT_HUB = "1-1"

# === Setting Keys ===

KEY_DEBUG = "debug"
KEY_PATH = "path"
KEY_HUB = "hub"
KEY_PORT = "port"
KEY_AUTOMATIC = "automatic"

# === Events ===
REGISTER_ENABLE_PORT = "enable_port"
REGISTER_DISABLE_PORT = "disable_port"
REGISTER_TOGGLE_PORT = "toggle_port"
EVENT_ENABLE_PORT = "{}{}".format(EVENT_PREFIX, REGISTER_ENABLE_PORT)
EVENT_DISABLE_PORT = "{}{}".format(EVENT_PREFIX, REGISTER_DISABLE_PORT)
EVENT_TOGGLE_PORT = "{}{}".format(EVENT_PREFIX, REGISTER_TOGGLE_PORT)


class Uhubctl(octoprint.plugin.StartupPlugin,
              octoprint.plugin.TemplatePlugin,
              octoprint.plugin.AssetPlugin,
              octoprint.plugin.EventHandlerPlugin,
              octoprint.plugin.SimpleApiPlugin,
              octoprint.plugin.SettingsPlugin):

  def __init__(self):
    self.config = dict(
      debug=False,
      # TODO: make this a string so we can do things like 3,4
      port=1,
      hub=DEFAULT_HUB,
      automatic=False,
      path=DEFAULT_PATH,
    )

  # ======== Startup ========

  def on_after_startup(self):
    self._log("on_after_startup")
    # TODO: Detect if we have uhubctl installed
    self._refresh_config()

  # ======== TemplatePlugin ========

  def get_template_configs(self):
    return [
      dict(type="settings", custom_bindings=False)
    ]

  # ======== AssetPlugin ========

  def get_assets(self):
    return dict(
      js=["uhubctl.js"]
    )

  # ======== SimpleApiPlugin ========

  def get_api_commands(self):
    return dict(
      enable_port=[],
      disable_port=[],
      toggle_port=[],
    )

  def on_api_command(self, command, data):
    if command == "toggle_port":
      if not user_permission.can():
        return abort(403, "Insufficient permissions")

      self._fire_event(EVENT_TOGGLE_PORT)

    if command == "enable_port":
      if not user_permission.can():
        return abort(403, "Insufficient permissions")

      self._fire_event(EVENT_ENABLE_PORT)

    if command == "disable_port":
      if not user_permission.can():
        return abort(403, "Insufficient permissions")
      
      self._fire_event(EVENT_DISABLE_PORT)

  # ======== EventHandlerPlugin ========

  def _fire_event(self, key, payload=None):
    self._event_bus.fire(key, payload=payload)

  def register_custom_events(*args, **kwargs):
    return [
      REGISTER_ENABLE_PORT,
      REGISTER_DISABLE_PORT,
      REGISTER_TOGGLE_PORT,
    ]

  def on_event(self, event, payload=None):
    # TODO: Would be cool if we implemented read so they could see what port to use.

    if event == EVENT_ENABLE_PORT:
      self._log("on_event {}".format(event), obj=payload, debug=True)
      self._enable_port()

    if event == EVENT_DISABLE_PORT:
      self._log("on_event {}".format(event), obj=payload, debug=True)
      self._disable_port()

    if event == EVENT_TOGGLE_PORT:
      self._log("on_event {}".format(event), obj=payload, debug=True)
      self._toggle_port()

    if event == Events.PRINT_STARTED:
      self._log("on_event {}".format(event), obj=payload, debug=True)
      if self.config[KEY_AUTOMATIC]:
        self._enable_port()

    # Handle done state
    if event == Events.PRINT_DONE:
      self._log("on_event {}".format(event), obj=payload, debug=True)
      if self.config[KEY_AUTOMATIC]:
        self._disable_port()

  # ======== SettingsPlugin ========

  def get_settings_defaults(self):
    return dict(
      debug=False,
      port=1,
      hub=DEFAULT_HUB,
      automatic=False,
      path=DEFAULT_PATH,
    )

  def on_settings_save(self, data):
    self._log("on_settings_save", debug=True)

    # save settings
    octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
    self._refresh_config()

  def _refresh_config(self):
    self.config[KEY_DEBUG] = self._settings.get_boolean([KEY_DEBUG])
    self.config[KEY_PORT] = self._settings.get_int([KEY_PORT])
    self.config[KEY_AUTOMATIC] = self._settings.get_boolean([KEY_AUTOMATIC])
    self.config[KEY_HUB] = self._settings.get([KEY_HUB])
    self.config[KEY_PATH] = self._settings.get([KEY_PATH])

  # ======== SoftwareUpdatePlugin ========
  # https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
  
  def get_update_information(self):
    githubUrl = "https://github.com/jukebox42/Octoprint-uhubctl"
    pipPath = "/releases/download/{target_version}/Octoprint-uhubctl.zip"
    # Define the configuration for your plugin to use with the Software Update.
    return dict(
	    PrusaMMU=dict(
        displayName=PLUGIN_NAME,
        displayVersion=self._plugin_version,

        # version check: github repository
        type="github_release",
        user="jukebox42",
        repo="Octoprint-uhubctl",
        current=self._plugin_version,

        # update method: pip
        pip=githubUrl+pipPath
      )
    )

  # ======== uhubctl ========
  # https://github.com/mvp/uhubctl#raspberry-pi-4b

  def _call_uhubctl(self, enable=True, toggle=False):
    args=[
      "./uhubctl",
      "--loc={}".format(self.config[KEY_HUB]),
      "--ports={}".format(self.config[KEY_PORT]),
    ]
    if toggle:
      args.append("--action=toggle")
    else:
      args.append("--action={}".format("on" if enable else "off"))
    output = subprocess.run(args, capture_output=True, cwd=self.config[KEY_PATH])
    self._log(
      "_call_uhubctl: {} | {} | {}".format(output.returncode, output.stderr.decode("utf-8") , output.stdout.decode("utf-8")),
      obj=args,
      debug=True)

  def _enable_port(self):
    self._log("_enable_port", debug=True)
    self._call_uhubctl(True)

  def _disable_port(self):
    self._log("_disable_port", debug=True)
    self._call_uhubctl(False)

  def _toggle_port(self):
    self._log("_toggle_port", debug=True)
    self._call_uhubctl(toggle=True)

  # ======== Misc ========

  def _log(self, msg, obj=None, debug=False):
    if debug and self.config[KEY_DEBUG]:
      if obj is not None:
        msg = "{} {}".format(msg, dumps(obj))
      self._logger.debug(msg)
      self._plugin_manager.send_plugin_message(
        self._identifier,
        dict(
          action="debug",
          msg=msg,
        )
      )
    else:
      self._logger.info(msg)


__plugin_name__ = "uhubctl"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_implementation__ = Uhubctl()
__plugin_hooks__ = {
  "octoprint.events.register_custom_events":  __plugin_implementation__.register_custom_events,
  # "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
}
