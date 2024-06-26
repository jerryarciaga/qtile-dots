#!/bin/sh

# Lock this screen with all these fancy effects
swaylock \
	--screenshots \
	--clock \
    --datestr "%a, %d %b %g" \
	--indicator \
	--indicator-radius 100 \
	--indicator-thickness 7 \
	--effect-blur 7x5 \
	--effect-vignette 0.5:0.5 \
	--ring-color bb00cc \
	--key-hl-color 880033 \
	--line-color 00000000 \
	--inside-color 00000088 \
	--separator-color 00000000 \
	--grace 0.5 \
	--grace-no-mouse \
	--fade-in 0.2
