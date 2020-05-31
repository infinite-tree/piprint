#! /bin/sh

export PRODUCTION=1
logger "Starting PiPrint WebServer"
while [ 1 ] ; do
    python3 /home/pi/piprint/upload-server.py 2>&1 | logger
    sleep 5
    logger "Restarting PiPrint WebServer"
done
