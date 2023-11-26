from data import Data
import folium
import json
with open("../simulatedTraffic/10.json", "r") as json_file:
    data = json.load(json_file)

from folium.plugins import BeautifyIcon

people = []
routes = []

for i in data["people"]:
    people.append(Data(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

for i in range(len(data["daily_routes"][0])):
    for j in range(len(data["daily_routes"][0][i]["coords"])):
        people[i].fillArrays(data["daily_routes"][0][i]["coords"][j], data["daily_routes"][0][i]["times"][j], j)

for i in people[2].coords:
    print(i)


m = folium.Map(location=(52.27, 8.04))

iconn = folium.Icon(
    #prefix="fa",
    #icon="circle",
    number=10,
    #icon_color="#FF0000"
)

folium.Marker(
    location=[51.5, 8], icon=iconn, popup="Mt. Hood Meadows"
).add_to(m)

folium.Marker(
    location=[52, 8],
    tooltip="est",
    popup="sagf",
    icon=folium.Icon(color="darkgreen")
).add_to(m)

folium.Marker(
    location=[52.272, 8.044],
    icon=folium.Icon(
        prefix="fa",
        color="white",
        icon_color="FF0000",
        icon="house"
    ),
    tooltip="uoihoi"
).add_to(m)

folium.Marker(
    #0.00005 / 0.0001
    location=[52.27205, 8.0441],
    icon=folium.Icon(
        prefix="fa",
        color="white",
        icon_color="FF0000",
        icon="house"
    ),
    tooltip="uga-uga"
).add_to(m)

icon_number = folium.plugins.BeautifyIcon(
    border_color="#ff007f",
    color='white',
    border_width=12,
    inner_icon_style="opacity:0;",
)
folium.Marker([52, 8.55], tooltip='square', icon=icon_number).add_to(m)

icon2 = folium.plugins.BeautifyIcon(
    border_color="#ff007f",
    color='white',
    border_width=12,
    inner_icon_style="opacity:0;",
)
folium.Marker([52.1, 8.55], tooltip="Nummer<br> Zeit", icon = icon2).add_to(m)

folium.PolyLine(
    locations=[[52, 8.55], [52.1, 8.55]],
    color="#ff007f",
    weight=5,
).add_to(m)

m.save("test.html")