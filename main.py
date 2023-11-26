from Person import Person
import folium
import json
with open("10.json", "r") as json_file:
    data = json.load(json_file)

from folium.plugins import BeautifyIcon

people = []
routes = []

#Personen Objekte anlegen und deren feste Orte zuweisen
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

#Wegpunkte in obige Objekte einfügen und Indizes der festen Orte speichern
for i in range(len(data["daily_routes"][0])):
    for j in range(len(data["daily_routes"][0][i]["coords"])):
        people[i].fillArrays(data["daily_routes"][0][i]["coords"][j], data["daily_routes"][0][i]["times"][j], j)

m = folium.Map(location=(52.27, 8.04))

for i in people:
    coordinatesPolyLine =[[]]

    for j in range(0, len(i.coords)):
        coordinatesPolyLine[0].append([i.coords[j][0], i.coords[j][1]])
        folium.Marker(
            location=[i.coords[j][0], i.coords[j][1]]
        ).add_to(m)

    folium.PolyLine(
        locations=coordinatesPolyLine,
        color="#FF0000",
        weight=5
    ).add_to(m)

m.save("marker.html")