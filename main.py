from datetime import datetime

import pytz
from person import Person
import folium
import json

with open("10.json", "r") as json_file:
    data = json.load(json_file)
from folium.plugins import BeautifyIcon


def increase(what):
    if what == "latitude":
        x = 0
    else:
        x = 1
    while True:
        i.coords[j][x] = i.coords[j][x] + 0.000009
        if not i.coords[j][x] in existingMarkers[x]:
            return


def decrease(what):
    if what == "latitude":
        x = 0
    else:
        x = 1
    while True:
        i.coords[j][x] = i.coords[j][x] - 0.000009
        if not i.coords[j][x] in existingMarkers[x]:
            return


def increase_offset():
    if i.coords[j][0] in existingMarkers[0]:
        increase("latitude")
    existingMarkers[0].append(i.coords[j][0])

    if i.coords[j][1] in existingMarkers[1]:
        increase("longitude")
    existingMarkers[1].append(i.coords[j][1])


def decrease_offset():
    if i.coords[j][0] in existingMarkers[0]:
        decrease("latitude")
    existingMarkers[0].append(i.coords[j][0])

    if i.coords[j][1] in existingMarkers[1]:
        decrease("longitude")
    existingMarkers[1].append(i.coords[j][1])


def calculate_color(how_many):
    # 16777148 is FFFFBC is decimal, white is omitted
    return int(16777148 / how_many)


def milliseconds_to_cet(mill):
    utc_time = datetime.utcfromtimestamp(mill)
    utc_timezone = pytz.timezone("UTC")
    utc_aware_time = utc_timezone.localize(utc_time)
    cet_timezone = pytz.timezone("Europe/Berlin")
    cet_aware_time = utc_aware_time.astimezone(cet_timezone)
    return cet_aware_time.strftime('%Y-%m-%d %H:%M:%S %Z')


def choose_icon(index, person, maximum, _color):
    if _color == "0":
        _color = "ffffdd"
    if index == person.indices[0]:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="house",
            inner_icon_style="oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif index == maximum - 1:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="minus",
            inner_icon_style="oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif index == 0:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="plus",
            inner_icon_style="oposition: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
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
# 2 arrays for longitude and latitude
existingMarkers = [[], []]
#cut off of "0x" from hex
mySlice = slice(2, 8, 1)

# initialize Person objects with coordinates and locations (home, work, free time)
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

color_breadth = calculate_color(len(people))
color = 0

# insert waypoints into upper objects and save indices of their locations (home, work, free time)
for i in range(len(data["daily_routes"][0])):
    for j in range(len(data["daily_routes"][0][i]["coords"])):
        people[i].fill_arrays(data["daily_routes"][0][i]["coords"][j], data["daily_routes"][0][i]["times"][j], j)

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14
)

#create and fill map

# true = plus; false = minus
offsetPlus = True
for i in people:
    coordinatesPolyLine = []
    for j in range(0, len(i.coords)):
        if offsetPlus:
            increase_offset()
            offsetPlus = False
        else:
            decrease_offset()
            offsetPlus = True

        coordinatesPolyLine.append([i.coords[j][0], i.coords[j][1]])
        chosenIcon = choose_icon(j, i, len(i.coords), hex(color)[mySlice])

        folium.Marker(
            location=[i.coords[j][0], i.coords[j][1]],
            tooltip=str(j) + "<br>" + milliseconds_to_cet(i.times[j]),
            icon=chosenIcon
        ).add_to(m)

    #catch bug that occurs at id 0
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
    color = color + color_breadth

m.save("marker.html")
