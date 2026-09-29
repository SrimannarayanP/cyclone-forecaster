# fetch_infra.py


import json, os, requests


def fetch_infra(output_path):
    url = 'http://overpass-api.de/api/interpreter'

    headers = {'User-Agent': "CycloneForecasterHackathon/1.0 (pes.edu student project)", 'Accept': '*/*'}

    query = """
        [out:json][timeout:25];

        area["name" = "Puri"]["admin_level" = "5"]->.searchArea;

        (
            node["power"](area.searchArea);
            way["power"](area.searchArea);

            node["amenity"~"hospital|clinic"](area.searchArea);
            way["amenity"~"hospital|clinic"](area.searchArea);

            way["highway"~"primary|secondary|trunk"](area.searchArea);

            node["amenity"="shelter"](area.searchArea);
        );

        out center;
    """

    print("Executing Overpass query for Puri district...")

    res = requests.post(url, data = {'data': query}, headers = headers)

    if res.status_code != 200:
        print(f"API Err: Status {res.status_code}")

        return

    data = res.json()

    features = []

    for element in data.get('elements', []):
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')

        if not lat or not lon: continue

        tags = element.get('tags', {})
        
        asset_type = 'unknown'
        
        weight = 0.1

        if 'amenity' in tags and tags['amenity'] in ['hospital', 'clinic']:
            asset_type = 'healthcare'

            weight = 1.0
        elif 'amenity' in tags and tags['amenity'] == 'shelter':
            asset_type = 'shelter'

            weight = 0.9
        elif 'power' in tags:
            asset_type = 'power'

            weight = 0.9
        elif 'highway' in tags:
            asset_type = 'arterial_road'

            weight = 0.6

        feature = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {'id': element['id'], 'type': asset_type, 'name': tags.get('name', "Unnamed Asset"), 'criticality_weight': weight}
        }

        features.append(feature)

    feature_collection = {'type': 'FeatureCollection', 'features': features}

    os.makedirs(os.path.dirname(output_path), exist_ok = True)

    with open(output_path, 'w') as f:
        json.dump(feature_collection, f)

    print(f"Successfully saved {len(features)} infra assets to {output_path}")


fetch_infra('../data/puri_infra.geojson')
