#!usr/bin/env bash

# bash build.sh YYYY.M.D

echo "=== Building uhubctl ===";
echo "";

# Take inputs
dt=`date +"%y.%-m.%-d"alpha`;
echo "Settings:";
version="${1:-$dt}";
echo "- Version: $version";
echo ""

# Delete and recreate the build directory
rm -rf Octoprint-uhubctl
rm -rf Octoprint-uhubctl.zip
mkdir Octoprint-uhubctl

# Copy files ans folders we need in the build
cp -r extras Octoprint-uhubctl/extras # this is empty so copy wont move it
cp -r octoprint_uhubctl Octoprint-uhubctl/octoprint_uhubctl
cp -r translations Octoprint-uhubctl/translations
cp babel.cfg Octoprint-uhubctl/babel.cfg
cp LICENSE.txt Octoprint-uhubctl/LICENSE.txt
cp MANIFEST.in Octoprint-uhubctl/MANIFEST.in
cp requirements.txt Octoprint-uhubctl/requirements.txt
cp setup.py Octoprint-uhubctl/setup.py

# Rewrite version
echo -n "Writing plugin version... "
sed -i "s/plugin_version = \"VERSION\"/plugin_version = \"$version\"/" Octoprint-uhubctl/setup.py
echo "done"

# Compress the build directory
echo -n "Zipping... ";
zip -q -r Octoprint-uhubctl.zip Octoprint-uhubctl
rm -rf Octoprint-uhubctl
echo "done";

echo "Done.";