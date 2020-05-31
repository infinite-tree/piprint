#! /bin/sh
mkdir -p /home/pi/piprint/tmp
/home/pi/piprint/server-wrapper.sh &
/home/pi/piprint/gui-wrapper.sh
