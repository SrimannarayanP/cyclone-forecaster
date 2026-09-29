# d8_flow.py


from pysheds.grid import Grid
from rasterio.features import shapes
from shapely.geometry import shape

import geopandas as gpd
import numpy as np
import os, rasterio


def compute_flood_pathways(dem_path, output_path, accumulation_threshold = 1500):
    print(f"Loading DEM from {dem_path} into PySheds Grid...")

    if not os.path.exists(dem_path):
        raise FileNotFoundError(f"DEM file missing at {dem_path}")

    grid = Grid.from_raster(dem_path)
    dem = grid.read_raster(dem_path)

    print("Conditioning DEM: Filling pits & resolving flats...")
    
    pit_filled_dem = grid.fill_pits(dem)
    flooded_dem = grid.resolve_flats(pit_filled_dem)

    print("Calculating DB flow direction...")

    dirmap = (64, 128, 1, 2, 4, 8, 16, 32) # Std. directional mapping - N, NE, E, SE, S, SW, W, NW
    fdir = grid.flowdir(flooded_dem, dirmap = dirmap)

    print("Accumulating flow...")
    
    acc = grid.accumulation(fdir, dirmap = dirmap)

    print(f"Applying threshold (> {accumulation_threshold} upstream pixels)...")

    acc_array = np.asarray(acc)

    stream_mask = (acc_array > accumulation_threshold).astype(np.uint8) # Bin mask: 1 if it's a major flow pathway, 0 otherwise

    print("Vectorizing flood pathways into GeoJSON...")

    with rasterio.open(dem_path) as src:
        transform = src.transform
        crs = src.crs

    polygons = []

    for geom, val in shapes(stream_mask, mask = stream_mask.astype(bool), transform = transform):
        if (val == 1):
            polygons.append(shape(geom))

    if not polygons:
        print("Err: Threshold too high. No flood pathways detected.")

        return

    gdf = gpd.GeoDataFrame({'geometry': polygons}, crs = crs)
    gdf = gdf.to_crs(epsg = 4326)

    os.makedirs(os.path.dirname(output_path), exist_ok = True)

    gdf.to_file(output_path, driver = 'GeoJSON')

    print(f"Flood pathways saved to {output_path}.")


compute_flood_pathways('data/srtm_dem.tif', 'outputs/flood_pathways.geojson')
