from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
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
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *


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


def create_map(dir, data, lat, lon):
    root = Tk()
    root.wm_title("Geocheat")

    fig = plt.figure(figsize=(8, 6))
    m = Basemap(projection='mill', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
    m.drawcoastlines()
    m.scatter(lon, lat, latlon=True, s=60, c='red', marker="o", alpha=1, edgecolor='k', linewidth=1, zorder=2)
    plt.title(dir, fontsize=10)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    container = Frame(master=root)
    container.pack(side='top', padx='5', pady='5')

    def _quit():
        root.quit()
        root.destroy()
        exit(1)

    def _continue():
        root.quit()
        root.destroy()
        cheatycheat()

    Label(master=root, text=data, font=('Helvatical bold', 12)).pack()
    yes_button = tkinter.Button(master=container, text="QUIT", height=4, width=10, command=_quit)
    yes_button.config(font=('Helvatical bold', 12))
    yes_button.pack(side=LEFT)
    no_button = tkinter.Button(master=container, text="CONTINUE", height=4, width=10, command=_continue)
    no_button.config(font=('Helvatical bold', 12))
    no_button.pack(side=LEFT)

    def on_closing():
        exit(1)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    tkinter.mainloop()


def get_url():
    app = Application(backend='uia')
    try:
        app.connect(title_re=".*Opera.*")
    except ElementAmbiguousError:
        ctypes.windll.user32.MessageBoxW(0, 'Multiple Browsers open. Geoguessr top level in ONE browser needed.',
                                         "Geocheater", 1)
        exit(1)
    element_name = "Adressfeld"
    dlg = app.top_window()
    url = dlg.child_window(title=element_name, control_type="Edit").get_value()
    # print(url)
    if 'geoguessr' not in url:
        ctypes.windll.user32.MessageBoxW(0, 'Window Geoguessr not found on Top Level.', "Geocheater", 1)
        exit(1)
    return url


def cheatycheat():
    r = requests.get(get_url())
    soup = BeautifulSoup(r.text, 'html.parser')
    game = soup.find(id="__NEXT_DATA__")
    json_element = json.loads(str(game).split(">")[1].rsplit("<")[0])
    try:
        rounds = json_element["props"]["pageProps"]["game"]["rounds"]
    except KeyError:
        ctypes.windll.user32.MessageBoxW(0, 'Need to start a Game first.', "Geocheater", 1)
        exit(1)
    lat, lng = rounds[len(rounds) - 1]["lat"], rounds[len(rounds) - 1]["lng"]
    coord_string = "" + str(lat) + ", " + str(lng)
    geolocator = Nominatim(user_agent="coordinateconverter")
    location = geolocator.reverse(coord_string, language='en')
    country = location.raw['address']['country']
    if country == 'Palestinian Territories':
        country = 'Israel'
    try:
        capital = CountryInfo(country).capital()
    except KeyError:
        r = ctypes.windll.user32.MessageBoxW(0, str(location.raw['address']), "Geocheater", 4)
        create_map(str(location.raw['address']), lat, lng)
        if r == 6:
            cheatycheat()
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
    prepared_json = str(location.raw['address']).replace("': '", "\": \"").replace("', '", "\", \"").replace("\", '",
                                                                                                             "\", \"").replace(
        "': \"", "\": \"").replace("'}", "\"}").replace("{'", "{\"")
    j = json.loads(prepared_json)
    text = ''
    counter = 0
    for key in reversed(list(j.keys())):
        value = j[key]
        if key != 'country_code' and key != 'postcode':
            temp = key.upper() + ': ' + value
            if counter % 2 != 0:
                temp += '\n'
            else:
                temp += ',   '
            text += temp
            counter += 1

    # text = text + 'Direction: ' + str(int(km)) + ' km' + ' (' + d + ')' + ' from ' + capital
    direction = 'Direction: ' + str(int(km)) + ' km' + ' (' + d + ')' + ' from ' + capital
    create_map(direction, text, lat, lng)


if __name__ == '__main__':
    cheatycheat()
