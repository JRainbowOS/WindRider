from flask import render_template, request
from app import app
from app.osm_api import get_road_ways_from_bbox, get_road_nodes_from_bbox
from app.osm_api2 import get_road_nodes_json_from_bbox, get_road_ways_json_from_bbox
from app.angle_match import calculate_way_geometry, get_angle_match
from app.osm2geojson import create_feature_collection


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/region/<region_name>')
def region(region_name):
    ANGLE = 50
    REGION_DICT = {'smeeth': (51.1040,0.9455,51.1206,0.9964),
                   'sellindge': (51.0862,0.9360,51.1188,1.0677)}
    bbox = REGION_DICT['smeeth']
    nodes = get_road_nodes_from_bbox(*REGION_DICT[region_name])
    ways = get_road_ways_from_bbox(*REGION_DICT[region_name])
    best_match = 0
    for way in ways:
        way_geometry = calculate_way_geometry(way, nodes)
        angle_match = get_angle_match(way_geometry, ANGLE)
        if angle_match > best_match:
            best_match = angle_match
    
    return render_template('region.html', region=region_name, best_match=best_match)


@app.route('/map')
def map_func():
    lat = request.args.get('lat', default=51.1, type=float)
    lon = request.args.get('lon', default=1, type=float)
    print(f'Lat: {lat} \t Lon: {lon}')
    return render_template('map.html', lat=lat, lon=lon, debug=True)   


@app.route('/data')
def map_data():
    # geojson = get_road_ways_json_from_bbox(51.1040,0.9455,51.1206,0.9964)
    nodes = get_road_nodes_from_bbox(51.1040,0.9455,51.1206,0.9964)
    ways = get_road_ways_from_bbox(51.1040,0.9455,51.1206,0.9964)
    geojson = create_feature_collection(ways, nodes)
    return geojson


@app.route('/map2')
def map_func2():
    lat = request.args.get('lat', default=51.1, type=float)
    lon = request.args.get('lon', default=1, type=float)
    print(f'Lat: {lat} \t Lon: {lon}')
    return render_template('map2.html', lat=lat, lon=lon, debug=True)   
