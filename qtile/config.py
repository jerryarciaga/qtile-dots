# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile import bar, layout, qtile, widget, hook
from libqtile.backend.wayland import InputConfig
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
import os.path, subprocess
import pulsectl_asyncio
import json

mod = "mod4"
terminal = "/usr/bin/alacritty"

flavor = "mocha" # Flavor choices can be latte, frappe, macchiato and mocha
# Color palette from Catpuccin project
# palette.json was downloaded from
#   https://github.com/catppuccin/palette/blob/main/palette.json
def json_read(filename:str):
    with open(filename) as input:
        return json.load(input)
palette = os.path.join(os.path.expanduser('~'), '.config/qtile/palette.json')
catpuccin = json_read(palette)[flavor]["colors"]

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "d", lazy.spawn("rofi -show drun"), desc="Rofi drun"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "1234567890"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(border_focus=catpuccin["lavender"]["hex"], border_width=1),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=5,
    foreground=catpuccin["text"]["hex"],
    background=catpuccin["base"]["hex"],
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        wallpaper=os.path.join(os.path.expanduser("~"),
            ".config/qtile/wallpaper/hk_greenpath.jpg"),
        wallpaper_mode="stretch",
        top=bar.Bar(
            [
                # widget.CurrentLayout(),
                widget.GroupBox(
                    active=catpuccin["text"]["hex"],
                    highlight_method='line',
                    highlight_color=[
                        catpuccin['surface0']['hex'],
                        catpuccin['green']['hex'],
                    ],
                    hide_unused=True,
                ),
                widget.Prompt(
                    bell_style=None,
                ),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                # widget.Systray(),
                widget.Clock(
                    format="  %a %d %b    %H:%M",
                ),
                widget.Spacer(),
                widget.Backlight(
                    backlight_name="intel_backlight",
                    fmt=" {}",
                    change_command=None,
                    step=5,
                    min_brightness=5,
                ),
                widget.PulseVolume(
                    fmt="  {}",
                    mute_format="",
                    limit_max_volume=True,
                ),
                widget.Battery(
                    charge_char="",
                    discharge_char="",
                    full_char="",
                    format="{char} {percent:1.0%}",
                    update_interval=5,
                ),
            ],
            30,
            background=catpuccin["crust"]["hex"],
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = {
    "type:touchpad": InputConfig(
        tap=True,
        middle_emulation=True,
        dwt=True,
    ),
}

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24


## Custom keybindings

# Manual lock screen
keys.extend(
    [
        Key([mod, "control"], "s",
            lazy.spawn(
                os.path.join(os.path.expanduser("~"),".config/qtile/scripts/screenlocker.sh")),
            desc="Manually lock screen",
        )
    ]
)

# Adjust brightness
keys.extend(
    [
        # NOTE: Give yourself read/write access to /sys/class/backlight/{}/brightness
        Key([mod], "right", lazy.widget["backlight"].change_backlight(widget.backlight.ChangeDirection.UP)),
        Key([mod], "left", lazy.widget["backlight"].change_backlight(widget.backlight.ChangeDirection.DOWN)),
    ]
)

# Adjust volume
keys.extend(
    [
        Key([mod], "up", lazy.widget["pulsevolume"].increase_vol(), desc="Increase volume"),
        Key([mod], "down", lazy.widget["pulsevolume"].decrease_vol(), desc="Decrease volume"),
        Key([mod], "m", lazy.widget["pulsevolume"].mute(), desc="Mute volume"),
    ]
)

# Applications
keys.extend(
    [
        # Firefox
        Key([mod], "b", lazy.spawn("/usr/bin/firefox"), desc="Launch Firefox"),
        Key([mod, "shift"], "b", lazy.spawn("/usr/bin/firefox --private-window"), desc="Launch Firefox"),

        # Screenshot
        Key([mod, "shift"], "s", lazy.spawn(
                os.path.join(os.path.expanduser("~"),
                ".config/qtile/scripts/screenshot.sh"),
            ),
            desc="Take screenshot"
        ),
    ]
)

@hook.subscribe.suspend
def lock_on_sleep():
    # Run screen locker
    qtile.spawn(os.path.join(os.path.expanduser("~"),
        ".config/qtile/scripts/screenlocker.sh"))

# TODO: Fix startup hook
# @hook.subscribe.startup
# def autostart():
#     subprocess.run(["/usr/bin/dunst"])

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "Qtile"
