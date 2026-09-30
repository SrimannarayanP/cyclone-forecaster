# surge_inundation.py


import numpy as np

import os


def predict_surge(lat, lon, wind_kph, pressure_mb):
    from rasterio.features import shapes
    
    import rasterio
    
    dem_path = 'data/srtm_dem.tif'

    if not os.path.exists(dem_path): 
    
        return {'type': 'FeatureCollection', 'features': []}
    
    # Calculate deterministic surge height based on storm intensity inputs
    surge_height_m = (wind_kph*0.015) + ((1010 - pressure_mb)*0.05)
    
    with rasterio.open(dem_path) as src:
        elevation = src.read(1)
        transform = src.transform
        nodata = src.nodata
        
    if nodata is not None:
        mask = (elevation < surge_height_m) & (elevation != nodata)
    else:
        mask = (elevation < surge_height_m)
        
    mask_uint8 = mask.astype(np.uint8)

    features = []
    
    for geom, value in shapes(mask_uint8, mask = mask_uint8, transform = transform):
        if value == 1:
            features.append({'type': 'Feature', 'geometry': geom, 'properties': {'surge_height_m': round(surge_height_m, 2)}})
            
    return {'type': 'FeatureCollection', 'features': features}
