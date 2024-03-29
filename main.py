import network
import json
from time import sleep
import urequests
from picounicorn import PicoUnicorn
import sys
import secrets
from character_map import CHARACTERS

CONNECTED = False

previous_prices = []


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_NETWORK, secrets.WIFI_PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
        continue
    CONNECTED = True
    ip = wlan.ifconfig()[0]
    print("Connected on " + ip)
    return ip


def get_price():
    try:
        request = urequests.get("https://api.binance.com/api/v3/ticker/price?symbol=" + secrets.CRYPTO_PAIR)
        res = request.content
        request.close()
        data = json.loads(res)
        fl_val = float(data["price"])
        previous_prices.append(fl_val)
        if len(previous_prices) > 20:
            previous_prices.pop(0)
        return fl_val
    except Exception as e:
        print(e)
        sleep(10)
    return get_price()


def get_latest_rgb(current_price):
    """
    Returns the RGB values for the latest price
    """
    # Calculate average of previous prices
    avg = sum(previous_prices) / len(previous_prices)
    if current_price > avg:
        return [0, 255, 0]
    elif current_price < avg:
        return [255, 0, 0]
    return [255, 255, 255]


picounicorn = PicoUnicorn()
picounicorn.set_pixel(0, 0, 255, 255, 255)
sleep(2)
connect()

w = picounicorn.get_width()
h = picounicorn.get_height()


def clear_display():
    # Reset the display
    for x in range(w):
        for y in range(h):
            picounicorn.set_pixel(x, y, 0, 0, 0)


# Display a rainbow across Pico Unicorn

r = 255
g = 255
b = 255

clear_display()
counter = 0
while True:
    counter += 1
    fl_number = get_price()
    string_number = '%.2f' % fl_number
    rgb = get_latest_rgb(fl_number)

    offset = 0
    clear_display()
    for a_number in string_number:
        number_width = CHARACTERS[a_number]["width"]
        characters = CHARACTERS[a_number]["chars"]
        for char in characters:
            x_pos = (char[0] + offset)
            if x_pos > w - 1:
                continue
            picounicorn.set_pixel(x_pos, (char[1] + 1), rgb[0], rgb[1], rgb[2])
        offset += (number_width + 1)
    sleep(3)
