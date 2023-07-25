import json
import requests
from geopy import distance
import folium
from flask import Flask
from dotenv import load_dotenv
import os


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def read_json_file(json_file):
    with open(json_file) as f:
        bars_json = f.read()
    bars = json.loads(bars_json)
    return bars


def get_top_bars_info(bars, my_coordinates):
    bars_info = []
    place_coordinate = my_coordinates
    for bar in bars:
        bar_latitude = bar['Latitude_WGS84']
        bar_longitude = bar['Longitude_WGS84']
        bar_coordinate = (
            bar_latitude,
            bar_longitude
        )
        bar_name = bar['Name']
        distance_to_bar = distance.distance(
            bar_coordinate,
            place_coordinate
        ).km

        bars_info.append(
            {
                'Название кофейни': bar_name,
                'Расстояние': distance_to_bar,
                'Широта': bar_latitude,
                'Долгота': bar_longitude
            }
        )
    return sorted(bars_info, key=lambda x: x['Расстояние'])[:5]


def main():
    load_dotenv()
    bars_info = read_json_file('coffee.json')
    yandex_api_key = os.getenv('YANDEX_API_KEY')
    my_place = input('Введите город: ')
    my_coordinates = fetch_coordinates(yandex_api_key, my_place)
    top_bars = get_top_bars_info(bars_info, my_coordinates)
    m = folium.Map(
        location=my_coordinates,
        zoom_start=12,
        tiles="Stamen Terrain")
    tooltip = "Click me!"
    for bar in top_bars:
        folium.Marker(
            [bar['Широта'], bar['Долгота']],
            popup=f"<i>{bar['Название кофейни']}</i>",
            tooltip=tooltip
        ).add_to(m)
    m.save("index.html")
    with open('index.html', 'rb') as file:
        return file.read()


if __name__ == '__main__':
    app = Flask(__name__)
    app.add_url_rule('/', 'map', main)
    app.run('0.0.0.0')
