from datetime import datetime

import pytz
from Person import Person
import folium
import json
with open("10.json", "r") as json_file:
    data = json.load(json_file)
from folium.plugins import BeautifyIcon

def increaseLatitude():
    while True:
        i.coords[j][0] = i.coords[j][0] + 0.000008
        if not i.coords[j][0] in existingMarkers[0]:
            return

def increaseLongitude():
    while True:
        i.coords[j][1] = i.coords[j][1] + 0.00008
        if not i.coords[j][1] in existingMarkers[1]:
            return

def decreaseLatitude():
    while True:
        i.coords[j][0] = i.coords[j][0] - 0.000008
        if not i.coords[j][0] in existingMarkers[0]:
            return

def decreaseLongitude():
    while True:
        i.coords[j][1] = i.coords[j][1] - 0.00008
        if not i.coords[j][1] in existingMarkers[1]:
            return

def increaseOffset():
    if i.coords[j][0] in existingMarkers[0]:
        increaseLatitude()
    existingMarkers[0].append(i.coords[j][0])

    if i.coords[j][1] in existingMarkers[1]:
        increaseLongitude()
    existingMarkers[1].append(i.coords[j][1])

def decreaseOffset():
    if i.coords[j][0] in existingMarkers[0]:
        decreaseLatitude()
    existingMarkers[0].append(i.coords[j][0])

    if i.coords[j][1] in existingMarkers[1]:
        decreaseLongitude()
    existingMarkers[1].append(i.coords[j][1])

def calculateColor(howMany):
    #16777148 is FFFFBC is decimal, white is omitted
    return int(16777148 / howMany)

def millisecondsToCET(mill):
    utc_time = datetime.utcfromtimestamp(mill)
    utc_timezone = pytz.timezone("UTC")
    utc_aware_time = utc_timezone.localize(utc_time)
    cet_timezone = pytz.timezone("Europe/Berlin")
    cet_aware_time = utc_aware_time.astimezone(cet_timezone)
    return cet_aware_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def chooseIcon(index, person, max, _color):
    if _color == "0":
        _color = "ffffdd"
    if (index == person.indices[0]):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="house",
            inner_icon_style="oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif (index == max - 1):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="minus",
            inner_icon_style="oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif (index == 0):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="plus",
            inner_icon_style = "oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    else:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            inner_icon_style="opacity: 0"
        )

people = []
routes = []
#2 arrays for longitude and latitude
existingMarkers = [[],[]]
mySlice = slice(2, 8, 1)

#Personen Objekte anlegen und deren feste Orte zuweisen
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

colorBreadth = calculateColor(len(people))
color = 0

#Wegpunkte in obige Objekte einfügen und Indizes der festen Orte speichern
for i in range(len(data["daily_routes"][0])):
    for j in range(len(data["daily_routes"][0][i]["coords"])):
        people[i].fillArrays(data["daily_routes"][0][i]["coords"][j], data["daily_routes"][0][i]["times"][j], j)

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14
)

#true = plus; false = minus
offsetPlus = True
for i in people:
    coordinatesPolyLine = []
    for j in range(0, len(i.coords)):
        if offsetPlus:
            increaseOffset()
            offsetPlus = False
        else:
            decreaseOffset()
            offsetPlus = True

        coordinatesPolyLine.append([i.coords[j][0], i.coords[j][1]])
        chosenIcon = chooseIcon(j, i, len(i.coords), hex(color)[mySlice])

        folium.Marker(
            location=[i.coords[j][0], i.coords[j][1]],
            tooltip=str(j) + "<br>" + millisecondsToCET(i.times[j]),
            icon=chosenIcon
        ).add_to(m)

    #catch bug in first calculateColor call
    if i.id != 0:
        folium.PolyLine(
            locations=coordinatesPolyLine,
            color="#" + str(hex(color)[mySlice]),
            weight=5,
            opacity=0.7
        ).add_to(m)
    else:
        folium.PolyLine(
            locations=coordinatesPolyLine,
            color="#ffffdd",
            weight=5,
            opacity=0.8
        ).add_to(m)
    # increase color by colorBreath to guarantee distinguishable colors
    color = color + colorBreadth

m.save("marker.html")