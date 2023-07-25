import json
import requests
from geopy import distance
from pprint import pprint
import folium


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
    return lon, lat


if __name__ == '__main__':
    with open('coffee.json') as f:
        bars_json = f.read()
    bars = json.loads(bars_json)
    bars_info = []
    yandex_api_key = '3dc190a5-d06f-4477-9f5a-e4790000109f'
    place = 'Красная площадь'
    place_coordinate = fetch_coordinates(apikey=yandex_api_key,address=place)
    for bar in bars:
        bar_latitude = bar['Latitude_WGS84']
        bar_longitude = bar['Longitude_WGS84']
        bar_coordinate = (
            bar_longitude,
            bar_latitude
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
    print('Ваши координаты: ', place_coordinate)
    top_bars = sorted(bars_info, key=lambda x: x['Расстояние'])[:5]
    pprint(top_bars,sort_dicts=False)
    m = folium.Map(
        location=place_coordinate[::-1],
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
