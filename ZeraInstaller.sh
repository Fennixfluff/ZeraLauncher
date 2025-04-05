#!/bin/bash

echo "Installing dependencies for ZeraLauncher..."

# Update package list and install dependencies
sudo apt update

# Install the required packages for Python3, Tkinter, and Wine
sudo apt install -y python3 python3-pip python3-tk wine

# Install Python packages needed for ZeraLauncher
pip3 install Pillow

# Make ZeraLauncher.py executable
chmod +x ZeraLauncher.py

# Get the current directory where the script is being run
DIR=$(pwd)

# Create a .desktop entry for ZeraLauncher to allow it to be run from the application menu
DESKTOP_FILE="$HOME/.local/share/applications/zeralauncher.desktop"

echo "Creating application menu shortcut..."

# Create the .desktop file for the application menu
cat << EOF > $DESKTOP_FILE
[Desktop Entry]
Version=2.0
Name=ZeraLauncher
Comment=I choose you! ZeraLauncher!
Exec=./ZeraLauncher.py
Icon=$DIR/icon.png
Terminal=false
Type=Application
Categories=Utility;
Path=$DIR
StartupNotify=false
EOF

# Create the desktop shortcut on the user's Desktop
DESKTOP_SHORTCUT="$HOME/Desktop/ZeraLauncher.desktop"

echo "Creating desktop shortcut..."

# Create the .desktop file for the desktop
cat << EOF > $DESKTOP_SHORTCUT
[Desktop Entry]
Version=2.0
Name=ZeraLauncher
Comment=I choose you! ZeraLauncher!
Exec=./ZeraLauncher.py
Icon=$DIR/icon.png
Terminal=false
Type=Application
Categories=Utility;
Path=$DIR
StartupNotify=false
EOF

# Make both the desktop and application menu .desktop files executable
chmod +x $DESKTOP_FILE
chmod +x $DESKTOP_SHORTCUT

echo "Installation complete. You can now run ZeraLauncher from your desktop or application menu, or with:"
echo "  ./ZeraLauncher.py"

