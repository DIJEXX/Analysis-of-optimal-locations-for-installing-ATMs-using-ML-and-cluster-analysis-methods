# src/visualizer.py
import leafmap.leafmap as leafmap
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os

def get_hex_color(score, cmap, norm):
    rgba = cmap(norm(score))
    return mcolors.to_hex(rgba)

def create_map(candidates_gdf, top_20_gdf, output_path="data/map.html"):
    """Создает интерактивную карту и сохраняет в HTML."""
    print(f"\n🗺️ Генерация карты: {output_path}")
    
    # Преобразование в WGS84 для карты
    candidates_wgs = candidates_gdf.to_crs("EPSG:4326")
    top_20_wgs = top_20_gdf.to_crs("EPSG:4326").copy()
    top_20_points = top_20_wgs.copy()
    top_20_points['geometry'] = top_20_points.geometry.centroid

    # Центр карты
    center_lat = top_20_points.geometry.y.mean()
    center_lon = top_20_points.geometry.x.mean()

    m = leafmap.Map(center=[center_lat, center_lon], zoom=13)

    # Цвета
    norm = mcolors.Normalize(vmin=candidates_wgs['potential_score'].min(), vmax=candidates_wgs['potential_score'].max())
    cmap = cm.get_cmap('plasma')

    # Слой 1: Гексагоны
    m.add_gdf(
        candidates_wgs,
        layer_name="Тепловая карта (Потенциал)",
        style_callback=lambda x: {
            "fillColor": get_hex_color(x['properties']['potential_score'], cmap, norm),
            "color": get_hex_color(x['properties']['potential_score'], cmap, norm),
            "weight": 1,
            "fillOpacity": 0.8 if x['properties']['potential_cat'] == 'High' else 0.2,
        },
        hover_style={"fillOpacity": 1.0, "weight": 2, "color": "white"}
    )

    # Слой 2: Топ точек
    m.add_gdf(
        top_20_points,
        layer_name="Топ-20 Рекомендаций",
        style={"color": "#00FFFF", "fillColor": "#00FFFF", "radius": 6, "fillOpacity": 1.0}
    )

    m.to_html(output_path)
    print("✅ Карта сохранена.")