$(() => {
  const PLUGIN_NAME = "uhubctl";
  const LOG_PLUGIN_NAME = `plugin_${PLUGIN_NAME}`;

  function UhubctlViewModel(parameters) {
    const self = this;
    self.globalSettings = parameters[0]; // settingsViewModel
    self.loginState = parameters[1]; // loginStateViewModel
    // self.printerState = parameters[2]; // printerStateViewModel

    self.settings = {};

    self.port = ko.observable(0);

    /* =============================
     * ==== Button Functions ====
     * =============================*/

    self.togglePort = () => {
      OctoPrint.simpleApiCommand(PLUGIN_NAME, "toggle_port");
    };

    self.enablePort = () => {
      OctoPrint.simpleApiCommand(PLUGIN_NAME, "enable_port");
    };

    self.disablePort = () => {
      OctoPrint.simpleApiCommand(PLUGIN_NAME, "disable_port");
    };

    /* =============================
     * ==== Octoprint Functions ====
     * =============================
     * https://docs.octoprint.org/en/master/plugins/viewmodels.html */

    /**
     * Fired when a plugin message is sent from the server.
     * 
     * @param {string} plugin - The name of the plugin that triggered the message.
     * @param {data} - The data sent from the api.
     */
    self.onDataUpdaterPluginMessage = (plugin, data) => {
      if (!self.loginState.isUser() || plugin !== PLUGIN_NAME) {
        return;
      }

      log("onDataUpdaterPluginMessage", plugin, data);
    }

    /**
     * Called per view model before attempting to bind it to its binding targets.
     */
    self.onBeforeBinding = function () {
      self.settings = self.globalSettings.settings.plugins.uhubctl;
    };

    /**
     * Called after the startup of the web app has been completed. Used to show/hide the nav and
     * load the printer state.
     */
    self.onStartupComplete = () => {
      log("onStartupComplete");
      self.port(self.settings.port());
    }

    /**
     * Called just before the settings view model is sent to the server. This is useful, for
     * example, if your plugin needs to compute persisted settings from a custom view model.
     */
    self.onSettingsBeforeSave = function () {
      self.port(self.settings.port());
    };

    /* =============================
     * =====  Misc. Functions  =====
     * ============================= */

    /**
     * Simple function to log out debug messages if debug is on. Use like you would console.log().
     * 
     * @param {...any} args - arguments to pass directly to console.warn.
     */
    const log = (...args) => {
      if (!self.settings.debug()) {
        return;
      }
      const d = new Date();
      const showtime = `[${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}]`
      console.log(String.fromCodePoint(0x1F6A9), showtime, `${LOG_PLUGIN_NAME}:`, ...args);
    };
  }

  OCTOPRINT_VIEWMODELS.push({
    construct: UhubctlViewModel,
    dependencies: ["settingsViewModel", "loginStateViewModel", "printerStateViewModel"],
    elements: ["#navbar_plugin_uhubctl"]
  });
});