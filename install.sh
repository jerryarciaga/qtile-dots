#!/bin/sh

CONFIG_FOLDERS=(
    "qtile"
    "alacritty"
    "dunst"
)
DOTS_DIR=$PWD
CONFIG_DIR="$HOME/.config"

# Install dotfiles by creating symlinks to local copy.
for config_folder in ${CONFIG_FOLDERS[*]}; do
    echo "Installing $config_folder..."
    if [[ -d $CONFIG_DIR/$config_folder ]]; then
        echo "$CONFIG_DIR/$config_folder exists. Deleting and setting symlink..."
    fi
    echo "Creating symlink for $CONFIG_DIR/$config_folder -\> $DOTS_DIR/$config_folder"
    ln -sf $DOTS_DIR/$config_folder $CONFIG_DIR/$config_folder
done
