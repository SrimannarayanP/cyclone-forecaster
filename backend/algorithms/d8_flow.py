# d8_flow.py


from pysheds.grid import Grid
from rasterio.features import shapes
from shapely.geometry import shape

import geopandas as gpd
import numpy as np

import json, os, rasterio, warnings


def calculate_flow(lat, lon):
    warnings.filterwarnings('ignore')

    dem_path = 'data/srtm_dem.tif'
    
    if not os.path.exists(dem_path): 
    
        return {'type': 'FeatureCollection', 'features': []}
    
    grid = Grid.from_raster(dem_path)
    dem = grid.read_raster(dem_path)
    pit_filled_dem = grid.fill_pits(dem)
    flooded_dem = grid.resolve_flats(pit_filled_dem)
    
    dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    fdir = grid.flowdir(flooded_dem, dirmap = dirmap)
    acc = grid.accumulation(fdir, dirmap = dirmap)
    
    acc_array = np.asarray(acc)
    
    accumulation_threshold = 1500
    stream_mask = (acc_array > accumulation_threshold).astype(np.uint8)
    
    with rasterio.open(dem_path) as src:
        transform = src.transform
        crs = src.crs
        
    polygons = []

    for geom, val in shapes(stream_mask, mask = stream_mask.astype(bool), transform = transform):
        if val == 1:
            polygons.append(shape(geom))
            
    if not polygons:
    
        return {'type': 'FeatureCollection', 'features': []}
        
    gdf = gpd.GeoDataFrame({'geometry': polygons}, crs = crs)
    gdf = gdf.to_crs(epsg = 4326)

    return json.loads(gdf.to_json())
