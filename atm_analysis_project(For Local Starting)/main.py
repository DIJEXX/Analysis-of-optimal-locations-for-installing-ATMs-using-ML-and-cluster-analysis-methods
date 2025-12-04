# main.py
import os
import warnings
from src import config, data_loader, geometry_utils, analysis, visualizer

# Игнорируем предупреждения
warnings.filterwarnings('ignore')

def main():
    # 0. Подготовка папок
    if not os.path.exists('data'):
        os.makedirs('data')
    
    print("=== ЗАПУСК АНАЛИЗА ЛОКАЦИЙ БАНКОМАТОВ ===")

    # 1. Загрузка данных
    area_gdf, area_proj = data_loader.download_roi(config.PLACE_NAME)
    data_layers = data_loader.download_infrastructure(area_proj.geometry.iloc[0])
    
    # 2. Создание сетки и фичей
    grid_gdf = geometry_utils.generate_h3_grid(area_gdf)
    processed_df = geometry_utils.engineer_features(grid_gdf, data_layers)
    
    # 3. Кластеризация и Моделирование
    processed_df, X_scaled, feature_cols = analysis.run_clustering(processed_df)
    result_df, feat_imp = analysis.train_model(processed_df, X_scaled, feature_cols)
    
    if result_df is None:
        print("Остановка: модель не обучена.")
        return

    # 4. Выбор рекомендаций (там, где нет банкоматов)
    candidates = result_df[result_df['atm_target'] == 0].copy()
    top_20 = candidates.sort_values('potential_score', ascending=False).head(20)
    
    print(f"\n🏆 Топ-20 локаций (Средний скор: {top_20['potential_score'].mean():.3f})")
    
    # 5. Сохранение результатов
    csv_path = "data/recommendations.csv"
    top_20.drop(columns=['geometry']).to_csv(csv_path)
    print(f"💾 Таблица сохранена: {csv_path}")
    
    # 6. Визуализация
    visualizer.create_map(candidates, top_20, "data/map.html")
    
    print("\n=== ГОТОВО ===")

if __name__ == "__main__":
    main()