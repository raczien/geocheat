import os

import requests
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import json
from countryinfo import CountryInfo
import geopy.distance
from geographiclib.geodesic import Geodesic
import ctypes
from pywinauto import Application
from pywinauto.findwindows import ElementAmbiguousError


def degree_to_direction(deg):
    dir = ''
    if deg in range(0, 12) or deg in range(348, 360):
        dir = 'N'
    elif deg in range(13, 32):
        dir = 'NNE'
    elif deg in range(32, 55):
        dir = 'NE'
    elif deg in range(55, 79):
        dir = 'ENE'
    elif deg in range(79, 102):
        dir = 'E'
    elif deg in range(102, 125):
        dir = 'ESE'
    elif deg in range(125, 146):
        dir = 'SE'
    elif deg in range(146, 169):
        dir = 'SSE'
    elif deg in range(169, 191):
        dir = 'S'
    elif deg in range(191, 214):
        dir = 'SSW'
    elif deg in range(214, 236):
        dir = 'SW'
    elif deg in range(236, 259):
        dir = 'WSW'
    elif deg in range(259, 281):
        dir = 'W'
    elif deg in range(281, 303):
        dir = 'WNW'
    elif deg in range(303, 327):
        dir = 'NW'
    elif deg in range(327, 347):
        dir = 'NNW'
    return dir


def get_url():
    app = Application(backend='uia')
    try:
        app.connect(title_re=".*Opera.*")
    except ElementAmbiguousError:
        ctypes.windll.user32.MessageBoxW(0, 'Multiple Browsers open. Geoguessr top level in ONE browser needed.', "Geocheater", 1)
        exit(1)
    element_name = "Adressfeld"
    dlg = app.top_window()
    url = dlg.child_window(title=element_name, control_type="Edit").get_value()
    print(url)
    if 'geoguessr' not in url:
        ctypes.windll.user32.MessageBoxW(0, 'Window Geoguessr not found on Top Level.', "Geocheater", 1)
        exit(1)
    return url


def main():
    r = requests.get(get_url())
    soup = BeautifulSoup(r.text, 'html.parser')
    game = soup.find(id="__NEXT_DATA__")
    json_element = json.loads(str(game).split(">")[1].rsplit("<")[0])
    try:
        rounds = json_element["props"]["pageProps"]["game"]["rounds"]
    except KeyError:
        ctypes.windll.user32.MessageBoxW(0, 'Need to start a Game first.', "Geocheater", 1)
        exit(1)
    lat, lng = rounds[len(rounds)-1]["lat"], rounds[len(rounds)-1]["lng"]
    coord_string = "" + str(lat) + ", " + str(lng)
    geolocator = Nominatim(user_agent="coordinateconverter")
    location = geolocator.reverse(coord_string, language='en')
    country = location.raw['address']['country']
    try:
        capital = CountryInfo(country).capital()
    except KeyError:
        r = ctypes.windll.user32.MessageBoxW(0, str(location.raw['address']), "Geocheater", 4)
        if r == 6:
            main()
        else:
            exit(1)
    loc = geolocator.geocode(capital)
    km = geopy.distance.distance((loc.raw['lat'], loc.raw['lon']), (lat, lng)).km
    geod = Geodesic.WGS84
    g = geod.Inverse(float(loc.raw['lat']), float(loc.raw['lon']), float(lat), float(lng))
    deg = int(g['azi1'])
    if deg < 0:
        deg = 180 + deg
        deg += 180
    d = degree_to_direction(deg)
    prepared_json = str(location.raw['address']).replace("': '", "\": \"").replace("', '", "\", \"").replace("\", '", "\", \"").replace("': \"", "\": \"").replace("'}", "\"}").replace("{'", "{\"")
    j = json.loads(prepared_json)
    text = ''
    for key in j:
        value = j[key]
        if key != 'country_code' and key != 'postcode':
            temp = key.capitalize() + ': ' + value + '\n'
            text += temp

    text = text + '\nDirection: ' + str(int(km)) + ' km' + ' (' + d + ')' + ' from ' + capital
    text += '\nContinue?'
    result = ctypes.windll.user32.MessageBoxW(0, text, "Geocheater", 4)
    if result == 6:
        main()


if __name__ == '__main__':
    main()
