from datetime import datetime
import pytz
from jinja2 import Template

from person import Person
import folium
import json
with open("10.json", "r") as json_file:
    data = json.load(json_file)
from folium.plugins import BeautifyIcon
from folium.plugins import TimestampedGeoJson


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
    # else is longitude
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
        return decrease("latitude")

    if i.coords[j][1] in existingMarkers[1]:
        return decrease("longitude")


def set_offset():
    global offset_plus
    if offset_plus:
        increase_offset()
        offset_plus = False
    else:
        decrease_offset()
        offset_plus = True


def set_other_offset(coords, _times, _id):
    is_to_add = True
    for i in range(len(no_overlay)):
        if no_overlay[i][0] != coords:        # check if coordinates already exist
            is_to_add = True
            continue
        elif _id == no_overlay[i][2]:     # delete to offset same id waypoints
            continue
        else:                           # if coordinates exist in array
            if no_overlay[i][1] == _times:     # check if times of those coordinates match
                is_to_add = False
                continue                # if so continue to prevent double entry
            else:
                if 0 < no_overlay[i][1] - _times < 600:
                    #print(str(test[i][0]) + " " + str(coords) + " " + str(test[i][1] - times) +
                     #     " id: " + str(_id) + " id_ar: " + str(test[i][2]) + " timestampe_ar: " + str(test[i][1]))
                    #no_overlay.append([[coords[0]+0.008, coords[1]], _times, _id])
                    is_to_add = False
                    coords[0] = coords[0] + 0.0009
                    no_overlay.append([coords, _times, _id])

    if is_to_add:
        no_overlay.append([coords, _times, _id])

    if len(no_overlay) == 0:
        no_overlay.append([coords, _times, _id])


def calculate_color(how_many):
    # 16777148 is FFFFBC is decimal, white is omitted
    return int(16777148 / how_many)


def seconds_to_cet(seconds):
    utc_time = datetime.utcfromtimestamp(seconds)
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
            inner_icon_style="position: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif index == maximum - 1:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="minus",
            inner_icon_style="position: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
        )

    elif index == 0:
        return folium.plugins.BeautifyIcon(
            prefix="fa",
            border_color="#" + str(_color),
            border_width=12,
            icon="plus",
            inner_icon_style="position: absolute; top: 50%;left: 50%; transform: translate(-50%, -100%);"
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
existing_coords_times = []
# 2 arrays for longitude and latitude
existingMarkers = [[], []]
# cut off of "0x" from hex
mySlice = slice(2, 8, 1)

# initialize Person objects with coordinates and locations (home, work, free time)
for i in data["people"]:
    people.append(Person(i["id"], i["home_location"], i["workplace"], i["free_time_places"]))

color_breadth = calculate_color(len(people))
color = 0

# insert waypoints into upper objects and save indices of their locations (home, work, free time)
for id in range(len(data["daily_routes"][0])):
    for coord_or_according_time in range(len(data["daily_routes"][0][id]["coords"])):
        times = data["daily_routes"][0][id]["times"][coord_or_according_time]
        people[id].fill_arrays(data["daily_routes"][0][id]["coords"][coord_or_according_time], data["daily_routes"][0][id]["times"][coord_or_according_time], coord_or_according_time)
        existing_coords_times.append([data["daily_routes"][0][id]["coords"][coord_or_according_time],
                                      data["daily_routes"][0][id]["times"][coord_or_according_time], data["people"][id]["id"]])

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14,
    prefer_canvas=True
)
#set_other_offset(existing_coords_times[1][0])
# create and fill map

no_overlay = []
colors = []
opacity = 0.8
offset_plus = True

for i in range(0, len(people)):
    colors.append(color)
    color = color + color_breadth
    #set_offset()

js = Template(
    """
    L.circleMarker({
    radius: 3,
    fillOpacity: 1,
    "lineJoin": "square",
    })
    """
)

js_code = js.render()

for j in range(len(people)):
    for i in range(len(people[j].coords)):
        set_other_offset(data["daily_routes"][0][j]["coords"][i], data["daily_routes"][0][j]["times"][i], data["people"][j]["id"])


features = [
    {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[people[j].coords[i][1], people[j].coords[i][0]], [people[j].coords[i+1][1], people[j].coords[i+1][0]]],
        },
        "properties": {
            "id": str(people[j].id),
            "tooltip": str(data["people"][j]["id"]) + "<br>" + str(i+1) + "<br>" + str(seconds_to_cet(people[j].times[i])),
            "times": [seconds_to_cet(people[j].times[i])[:-4].replace(" ", "T"),
                      seconds_to_cet(people[j].times[i+1])[:-4].replace(" ", "T")],
            "style": {
                "color": "#" + str(hex(colors[j])[mySlice]) if people[j].id != 0 else "#000000",
                "weight": 5,
                "opacity": opacity,
            },
            "icon": "circle",  #icon.divIcon
            "iconstyle": {
                "fillColor": "#" + str(hex(colors[j])[mySlice]) if people[j].id != 0 else "#000000",
                "fillOpacity": opacity,
                "radius": 3,
                "line_join": "square",
                #"iconUrl": "house-solid.svg",
                #"js": js_code,
            },
        },
    }
    for j in range(len(people))
    for i in range(len(people[j].coords) - 1)
]

TimestampedGeoJson(
    {
        "type": "FeatureCollection",
        "features": features,
    },
    period="PT1M",
    add_last_point=True,
    duration="PT10M"
).add_to(m)

m.save("marker.html")
