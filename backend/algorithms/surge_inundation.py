# surge_inundation.py


from rasterio.features import shapes

import numpy as np
import argparse, json, os, rasterio


def compute_surge_polygon(dem_path, surge_height_m):
    with rasterio.open(dem_path) as src:
        elevation = src.read(1)
        transform = src.transform
        crs = src.crs

    # Create a mask for pixels where elevation is < surge_height_m (and not nodata)
    # Assuming nodata is very negative or well above surge height
    nodata = src.nodata
    if nodata is not None:
        mask = (elevation < surge_height_m) & (elevation != nodata)
    else:
        mask = (elevation < surge_height_m)

    # Convert the boolean mask to uint8 for rasterio.features.shapes
    mask_uint8 = mask.astype(np.uint8)

    features = []
    # Generate shapes
    for geom, value in shapes(mask_uint8, mask = mask_uint8, transform = transform):
        if value == 1:
            features.append({'type': 'Feature', 'geometry': geom, 'properties': {'surge_height_m': surge_height_m}})

    return {'type': 'FeatureCollection', 'features': features}


parser = argparse.ArgumentParser(description = "Compute surge polygon from DEM")
parser.add_argument('--dem', default = '../data/srtm_dem.tif', help = "Path to DEM GeoTIFF")
parser.add_argument('--surge', type = float, default = 2.5, help = "Surge height in meters")
parser.add_argument('--out', default = '../data/surge_polygon.geojson', help = "Output GeoJSON path")
args = parser.parse_args()

if not os.path.exists(args.dem):
    print(f"Error: DEM file not found at {args.dem}")

    exit(1)

print(f"Processing DEM: {args.dem} with surge height: {args.surge}m")

feature_collection = compute_surge_polygon(args.dem, args.surge)

with open(args.out, 'w') as f:
    json.dump(feature_collection, f)

    print(f"Saved {len(feature_collection['features'])} features to {args.out}")
