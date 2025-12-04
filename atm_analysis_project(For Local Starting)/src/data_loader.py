# src/data_loader.py
import osmnx as ox
import geopandas as gpd
from .config import TARGET_CRS, OSM_TAGS

def download_roi(place_name):
    """Скачивает границы области интереса."""
    print(f"📥 Скачивание границ: {place_name}...")
    try:
        area = ox.geocode_to_gdf(place_name)
        area_proj = area.to_crs(TARGET_CRS)
        print(f"✅ Границы загружены. Площадь: {area_proj.area.iloc[0] / 1e6:.2f} км²")
        return area, area_proj
    except Exception as e:
        raise Exception(f"❌ Ошибка загрузки границ: {e}")

def download_infrastructure(roi_polygon):
    """Скачивает объекты инфраструктуры по тегам."""
    data_layers = {}
    print("\n📥 Загрузка объектов OSM (это может занять время)...")
    
    for layer_name, tag_dict in OSM_TAGS.items():
        try:
            gdf = ox.features_from_polygon(roi_polygon, tags=tag_dict)
            if not gdf.empty:
                # Оставляем только геометрию и проецируем
                gdf = gdf[['geometry']].to_crs(TARGET_CRS)
                # Преобразуем полигоны в точки (центроиды)
                gdf['geometry'] = gdf.geometry.centroid
                data_layers[layer_name] = gdf
                print(f"  - {layer_name}: {len(gdf)} объектов")
            else:
                print(f"  - {layer_name}: пусто")
                data_layers[layer_name] = None
        except Exception as e:
            print(f"  ⚠️ Ошибка загрузки {layer_name}: {e}")
            data_layers[layer_name] = None
            
    return data_layers