#! /bin/sh

export PRODUCTION=1
logger "Starting PiPrint GUI"
while [ 1 ] ; do
    python3 /home/pi/piprint/gui.py 2>&1 | logger
    sleep 5
    logger "Restarting PiPrint GUI"
done
