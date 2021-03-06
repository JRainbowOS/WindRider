import requests
from geojson import Feature, FeatureCollection
from shapely.geometry import LineString
from app.angle_match import calculate_bearing_match_of_linestring


WFS_ENDPOINT = "https://api.os.uk/features/v1/wfs"
KEY = 'vCGRsoADDTxbmamXfuvELPxlqVIv9nmN'

def create_bbox_string(lat_north, lon_west, lat_south, lon_east):
    return str(lat_north) + ',' + str(lon_west) + ',' + str(lat_south) + ',' + str(lon_east)


def get_open_roads_geojson_from_bbox(lat_north, lon_west, lat_south, lon_east,
                                     wfs_endpoint=WFS_ENDPOINT,
                                     key=KEY):
    bbox = create_bbox_string(lat_north, lon_west, lat_south, lon_east)
    all_features = []
    for product in ('Zoomstack_RoadsLocal',
                     'Zoomstack_RoadsRegional',
                     'Zoomstack_RoadsNational'):
    # for product in ['Zoomstack_RoadsNational']:
        print(f'Getting data from {product}...')
        data_remaining = True
        i = 0
        while data_remaining:
            print(i)
            start_index = i * 100
            wfs_params = {
                'key': key,
                'service': 'wfs',
                'version': '2.0.0',
                'startIndex': start_index,
                'request': 'GetFeature',
                'typeNames': product,
                'outputFormat': 'GeoJSON',
                'srsName': 'EPSG:4326',
                'bbox': bbox,
                'count': 100
            }
            response = requests.get(wfs_endpoint, params=wfs_params)
            payload = response.json()
            features = payload['features']
            data_remaining = len(features)
            all_features.extend(features)
            i += 1
            if i > 100:
                break
    feature_collection = FeatureCollection(all_features, crs="EPSG:4326")
    return feature_collection


def convert_payload_to_geojson(payload, target_bearing):
    features = payload['features']
    matched_features = []
    for f in features:
        coordinates = f['geometry']['coordinates'][0]
        linestring = LineString(coordinates)
        match = calculate_bearing_match_of_linestring(linestring, target_bearing)
        match_feature = Feature(geometry=LineString(coordinates), properties={'match': match,
                                                                              'color': f'rgba({255 * (1 - match)},\
                                                                                              {255 * match}, 0, 0.8)'})
        matched_features.append(match_feature)
    fc = FeatureCollection(matched_features, crs="EPSG:4326")    
    return fc


if __name__ == '__main__':
    bounds = [51.0162, 0.9160, 51.1388, 1.1877]
    target_bearing = 180
    payload = get_open_roads_geojson_from_bbox(*bounds)
    geojson = convert_payload_to_geojson(payload, target_bearing)
    print(geojson)