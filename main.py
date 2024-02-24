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


def increase(longitude_latitude, times, degree):
    if longitude_latitude == "latitude":
        x = 0
    # else is longitude
    else:
        x = 1
    is_present = True
    while is_present:
        no_match_found = 0
        for marker in no_overlay:
            existing_coords = marker[0]  # legt eigenen array nur für bereits existierende koordinaten an
            if existing_coords[x] == degree and marker[1] - times < 600:
                degree = degree + 0.000015
                break  # loop beenden um laufzeit zu verringern
            else:
                no_match_found = no_match_found + 1
            if no_match_found == len(no_overlay):
                is_present = False
                return degree


def decrease(longitude_latitude, times, degree):
    if longitude_latitude == "latitude":
        x = 0
    # else is longitude
    else:
        x = 1
    is_present = True
    while is_present:
        no_match_found = 0
        for marker in no_overlay:
            existing_coords = marker[0]  # legt eigenen array nur für bereits existierende koordinaten an
            if existing_coords[x] == degree and marker[1] - times < 600:
                degree = degree - 0.000015
                break  # loop beenden um laufzeit zu verringern
            else:
                no_match_found = no_match_found + 1
            if no_match_found == len(no_overlay):
                is_present = False
                return degree


def increase_offset(coords, times):
    coords[0] = decrease("latitude", times, coords[0])
    coords[1] = decrease("longitude", times, coords[1])
    return coords


def decrease_offset(coords, times):
    coords[0] = decrease("latitude", times, coords[0])
    coords[1] = decrease("longitude", times, coords[1])
    return coords


def set_offset(coords, times, id):
    global offset_plus
    if offset_plus:
        offset_plus = False
        coords = increase_offset(coords, times)
    else:
        offset_plus = True
        coords = decrease_offset(coords, times)
    no_overlay.append([coords, times, id])


def set_other_offset(coords, _times, _id):
    is_to_add = True
    for i in range(len(no_overlay)):
        if no_overlay[i][0] != coords:  # check if coordinates already exist
            is_to_add = True
            continue
        elif _id == no_overlay[i][2]:  # delete to offset same id waypoints
            continue
        else:  # if coordinates exist in array
            if no_overlay[i][1] == _times:  # check if times of those coordinates match
                is_to_add = False
                continue  # if so continue to prevent double entry
            else:
                if 0 < no_overlay[i][1] - _times < 600:
                    is_to_add = False
                    #coords[0] = coords[0] + 0.000015
                    #no_overlay.append([coords, _times, _id])
                    set_offset(coords, _times, id)

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
        people[id].fill_arrays(data["daily_routes"][0][id]["coords"][coord_or_according_time],
                               data["daily_routes"][0][id]["times"][coord_or_according_time], coord_or_according_time)
        existing_coords_times.append([data["daily_routes"][0][id]["coords"][coord_or_according_time],
                                      data["daily_routes"][0][id]["times"][coord_or_according_time],
                                      data["people"][id]["id"]])

m = folium.Map(
    location=(52.27, 8.04),
    zoom_start=14,
    prefer_canvas=True
)
# set_other_offset(existing_coords_times[1][0])
# create and fill map

no_overlay = []
colors = []
opacity = 0.8
offset_plus = True

for i in range(0, len(people)):
    colors.append(color)
    color = color + color_breadth
    # set_offset()

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
        set_other_offset(data["daily_routes"][0][j]["coords"][i], data["daily_routes"][0][j]["times"][i],
                         data["people"][j]["id"])

features1 = [
    {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[people[j].coords[i][1], people[j].coords[i][0]],
                            [people[j].coords[i + 1][1], people[j].coords[i + 1][0]]],
        },
        "properties": {
            "id": str(people[j].id),
            "tooltip": str(data["people"][j]["id"]) + "<br>" + str(i + 1) + "<br>" + str(
                seconds_to_cet(people[j].times[i])),
            "times": [seconds_to_cet(people[j].times[i])[:-4].replace(" ", "T"),
                      seconds_to_cet(people[j].times[i + 1])[:-4].replace(" ", "T")],
            "style": {
                "color": "#" + str(hex(colors[j])[mySlice]) if people[j].id != 0 else "#000000",
                "weight": 5,
                "opacity": opacity,
            },
            "icon": "circle",  # icon.divIcon
            "iconstyle": {
                "fillColor": "#" + str(hex(colors[j])[mySlice]) if people[j].id != 0 else "#000000",
                "fillOpacity": opacity,
                "radius": 3,
                "line_join": "square",
                # "iconUrl": "house-solid.svg",
                # "js": js_code,
            },
        },
    }
    for j in range(len(people))
    for i in range(len(people[j].coords) - 1)
]
# in features sind 3 einträge für coords
features = [
    {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [no_overlay[i][0][1], no_overlay[i][0][0]], [no_overlay[i + 1][0][1], no_overlay[i + 1][0][0]]
            ] if no_overlay[i][2] == no_overlay[i + 1][2] else [[no_overlay[i][0][1], no_overlay[i][0][0]],
                                                                [no_overlay[i][0][1], no_overlay[i][0][0]]],
        },
        "properties": {
            "id": str(no_overlay[i][2]),
            "tooltip": str(no_overlay[i][2]) + "<br>" + str(i + 1) + "<br>" + str(seconds_to_cet(no_overlay[i][1])),
            "times": [seconds_to_cet(no_overlay[i][1])[:-4].replace(" ", "T"),
                      seconds_to_cet(no_overlay[i + 1][1])[:-4].replace(" ", "T")],
                        #if no_overlay[i][2] == no_overlay[i + 1][2] else
                         #   [seconds_to_cet(no_overlay[i][1])[:-4].replace(" ", "T"),
                          #  seconds_to_cet(no_overlay[i][1])[:-4].replace(" ", "T")],
            "style": {
                "color": "#" + str(hex(colors[no_overlay[i][2]])[mySlice]) if no_overlay[i][2] != 0 else "#000000",
                "weight": 5,
                "opacity": opacity,
            },
            "icon": "circle",
            "iconstyle": {
                "fillColor": "#" + str(hex(colors[no_overlay[i][2]])[mySlice]) if people[j].id != 0 else "#000000",
                "fillOpacity": opacity,
                "radius": 3,
                "line_join": "square",
            },
        },
    }
    for i in range(len(no_overlay) - 1)
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
