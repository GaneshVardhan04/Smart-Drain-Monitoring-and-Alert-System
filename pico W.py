import network
import urequests
import utime
from machine import Pin
from machine import time_pulse_us, ADC

WIFI_SSID = "YourWiFiName"
WIFI_PASS = "YourWiFiPassword"

THINGSPEAK_API_KEY = "YOUR_WRITE_API_KEY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

gas_sensor = ADC(26)   # GPIO26 = ADC0

buzzer = Pin(15, Pin.OUT)
led = Pin(14, Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        utime.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

def get_distance():
    TRIG.low()
    utime.sleep_us(2)
    TRIG.high()
    utime.sleep_us(10)
    TRIG.low()
    duration = time_pulse_us(ECHO, 1, 30000)
    distance = (duration * 0.0343) / 2
    return distance

def get_gas_ppm():
    adc_value = gas_sensor.read_u16()
    ppm = (adc_value / 65535) * 1000 
    return ppm

connect_wifi()
while True:
    distance = get_distance()
    gas_ppm = get_gas_ppm()

    print("Water Level Distance: ", distance, "cm")
    print("Gas Level: ", gas_ppm, "ppm")

    if distance < 10 or gas_ppm > 400:
        buzzer.value(1)
        led.value(1)
    else:
        buzzer.value(0)
        led.value(0)

    try:
        response = urequests.get(THINGSPEAK_URL + "&field1=" + str(distance) + "&field2=" + str(gas_ppm))
        print("ThingSpeak response:", response.text)
        response.close()
    except:
        print("Error sending to ThingSpeak")

    utime.sleep(15)  
