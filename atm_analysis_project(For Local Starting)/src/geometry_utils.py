# src/geometry_utils.py
import h3
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
from .config import TARGET_CRS, H3_RESOLUTION, RADII_CONFIG

def generate_h3_grid(area_gdf):
    """Генерирует гексагональную сетку внутри границ."""
    print("cS Генерация сетки H3...")
    
    # Границы в WGS84 для H3
    area_wgs84 = area_gdf.to_crs("EPSG:4326")
    roi_poly = area_wgs84.geometry.iloc[0]
    minx, miny, maxx, maxy = roi_poly.bounds

    # Сканирование координат
    lat_steps = np.arange(miny, maxy, 0.0015)
    lon_steps = np.arange(minx, maxx, 0.0025)
    
    hex_ids = set()
    for lat in lat_steps:
        for lon in lon_steps:
            if roi_poly.contains(Point(lon, lat)):
                hex_ids.add(h3.latlng_to_cell(lat, lon, H3_RESOLUTION))

    print(f"✅ Создано гексагонов: {len(hex_ids)}")
    
    # Создание геометрии
    hex_polys = []
    valid_hex_ids = []
    for h in hex_ids:
        try:
            boundary = h3.cell_to_boundary(h)
            poly_coords = [(coord[1], coord[0]) for coord in boundary]
            hex_polys.append(Polygon(poly_coords))
            valid_hex_ids.append(h)
        except:
            continue
            
    grid_gdf = gpd.GeoDataFrame({'h3_index': valid_hex_ids}, geometry=hex_polys, crs="EPSG:4326")
    return grid_gdf.to_crs(TARGET_CRS)

def count_nearby(centroids_gdf, target_gdf, radius_meters):
    """Считает количество объектов в радиусе."""
    if target_gdf is None or target_gdf.empty:
        return pd.Series(0, index=centroids_gdf.index)

    buffers = centroids_gdf.geometry.buffer(radius_meters)
    buffers_gdf = gpd.GeoDataFrame(geometry=buffers, crs=TARGET_CRS)

    joined = gpd.sjoin(target_gdf, buffers_gdf, how='inner', predicate='intersects')
    return joined.index_right.value_counts().reindex(centroids_gdf.index, fill_value=0)

def engineer_features(grid_gdf, data_layers):
    """Создает признаки для каждого гексагона."""
    print("C$ Расчет признаков...")
    df = grid_gdf.copy()
    hex_centroids = df.copy()
    hex_centroids['geometry'] = hex_centroids.geometry.centroid

    # Целевая переменная (есть ли банкомат в радиусе 70м)
    atms_gdf = data_layers.get('atms')
    df['atm_target'] = 0
    if atms_gdf is not None:
        atm_counts = count_nearby(hex_centroids, atms_gdf, 70)
        df.loc[atm_counts > 0, 'atm_target'] = 1
        
        # Конкуренция (банкоматы в радиусе 300м)
        df['atm_competitors_300m'] = count_nearby(hex_centroids, atms_gdf, 300).values
    else:
        df['atm_competitors_300m'] = 0

    # Инфраструктура
    for cat, radii in RADII_CONFIG.items():
        if cat in data_layers and data_layers[cat] is not None:
            for r in radii:
                col_name = f'{cat}_{r}m'
                df[col_name] = count_nearby(hex_centroids, data_layers[cat], r).values
    
    return df