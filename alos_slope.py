import ee
from google.colab import auth

auth.authenticate_user()
ee.Initialize(project="evident-syntax-480714-p0")

import geemap

# ТВОИ НОВЫЕ КООРДИНАТЫ (маленький участок) - ОБНОВЛЕНЫ НА (longitude, latitude)
TEST_COORDS = [
    (58.60994, 52.24872),  # левый верхний (lon, lat)
    (58.68310, 52.24872),  # правый верхний (lon, lat)
    (58.68310, 52.20368),  # правый нижний (lon, lat)
    (58.60994, 52.20368),  # левый нижний (lon, lat)
]


# Функция с ФИКСОМ ОТОБРАЖЕНИЯ
def calculate_alos_slope(coords):
    polygon = ee.Geometry.Polygon([coords])

    # ИСПОЛЬЗУЕМ NASADEM, ТАК КАК ALOS НЕ ИМЕЕТ ДАННЫХ ДЛЯ ЭТОГО РЕГИОНА
    nasadem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")
    slope = ee.Terrain.slope(nasadem).clip(polygon)

    # СТАТИСТИКА
    stats = slope.reduceRegion(
        reducer=ee.Reducer.minMax().combine(ee.Reducer.mean(), "", True),
        geometry=polygon,
        scale=30,
        maxPixels=1e6,  # увеличено maxPixels
    )
    print("=== СТАТИСТИКА УКЛОНА (NASADEM) ===")
    print(stats.getInfo())

    # КАРТА С ЗУМОМ НА ПОЛИГОН
    m = geemap.Map()
    m.centerObject(polygon, 18)  # ✅ ЗУМ НА ТВОЙ УЧАСТОК
    m.addLayer(polygon, {"color": "red", "weight": 3}, "📍 Полигон")

    vis = {"min": 0, "max": 30, "palette": ["blue", "cyan", "lime", "yellow", "orange", "red"]}
    m.addLayer(slope, vis, "🎨 Уклон NASADEM 30м")

    # ✅ FIT BOUNDS
    m.fit_bounds(polygon.coordinates().getInfo()[0])

    return m