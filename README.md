Note: I'm not publishing this plugin because I don't want to support it. Built it for myself. Use at your own risk.

# Octoprint-uhubctl

**Description** Plugin enables and disables USB ports probably. I wouldn't use this. Well _I_ am but you probably shouldn't. I haven't tested it. If you do, know this only works with pi4s probably.

## Configuration

TBD

## Developer Zone

This plugin depends on you having uhubctl installed and working with a usb hub that's compatible.

You can find more information here: https://github.com/mvp/uhubctl#linux-usb-permissions

To debug try running this on the octoprint server:
```
sudo ./uhubctl/uhubctl --loc=<your location> --ports=<your port> --action=toggle 
```

### Building

You can manually build this project into a zip by running:
```
$ bash build.sh [VERSION]

# ex:
$ bash build.sh 2022.7.4
=== Building PrusaMMU ===

Settings:
- Version: 2022.7.4
- Debug n

Writing plugin version... done
Disabling debug... done
Zipping... done
Done.
```

- Version expects a string (optional, defaults to YYYY.M.Dalpha)

### Versioning

Versioning is done by date so it's clear when the build was installed and made available. Year is
four characters long. Month is one or two characters long depending and does not have a leading zero
for sub ten. Day follows the same rules as month. Beta versions are denoted by a "b" directly
following the day and then a number describing what beta version it is. Sequentially `2022.1.1b1`
comes before `2022.1.1`.

Format:
```
YYYY.M.D
YYYY.M.Db#
```

Examples:
```
2022.10.4
2022.1.20
2022.1.20b2
```