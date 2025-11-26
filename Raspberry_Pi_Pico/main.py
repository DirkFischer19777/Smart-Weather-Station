import network
import socket
from machine import Pin, I2C
from time import sleep
import BME280

# -------- WLAN CONNECT --------
ssid = "your ssid here"
password = "your WLAN password here"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to WiFi...")
while not wlan.isconnected():
    sleep(0.5)

print("Connected!")
print("IP Address:", wlan.ifconfig()[0])


# -------- SENSOR --------

# Initialize I2C communication
i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=10000)

# Initialize BME280 sensor
bme = BME280.BME280(i2c=i2c)

# -------- WEB SERVER --------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Webserver running...")

while True:
    cl, addr = s.accept()
    print("Client connected:", addr)

    # Read sensor data
    temp = bme.read_temperature() / 100
    hum = bme.read_humidity() / 1024
    pres = bme.read_pressure() / 25600

    # JSON response
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n\r\n"
        f'{{"temperature": {temp:.2f}, "humidity": {hum:.2f}, "pressure": {pres:.2f}}}'
    )

    cl.send(response)
    cl.close()

