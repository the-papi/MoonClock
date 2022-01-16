import adafruit_requests
import adafruit_tca9548a
import board
import busio
import font
import microcontroller
import rtc
import socketpool
import ssl
import traceback
import time
import wifi

from datetime import RTC, datetime, tz, timedelta
from display import BetterSSD1306_I2C, DisplayGroup


display_group = None


def reset():
    if display_group:
        try:
            display_group.render_string('RESET', center=True, empty_as_transparent=False)
            display_group.show()
        except Exception:
            pass

    print("Resetting in 30 seconds...")
    time.sleep(30)
    print("Setting reset mode...")
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    print("Resetting...")
    microcontroller.reset()


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

WIDTH = 128
HEIGHT = 64

SDA = board.IO10
SCL = board.IO11

i2c = busio.I2C(SCL, SDA, frequency=1400000)

if i2c.try_lock():
    print('i2c.scan():' + str(i2c.scan()))
    i2c.unlock()

tca = adafruit_tca9548a.TCA9548A(i2c)
display_group = DisplayGroup(
    [BetterSSD1306_I2C(WIDTH, HEIGHT, tca[i]) for i in range(5)])

print('My MAC addr:', [hex(i) for i in wifi.radio.mac_address])

display_group.render_string('wifi setup', center=True)
display_group.show()

connected = False

while not connected:
    fail_count = 0
    for wifi_conf in secrets:
        try:
            print('Connecting to {}'.format(wifi_conf['ssid']))
            display_group.clear()
            display_group.render_string('{0} {1}'.format(font.CHAR_WIFI, wifi_conf['ssid'][:8]), center=False)
            display_group.show()
            wifi.radio.connect(wifi_conf['ssid'], wifi_conf['password'])
            print('Connected to {}!'.format(wifi_conf['ssid']))
            print('My IP address is', wifi.radio.ipv4_address)
            display_group.clear()
            display_group.render_string('{0} '.format(font.CHAR_CHECK), center=True)
            display_group.show()
            connected = True
            break
        except ConnectionError:
            fail_count += 1
            print('Connection to {} has failed. Trying next ssid...'.format(wifi_conf['ssid']))
            display_group.clear()
            display_group.render_string('{0} '.format(font.CHAR_CROSS), center=True)
            display_group.show()

    if fail_count == len(secrets):
        display_group.clear()
        display_group.render_string('no wifi!', center=True)
        display_group.show()
        display_group.clear()
        display_group.render_string('scanning..', center=True)
        display_group.show()

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

try:
    display_group.clear()
    display_group.render_string('TIME  INIT', center=True)
    display_group.show()
    rtc.set_time_source(RTC(requests))
except Exception as e:
    print(e)
    traceback.print_exception(type(e), e, e.__traceback__)
    reset()


def main():
    try:
        while True:
            print('A', time.monotonic())
            now = datetime.now(tz(requests, 'Europe/Prague'))
            print('B', time.monotonic())
            display_group.clear()
            print('C', time.monotonic())
            display_group.render_string('{}{} {}'.format(now.hour, font.CHAR_WIDECOLON, now.minute), center=True)
            print('D', time.monotonic())
            display_group.show()
            print('E', time.monotonic())
            time.sleep(10)
            print('F', time.monotonic())
    except Exception as e:
        print('G', time.monotonic())
        print(e, time.monotonic())
        traceback.print_exception(type(e), e, e.__traceback__)
        print('H', time.monotonic())
        reset()
        print('I', time.monotonic())


if __name__ == '__main__':
    main()
