import adafruit_tca9548a
import urequests
import json
import machine
import network
import time

from display import BetterSSD1306_I2C, DisplayGroup
import apps
import font


display_group = None


def reset():
    if display_group:
        try:
            display_group.render_string('RESET', center=True, empty_as_transparent=False)
            display_group.show()
        except Exception:
            pass

    print("Resetting....")
    time.sleep(30)
    machine.reset()


# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    raise

WIDTH = 128
HEIGHT = 64

i2c = machine.SoftI2C(sda=machine.Pin(10), scl=machine.Pin(11))

tca = adafruit_tca9548a.TCA9548A(i2c)
display_group = DisplayGroup(
    [BetterSSD1306_I2C(WIDTH, HEIGHT, tca[i]) for i in range(5)])

display_group.render_string('wifi setup', center=True)
display_group.show()
time.sleep(1)

# Get configuration from a conf.py file
try:
    with open('conf.json', 'r') as f:
        conf = json.loads(f.read())
except OSError:
    # Backward compatibility
    try:
        from conf import conf
    except Exception as e:
        print(e)
        display_group.render_string('CONF ERROR')
        display_group.show()
        raise
except Exception as e:
    print(e)
    display_group.render_string('CONF ERROR')
    display_group.show()
    raise

connected = False

display_group.clear()
display_group.render_string('WIFI  INIT', center=True)
display_group.show()

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

while not connected:
    fail_count = 0
    for wifi_conf in secrets:
        try:
            print('Connecting to {}'.format(wifi_conf['ssid']))
            display_group.clear()
            display_group.render_string('{0} {1}'.format(font.CHAR_WIFI, wifi_conf['ssid'][:8]), center=False)
            display_group.show()
            time.sleep(1)
            import gc
            print(gc.mem_alloc())
            print(gc.mem_free())
            print(gc.collect())
            print(gc.isenabled())
            print(gc.mem_alloc())
            print(gc.mem_free())
            print(gc.isenabled())
            print(sta_if.scan())
            sta_if.connect(wifi_conf['ssid'], wifi_conf['password'])
            while not sta_if.isconnected():
                print("connecting to wifi...")
                time.sleep(1)
            display_group.clear()
            display_group.render_string('{0} '.format(font.CHAR_CHECK), center=True)
            display_group.show()
            connected = True
            break
        except Exception as e:
            fail_count += 1
            print(e)
            print('Connection to {} has failed. Trying next ssid...'.format(wifi_conf['ssid']))
            display_group.clear()
            display_group.render_string('{0} '.format(font.CHAR_CROSS), center=True)
            display_group.show()
            time.sleep(1)

    if fail_count == len(secrets):
        display_group.clear()
        display_group.render_string('no wifi!', center=True)
        display_group.show()
        time.sleep(2)
        display_group.clear()
        display_group.render_string('scanning..', center=True)
        display_group.show()
        time.sleep(2)

try:
    display_group.clear()
    display_group.render_string('TIME  INIT', center=True)
    display_group.show()
    # machine.RTC(RTC(requests_, pool))
except Exception as e:
    reset()

APPS = {
    'auto_contrast': apps.AutoContrastApp,
    'crypto': apps.CryptoApp,
    'time': apps.TimeApp,
    'blockheight': apps.BlockHeight,
    'halving': apps.Halving,
    'fees': apps.Fees,
    'text': apps.Text,
    'marketcap': apps.MarketCap,
    'moscow_time': apps.MoscowTime,
    'difficulty': apps.Difficulty,
    'temperature': apps.Temperature,
    'xpub': apps.Xpub,
    'test': apps.TestDisplay,
    'lnbits_wallet_balance': apps.LnbitsWalletBalance,
}


def main():
    apps = []

    # Initialize all apps
    display_group.clear()
    display_group.render_string('APPS  INIT', center=True)
    display_group.show()
    for app_conf in conf['apps']:
        name = app_conf.pop('name')
        print('Initializing {} app'.format(name))

        try:
            apps.append(APPS[name](display_group, **app_conf))
        except KeyError:
            raise ValueError('Unknown app {}'.format(name))
        except Exception as e:
            print('Initialization of application {} has failed'.format(APPS[name].__name__))
            print(e)

    # Run apps
    while True:
        for app in apps:
            try:
                print('Running {} app'.format(app.__class__.__name__))
                app.run()
            except Exception as e:
                print('Application {} has crashed'.format(app.__class__.__name__))
                print(e)
                reset()


if __name__ == '__main__':
    main()
