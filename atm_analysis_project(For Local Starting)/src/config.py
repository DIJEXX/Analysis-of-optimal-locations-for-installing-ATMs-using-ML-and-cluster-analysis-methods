# src/config.py

# Целевая проекция для Москвы (UTM zone 37N)
TARGET_CRS = "EPSG:32637"

# Область интереса
PLACE_NAME = "Central Administrative Okrug, Moscow, Russia"

# Параметры H3
H3_RESOLUTION = 9

# Теги для OSM
OSM_TAGS = {
    'atms': {'amenity': ['atm', 'bank']},
    'retail': {'shop': ['mall', 'supermarket', 'department_store', 'convenience', 'clothes', 'electronics']},
    'food': {'amenity': ['cafe', 'restaurant', 'fast_food', 'bar', 'pub']},
    'business': {'office': ['company', 'government', 'it', 'lawyer', 'coworking']},
    'transport': {'public_transport': ['stop_position', 'platform'], 'railway': 'subway_entrance', 'highway': 'bus_stop'},
    'residential': {'building': ['apartments', 'residential']}
}

# Радиусы для подсчета соседей (в метрах)
RADII_CONFIG = {
    'retail': [300],
    'food': [300],
    'business': [300],
    'transport': [300],
    'residential': [300, 500]
}