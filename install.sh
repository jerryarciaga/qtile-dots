#!/bin/sh
# 
# File Name: install.sh
# Author: Jerry Arciaga <jerryarciaga11@gmail.com>
# Purpose: Install dotfiles by creating symlinks for ease of maintenance

CONFIG_FOLDERS=(
    "qtile"
    "alacritty"
    "dunst"
    "rofi"
)
DOTS_DIR=$PWD
CONFIG_DIR="$HOME/.config"

for config_folder in ${CONFIG_FOLDERS[*]}; do
    echo "Installing $config_folder..."
    config=$CONFIG_DIR/$config_folder
    if [ -d $config ]; then
        echo "  $config exists. Deleting folder and setting symlink..."
        rm -r $config
    fi
    echo "  Creating symlink for $config -> $DOTS_DIR/$config_folder"
    ln -sf $DOTS_DIR/$config_folder $config
    echo "  Done."
done
