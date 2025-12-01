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
    time.sleep(0.5)

print("Connected!")
print("IP Address:", wlan.ifconfig()[0])


# -------- SENSOR --------
i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=10000)
bme = BME280.BME280(i2c=i2c)


def safe_sensor_read():
    """Verhindert KeyError."""
    try:
        temp = bme.read_temperature() / 100
        hum = bme.read_humidity() / 1024
        pres = bme.read_pressure() / 25600
        return temp, hum, pres
    except Exception as e:
        print("Sensor Error:", e)
        return None, None, None


# -------- WEB SERVER --------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Webserver running...")
led_onboard = machine.Pin("LED", machine.Pin.OUT, value=1)

while True:
    cl, addr = s.accept()
    print("Client connected:", addr)

    try:
        request = cl.recv(1024)  # komplette Anfrage lesen
        if not request:
            cl.close()
            continue

        temp, hum, pres = safe_sensor_read()

        if temp is None:
            payload = '{"error":"sensor"}'
        else:
            payload = '{{"temperature": {:.2f}, "humidity": {:.2f}, "pressure": {:.2f}}}'.format(
                temp, hum, pres
            )

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Connection: close\r\n\r\n"
            + payload
        )

        cl.sendall(response)

    except Exception as e:
        print("Webserver error:", e)

    finally:
        cl.close()

