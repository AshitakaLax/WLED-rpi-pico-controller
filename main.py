# This is controller board will offer 3 types of controls
# 1st an on off switch
# 2nd an mode button
# 3rd a potentiometer to control the dimmer.
# much of the functions here are taken from https://projects.raspberrypi.org/en/projects/introduction-to-the-pico/10
# for the WLED api I used https://kno.wled.ge/interfaces/http-api/
# For sending http request with micropython I used https://randomnerdtutorials.com/raspberry-pi-pico-w-http-requests-micropython/
# 1st On/Off switch pins 4(GP2)
# 2nd Button pin ?(GP13)
# 3rd 
# Pot pin 1 to 36(3v3), 
# Pot pin 2 to 31(GP26/ADC0),
# Pot pin 3 to 33(Gnd/AGND)

from picozero import Pot
from picozero import Button
from picozero import Switch
import urequests
import requests
import ntptime
import machine, network
import time
from time import sleep

dial = Pot(0)
on_off_switch = Switch(2)
mode_button = Button(13)
utc_offset_seconds = -6 * 3600
# Ellie wled_ip='172.16.0.133'
# Kate wled_ip='172.16.0.110'
# Tessa
wled_ip='172.16.0.141'
url = f"http://{wled_ip}/json/state"
headers = {'Content-type': 'application/json'}
#url = f'http://wled-ellie.local/win'
# Ellie List effect_list = [ 0, 2, 3 ]
# Kate List effect_list = [ 0, 2, 3 ]
# Tessa List
effect_list = [ 0, 90, 110, 2, 3 ]
effect_list = [ 0, 90, 110, 2, 3 ]

current_effect = 0
# http://wled-ellie.local/win&T=2
def ChangeMode():
    global current_effect
    current_effect = current_effect + 1
    if(current_effect >= len(effect_list)):
        current_effect = 0
    print('Changing to mode:', current_effect)
    effect_num = current_effect
    data = f'{{"seg": [{{"fx": {effect_num}}}]}}'
    response = urequests.post(url, headers=headers, data=data)
    response.close()
    requestErrorCheck(response)
    
def requestErrorCheck(response):
    response_code = response.status_code
    if(response_code != 200):
        print('ERROR')
        print('Response code: ', response_code)

def turn_off():
    # Turns off the WLED
    print('Turning off')
    brightness = get_brightness_dial_value()
    data = f'{{"on": false, "bri": {brightness}}}'
    response = urequests.post(url, headers=headers, data=data)
    response.close()
    requestErrorCheck(response)

def turn_on():
    print('Turning on')
    #check the time to determine whether this is allowed
    if(get_hour() > 20 or get_hour() < 5):
        return
    # Turns on the WLED lights
    brightness = get_brightness_dial_value()
    data = f'{{"on": true, "bri": {brightness}}}'
    response = urequests.post(url, headers=headers, data=data)
    response.close()
    requestErrorCheck(response)


def get_brightness_dial_value():
    # Gets a value from 0 to 1
    print('Current Brightness: ', (dial.value * 255))
    return dial.value * 255

def update_brightness(brightness, scale = 1):
    new_brightness = brightness * scale
    print("Updating brightness", new_brightness)
    data = f'{{"on": true, "bri": {int(new_brightness):d}}}'
    print('brightness data:', data)
    response = urequests.post(url, headers=headers, data=data)
    response.close()
    requestErrorCheck(response)

########### Time ############
local_time = 0
    
def set_pico_time():
    try:
        ntptime.settime()
        print("NTP time set successfully")
    except OSError as e:
        print(f"NTP time update failed: {e}")

    # Print current time in UTC
    print("Current time (UTC):", time.localtime())

    # Example of DST and timezone handling (example for UTC-5, adjust as needed)
    # You'll likely need a more robust solution for timezone handling in real applications
    # This is a simplified example for demonstration
    local_time = time.localtime(time.time() + utc_offset_seconds)
    print("Current time (UTC-6):", local_time)
    # Print the hour and minute
    hour = local_time[3]
    minute = local_time[4]
    #TODO: Setup the time
    print(f"Current local time: {hour:02d}:{minute:02d}")

def get_hour():
    local_time = time.localtime(time.time() + utc_offset_seconds)
    return local_time[3]

def get_minute():
    local_time = time.localtime(time.time() + utc_offset_seconds)
    return local_time[4]


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('bmesh', '@2ScreenSmiles19')
    while not wlan.isconnected():
        machine.idle()
print('network config:', wlan.ipconfig('addr4'))
print('current wlan status:', wlan.isconnected())

print('Starting WLED Controller')
#connect_to_bmesh()
print('Connected')

mode_button.when_pressed = ChangeMode
on_off_switch.when_closed = turn_on
on_off_switch.when_opened = turn_off

print('current wlan status:', wlan.status())
set_pico_time()
# used to check if there is a delta of x amount in order to change the brightness
last_pot_value = get_brightness_dial_value()

while True:
    sleep(4)
    #Check if on
    current_pot_value = get_brightness_dial_value()
    pot_delta = last_pot_value - current_pot_value
    #Check if the time is 8pm for dim, and 8:30pm to be off.
    # Start dim is at 5:30am, 6:00am
    # update this to be function call is_night()
    
    hour = get_hour()
    minute = get_minute()
    # check if it should be off
    if(hour > 20  or (hour == 20 and minute >= 30) or hour < 5 or (hour == 5 and minute < 30)):
        print('lights off time')
        # it should off
        #if(on_off_switch.is_closed):
        turn_off()
        continue
    # check whether it should be dim
    scale = 1
    if(hour == 20):
        print('should be getting dimmer')
        # it should be getting progressively dimmer.
        multiplier = 30 - minute
        scale = multiplier * 0.033
        update_brightness(current_pot_value, scale)
        
    if(hour == 5):
        #calculate
        # it should be getting progressively brighter
        # scale increments should be 0.033
        print('should be getting brighter')
        multiplier = minute - 30
        scale = multiplier * 0.033
        update_brightness(current_pot_value, scale)
    
    if(on_off_switch.is_closed):
        print('checking whether pot moved enough delta:', pot_delta)
        if(pot_delta > 13 or pot_delta < -13):
            
            update_brightness(current_pot_value)
            last_pot_value = current_pot_value
       
