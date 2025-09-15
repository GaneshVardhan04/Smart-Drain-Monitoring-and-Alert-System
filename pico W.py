import network
import urequests
import utime
from machine import Pin, ADC

# ==== Blynk IoT credentials ====
BLYNK_AUTH = "4AEf1vxK3Y9a4OQWJbGyEMo6NleJ5BfH"
SSID = "VVIT Campus WIFI"
PASSWORD = "91357924680"

# ==== Pin Configuration ====
TRIG = Pin(2, Pin.OUT)
ECHO = Pin(3, Pin.IN)
gas_sensor = ADC(Pin(26))  # MQ sensor analog output

# ==== Connect to Wi-Fi ====
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...", end="")
while not wifi.isconnected():
    print(".", end="")
    utime.sleep(0.5)
print("\nConnected to WiFi:", wifi.ifconfig())

# ==== Function to read distance from HC-SR04 ====
def read_distance():
    TRIG.low()
    utime.sleep_us(2)
    TRIG.high()
    utime.sleep_us(10)
    TRIG.low()

    while ECHO.value() == 0:
        signal_off = utime.ticks_us()
    while ECHO.value() == 1:
        signal_on = utime.ticks_us()

    time_passed = signal_on - signal_off
    distance_cm = (time_passed * 0.0343) / 2
    return round(distance_cm, 2)

# ==== Main Loop ====
while True:
    try:
        # Read sensor values
        distance = read_distance()
        gas_raw = gas_sensor.read_u16()  # 0 - 65535
        gas_percent = (gas_raw / 65535) * 100  # Convert to percentage

        print("Distance:", distance, "cm | Gas:", gas_percent, "%")

        # Send data to Blynk (V0 = distance, V1 = gas %)
        url_data = "https://blynk.cloud/external/api/update?token={}&V0={}&V1={}".format(
            BLYNK_AUTH, distance, round(gas_percent, 2)
        )
        r = urequests.get(url_data)
        r.close()

        # Check alerts
        if distance < 10:
            alert_url = "https://blynk.cloud/external/api/notify?token={}&message={}".format(
                BLYNK_AUTH, "⚠ Alert: Object too close! Distance = {}cm".format(distance)
            )
            urequests.get(alert_url).close()

        if gas_percent > 80:
            alert_url = "https://blynk.cloud/external/api/notify?token={}&message={}".format(
                BLYNK_AUTH, "⚠ Alert: Gas level high! = {}%".format(round(gas_percent, 2))
            )
            urequests.get(alert_url).close()

    except Exception as e:
        print("Error:", e)

    utime.sleep(2)  # Update every 2 seconds
