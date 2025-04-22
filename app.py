import asyncio
import csv

import transliterate
from fuzzywuzzy import process
from geopy.distance import geodesic
from googletrans import Translator


def read_world_cities():
    data = []
    with open('worldcities.csv', 'r', encoding="UTF-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append({"city": row['city'], "admin_name": row['admin_name'], "lat": row['lat'], "lng": row['lng']})
    return data

def convert_cyrillic_to_latin(text):
    if transliterate.detect_language(text):
        return transliterate.translit(text, reversed=True)
    else:
        return text
    
async def translate_to_language(text, language = 'en'):
    translator = Translator()
    try:
        result = await translator.translate(text, dest=language)
        return result.text
    except Exception as e:
        print(f"Failed to translate {text}, {e}")
        return convert_cyrillic_to_latin(text)

def calculate_distance(lat1, lng1, lat2, lng2):
    result = geodesic((lat1, lng1), (lat2, lng2)).kilometers
    return int(result) if result > 1 else None

def find_closest_cities(base_city, cities, max_distance):
    list_of_cities = []
    for city in cities:
        distance = calculate_distance(base_city['lat'], base_city['lng'], city['lat'], city['lng'])
        if distance and distance <= max_distance:
            list_of_cities.append({"city_name": city['city'], 'distance_from_base': distance})
    return list_of_cities

def find_city(word, language):
    data = read_world_cities()
    best_match = process.extractOne(asyncio.run(translate_to_language(word, language)), [entry['admin_name'] for entry in data])[0]
    for entry in data:
        if best_match == entry['admin_name']:
            return entry, data
    return None

word = 'Букурещ'
language = 'ro'
distance = 20
base_city, data = find_city(word, language)
if base_city:
    print(f'Oraș introdus {word}')
    print(f'Oraș corectat {base_city['admin_name']}')
    result = find_closest_cities(base_city, data, distance)
    print(f"Orașe in raza de {distance} km:")
    for entry in result:
        print(f"- {entry["city_name"]} : {entry["distance_from_base"]} km")





