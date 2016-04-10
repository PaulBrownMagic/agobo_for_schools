#!/usr/bin/python
#
# Python Module to externalise all Agobo specific hardware
# 
#
#======================================================================


#======================================================================
# General Functions
#
# start(). Initialises GPIO pins, switches motors off, etc
# end(). Sets all motors off and sets GPIO to standard values
#======================================================================


#======================================================================
# Motor Functions
#
# stop(): Stops both motors
# forward(duration, speed): Sets both motors to move forward at speed. 0 <= speed <= 100
# backward(duration, speed): Sets both motors to reverse at speed. 0 <= speed <= 100
# left(duration, speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
# right(duration, speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
# turn_forward(duration, leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
# turn_backward(duration, leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
#======================================================================


#======================================================================
# IR Sensor Functions
#
# left_line(): Returns state of Left IR Line sensor
# right_line(): Returns state of Right IR Line sensor
#======================================================================


#======================================================================
# UltraSonic Functions
#
# get_distance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
#======================================================================


#======================================================================
# LED Functions
#
# setLED(led, val). Sets the White LED On (0) or Off (non-zero). LED 0 is Left, 1 is Right
# setAllLEDs(val). Sets both LEDs to same value
# pulse_lights(strip, colour). Pulses lights on a set colour.
# left_light(colour). Changes light to set colour
# right_light(colour). Changes light to set colour.
# both_lights(colour). Changes both lights to set colour.
#======================================================================


#======================================================================
# Button Functions
#
# get_button(). Returns True/False depending whether button is pressed or not
# wait_for_button(). Pauses program until button is pressed to continue
# button_interrupt(). Creates event handler in seperate thread to watch for button press.
#======================================================================


# Import all necessary libraries
import RPi.GPIO as GPIO, sys, threading, time, os
from leds import *

# Pins 24, 26 Left Motor
# Pins 19, 21 Right Motor
L1 = 26
L2 = 24
R1 = 19
R2 = 21

# Define obstacle sensors and line sensors
lineRight = 11
lineLeft = 7

# Define LED pins
leftLED = 15
rightLED = 13

# Define Tact Button Pin
button = 16

# Define Sonar Pin (same pin for both Ping and Echo)
# Note that this can be either 8 or 23 on PiRoCon
sonar = 23

# Define constants for ease of programing
TRUE = ON = WHITE = True
FALSE = OFF = BLACK = False
program_state = "waiting"

#Leds Setup
#strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
#strip.begin()

#Colours
#RED =    Color( 100,   0,   0)
#GREEN =  Color(   0, 100,   0)
#BLUE =   Color(   0,   0, 100)
#CYAN =   Color(   0, 100, 100)
#YELLOW = Color( 100, 100,   0)
#PURPLE = Color(  60,   0,  60)
#PINK =   Color( 100,  20,  40)
#ORANGE = Color( 100,  30,   0)

#======================================================================
# General Functions
#
# start(). Initialises GPIO pins, switches motors and LEDs Off, etc
def start():
    global p, q, a, b
    # Initialise the PWM device using the default address

    #use physical pin numbering
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    #set up digital line detectors as inputs
    GPIO.setup(lineRight, GPIO.IN) # Right line sensor
    GPIO.setup(lineLeft, GPIO.IN) # Left line sensor

    #set up white LEDs as outputs
    GPIO.setup(leftLED, GPIO.OUT)
    GPIO.setup(rightLED, GPIO.OUT)
    setAllLEDs(1)

    #set up tact button as input with pullup
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

    #use pwm on inputs so motors don't go too fast
    GPIO.setup(L1, GPIO.OUT)
    p = GPIO.PWM(L1, 20)
    p.start(0)

    GPIO.setup(L2, GPIO.OUT)
    q = GPIO.PWM(L2, 20)
    q.start(0)

    GPIO.setup(R1, GPIO.OUT)
    a = GPIO.PWM(R1, 20)
    a.start(0)

    GPIO.setup(R2, GPIO.OUT)
    b = GPIO.PWM(R2, 20)
    b.start(0)

    # Setup button interrupt and program_state.
    try:
        button_interrupt()
        global program_state
        print("Press MODE button to start")
        while program_state == "waiting":
            #pulse_lights(strip,Color(100, 100, 100))
            pass
        #strip.setBrightness(50)
        #left_light(RED)
        #right_light(GREEN)
        print("Running program. Press MODE button to end.\n...")
        time.sleep(0.5)
    except KeyboardInterrupt:
        end()
    except:
        end()
        start()



# end(). Sets all motors off and sets GPIO to standard values
def end():
    #colorWipe(strip, Color(0, 0, 0))
    stop()
    GPIO.cleanup()

def program_mode(channel):
    print("MODE button pressed")
    global program_state
    if program_state == "waiting":
        program_state = "running"
    elif program_state == "running":
        program_state = "ending"
        print("Ending program")
        end()

# Called in pupil's while loop to allow them to exit.
def running():
    global program_state
    if program_state != "ending":
        return True
    else:
        print("Program Ended")
        return False


# End of General Functions
#======================================================================


#======================================================================
# Motor Functions
#
# stop(): Stops both motors
def stop(duration=0):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(0)
    time.sleep(duration)
    
# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
def forward(duration, speed=100):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)
    time.sleep(duration)
    stop()
    
# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
def backward(duration, speed=100):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    q.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)
    time.sleep(duration)
    stop()

# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def left(duration, speed=100):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    q.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)
    time.sleep(duration)
    stop()
    
# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def right(duration, speed=100):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    p.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)
    time.sleep(duration)
    stop()
    
# turnForward(leftSpeed, rightSpeed): Moves forwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
def turn_forward(duration, leftSpeed=100, rightSpeed=100):
    p.ChangeDutyCycle(leftSpeed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(rightSpeed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(leftSpeed + 5)
    a.ChangeFrequency(rightSpeed + 5)
    time.sleep(duration)
    stop()
    
# turnReverse(leftSpeed, rightSpeed): Moves backwards in an arc by setting different speeds. 0 <= leftSpeed,rightSpeed <= 100
def turn_backward(duration, leftSpeed=100, rightSpeed=100):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(leftSpeed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(rightSpeed)
    q.ChangeFrequency(leftSpeed + 5)
    b.ChangeFrequency(rightSpeed + 5)
    time.sleep(duration)
    stop()

# End of Motor Functions
#======================================================================


#======================================================================
# IR Sensor Functions
#
# irLeftLine(): Returns state of Left IR Line sensor
def left_line():
    if GPIO.input(lineLeft)==0:
        return True
    else:
        return False
    
# irRightLine(): Returns state of Right IR Line sensor
def right_line():
    if GPIO.input(lineRight)==0:
        return True
    else:
        return False
    
# End of IR Sensor Functions
#======================================================================


#======================================================================
# NeoPixel Functions
#
# setLED(LED, value): Sets the LED specified to OFF == 0 or ON == 1
def setLED(LED, value):
    if LED == 0:
        GPIO.output (leftLED, value)
    else:
        GPIO.output (rightLED, value)
        
# setAllLEDs(value): Sets both LEDs to OFF == 0 or ON == 1
def setAllLEDs(value):
    GPIO.output (leftLED, value)
    GPIO.output (rightLED, value)
    
# Pulsing functionality
brightness = 20
direction_of_change = 1
def pulse_lights(strip, colour):
    global brightness
    global direction_of_change
    strip.setBrightness(brightness)
    colorWipe(strip, colour)
    if brightness > 160 or brightness < 15:
        direction_of_change *= -1
    brightness += (10*direction_of_change)

def left_light(colour):
    strip.setPixelColor(0,colour)
    strip.show()

def right_light(colour):
    strip.setPixelColor(1,colour)
    strip.show()

def both_lights(colour):
    strip.setPixelColor(0,colour)
    strip.setPixelColor(1,colour)
    strip.show()

def light_brightness(num):
    strip.setBrightness(num)
    strip.show()
    
# End of White LED Functions
#======================================================================


#======================================================================
# Switch Functions
# 
# get_button(). Returns the value of the tact switch: True==pressed
def get_button():
    val = GPIO.input(button)
    return (val == 0)

# button_interrupt. Sets button to interrupt the running program. Calls end().
def button_interrupt():
    GPIO.add_event_detect(button, GPIO.FALLING, callback=program_mode, bouncetime=500)
#
# End of switch functions
#======================================================================


#======================================================================
# UltraSonic Functions
#
# get_distance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
def get_distance():
    GPIO.setup(sonar, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(sonar, True)
    time.sleep(0.00001)
    GPIO.output(sonar, False)
    start = time.time()
    count=time.time()
    GPIO.setup(sonar,GPIO.IN)
    while GPIO.input(sonar)==0 and time.time()-count<0.1:
        start = time.time()
    count=time.time()
    stop=count
    while GPIO.input(sonar)==1 and time.time()-count<0.1:
        stop = time.time()
    # Calculate pulse length
    elapsed = stop-start
    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000
    # That was the distance there and back so halve the value
    distance = distance / 2
    return distance

# End of UltraSonic Functions    
#======================================================================

if __name__ != '__main__':
    start()
    
