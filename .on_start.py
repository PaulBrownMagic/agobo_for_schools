#! /usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep
from subprocess import check_output, call
GPIO.setmode(GPIO.BCM)
RED = 4
GREEN = 17
GPIO.setup(RED, GPIO.OUT, initial = 1)
GPIO.setup(GREEN, GPIO.OUT, initial = 0)

def has_ip():
    return len(check_output(["hostname", "-I"]).decode('utf-8').strip()) > 6

def has_license():
    return len(check_output(["cat", "/etc/vnc/licensekey"]).decode('utf-8').strip()) > 15

def vncserver_started():
    return '1.pid' in subprocess.check_output(["ls", ".vnc"]).decode('utf-8').strip()

red, green = False, True

# Get IP address
for _ in range(10):
    red = not red
    GPIO.output(RED, red)
    sleep(0.03)
while not has_ip():
    red = not red
    GPIO.output(RED, red)
    sleep(0.1)

GPIO.output(RED, 0)
GPIO.output(GREEN, 1)

# Assert License
for _ in range(10):
    red = not red
    green = not green
    GPIO.output(RED, red)
    GPIO.output(GREEN, green)
    sleep(0.03)
while not has_license():
    red = not red
    green = not green
    GPIO.output(RED, red)
    GPIO.output(GREEN, green)
    call(["sudo","vnclicense","-add", "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"])  # You'll need your own key here, they are free
    sleep(0.1)

GPIO.output(RED, 0)
GPIO.output(GREEN, 1)

# Start VNC server
for _ in range(10):
    green = not green
    GPIO.output(GREEN, green)
    sleep(0.03)
call(["vncserver",":1"])
while not vncserver_started:
    call(["vncserver",":1"])
    green = not green
    GPIO.output(GREEN, green)
    sleep(0.1)

GPIO.output(RED, 0)
GPIO.output(GREEN, 1)

# Leave Green light on
sleep(30)

# Exit
GPIO.cleanup()
