from datetime import datetime

import pytz

from Person import Person
import folium
import json
with open("10.json", "r") as json_file:
    data = json.load(json_file)

from folium.plugins import BeautifyIcon

def millisecondsToCET(mill):
    utc_time = datetime.utcfromtimestamp(mill)
    utc_timezone = pytz.timezone("UTC")
    utc_aware_time = utc_timezone.localize(utc_time)
    cet_timezone = pytz.timezone("Europe/Berlin")
    cet_aware_time = utc_aware_time.astimezone(cet_timezone)
    return cet_aware_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def chooseIcon(index, person, max):
    if (index == person.indices[0]):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#00CED1",
            border_width=12,
            icon="house"
        )

    elif (index == max - 1):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#00CED1",
            border_width=12,
            icon="minus"
        )

    elif (index == 0):
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#00CED1",
            border_width=12,
            icon="plus"
        )

    else:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#00CED1",
            border_width=12,
            inner_icon_style="opacity: 0"
        )

people = []
routes = []

#Personen Objekte anlegen und deren feste Orte zuweisen
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

#Wegpunkte in obige Objekte einfügen und Indizes der festen Orte speichern
for i in range(len(data["daily_routes"][0])):
    for j in range(len(data["daily_routes"][0][i]["coords"])):
        people[i].fillArrays(data["daily_routes"][0][i]["coords"][j], data["daily_routes"][0][i]["times"][j], j)

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14
)

for i in people:
    coordinatesPolyLine = []

    for j in range(0, len(i.coords)):
        coordinatesPolyLine.append([i.coords[j][0], i.coords[j][1]])

        iconColor = chooseIcon(j, i, len(i.coords))

        folium.Marker(
            location=[i.coords[j][0], i.coords[j][1]],
            tooltip=str(j) + "<br>" + millisecondsToCET(i.times[j]),
            icon=iconColor
        ).add_to(m)

    folium.PolyLine(
        locations=coordinatesPolyLine,
        color="#00CED1",
        weight=5
    ).add_to(m)

m.save("marker.html")