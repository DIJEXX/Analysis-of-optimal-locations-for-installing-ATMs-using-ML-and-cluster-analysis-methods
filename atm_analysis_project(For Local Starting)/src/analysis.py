# src/analysis.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from kneed import KneeLocator

def run_clustering(df):
    """Кластеризация территорий."""
    print("\n🧩 Запуск кластеризации...")
    feature_cols = [c for c in df.columns if c not in ['h3_index', 'geometry', 'atm_target']]
    X = df[feature_cols].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Метод локтя (упрощенно для скрипта)
    wcss = []
    K_range = range(2, 11)
    for i in K_range:
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
        
    kl = KneeLocator(K_range, wcss, curve="convex", direction="decreasing")
    optimal_k = kl.elbow if kl.elbow else 4
    print(f"  Оптимальное количество кластеров: {optimal_k}")
    
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    return df, X_scaled, feature_cols

def train_model(df, X_scaled, feature_cols):
    """Обучение модели и расчет скора."""
    print("🧠 Обучение Random Forest...")
    y = df['atm_target']
    
    # Если банкоматов совсем нет, модель не обучится
    if y.sum() == 0:
        print("⚠️ Нет данных о существующих банкоматах для обучения.")
        return df, None

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_leaf=4, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    
    # Метрики
    y_test_pred = rf.predict(X_test)
    y_test_prob = rf.predict_proba(X_test)[:, 1]
    print(f"  Accuracy: {accuracy_score(y_test, y_test_pred):.4f}")
    print(f"  ROC AUC: {roc_auc_score(y_test, y_test_prob):.4f}")
    
    # Расчет потенциала для ВСЕХ зон
    df['prob_success'] = rf.predict_proba(X_scaled)[:, 1]
    
    # Фактор конкуренции (инвертированный)
    df['competition_factor'] = 1 / (np.log1p(df['atm_competitors_300m']) + 1)
    
    # Итоговый скор: 0.6 * Вероятность успеха + 0.4 * Низкая конкуренция
    df['potential_score'] = (0.6 * df['prob_success']) + (0.4 * df['competition_factor'])
    
    # Категории
    df['potential_cat'] = pd.qcut(df['potential_score'], q=[0, 0.5, 0.8, 1], labels=['Low', 'Medium', 'High'])
    
    # Важность признаков
    feat_imp = pd.DataFrame({'Feature': feature_cols, 'Importance': rf.feature_importances_})
    feat_imp = feat_imp.sort_values('Importance', ascending=False).head(10)
    print("\nTOP-5 Важных признаков:")
    print(feat_imp.head(5))
    
    return df, feat_imp