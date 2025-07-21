# This is controller board will offer 3 types of controls
# 1st an on off switch
# 2nd an mode button
# 3rd a potentiometer to control the dimmer.
# much of the functions here are taken from https://projects.raspberrypi.org/en/projects/introduction-to-the-pico/10
# for the WLED api I used https://kno.wled.ge/interfaces/http-api/
# For sending http request with micropython I used https://randomnerdtutorials.com/raspberry-pi-pico-w-http-requests-micropython/
# 1st On/Off switch pins 4(GP2)
# 2nd Button pin 5(GP3)
# 3rd 
# Pot pin 1 to 36(3v3), 
# Pot pin 2 to 31(GP26/ADC0),
# Pot pin 3 to 33(Gnd/AGND)

from picozero import Pot
from picozero import Button
from picozero import Switch
import requests

dial = Pot(0)
on_off_switch = Switch(2)
mode_button = Button(3)


def ChangeMode():
    # Changes the LED mode
    # send the command to change the WLED mode
    connect_to_bmesh()
    # kick the watch dog

def toggle_on_off():
    # Get whether the WLED lights are on,
    # If on turn them off
    if(True):
        #  
    else:
        # 


def turn_off():
    # Turns off the WLED

def turn_on():
    # Turns on the WLED lights
    dimmer_value = dial.percent


def get_dimmer_value():
    # Gets a value from 0 to 1
    return dial.percent


def connect_to_bmesh():
    import machine, network
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('bmesh', 'key')
        while not wlan.isconnected():
            machine.idle()
    print('network config:', wlan.ipconfig('addr4'))