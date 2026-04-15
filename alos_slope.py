import ee
import geemap
import folium
from typing import List, Tuple

# АВТОАВТОРИЗАЦИЯ ПРИ ПЕРВОМ ЗАПУСКЕ
# Запусти один раз: ee.Authenticate()
# КЛЮЧ НЕ НУЖЕН - авторизация через браузер

def calculate_alos_slope(
    coords: List[Tuple[float, float]],  # [(lon1,lat1), (lon2,lat2), (lon3,lat3), (lon4,lat4)]
    scale: int = 30
) -> folium.Map:
    """
    coords: 4 точки полигона по часовой от левого верхнего
    Возвращает: Folium карта с уклоном ALOS 30m
    """
    
    # Создаем полигон из 4 точек
    polygon = ee.Geometry.Polygon([coords])
    
    # ALOS World 3D 30m (DSM v4.1) - улучшенная точность
    dem = ee.Image('JAXA/ALOS/AW3D30/V4_1').select('DSM')
    
    # Вычисляем уклон (градусы, 0-90)
    slope = ee.Terrain.slope(dem).clip(polygon)
    
    # Статистика уклона
    stats = slope.reduceRegion(
        reducer=ee.Reducer.minMax().combine(ee.Reducer.mean().combine(ee.Reducer.stdDev())),
        geometry=polygon,
        scale=scale,
        maxPixels=1e6
    )
    
    print("Статистика уклона (градусы):")
    print(stats.getInfo())
    
    # Создаем карту Folium
    m = geemap.Map(center=[sum(lat for _,lat in coords)/4, sum(lon for lon,_ in coords)/4], zoom=12)
    
    # Визуализация уклона: синий=плоский (0°), красный=крутой (45°+)
    vis_params = {
        'min': 0,
        'max': 45,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    }
    
    # Добавляем слои
    m.add_layer(polygon, {'color': 'red'}, 'Твой полигон')
    map_layer = geemap.ee_tile_layer(slope, vis_params, 'Уклон ALOS 30m')
    m.add_layer(map_layer)
    
    # Легенда
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <b>Уклон (°)</b><br>
    <i style="background:linear-gradient(to right, #0000FF 0%, #00FFFF 25%, #FFFF00 50%, #FF8C00 75%, #FF0000 100%); width:100%; height:20px; display:block;"></i>
    <small>0°(плоский) → 45°(крутой)</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# ТЕСТОВЫЙ ЗАПУСК
if __name__ == "__main__":
    # Твои 4 координаты: левый верхний → по часовой → левый нижний
    TEST_COORDS = [ (52.23563, 58.65520),  # левый верхний
  (52.23563, 58.65667),  # правый верхний
  (52.23473, 58.65667),  # правый нижний
  (52.23473, 58.65520) ] # левый нижний
    
    # Инициализация Earth Engine (один раз)
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()
    
    # Запуск
    mapa = calculate_alos_slope(TEST_COORDS)
    mapa.save('alos_slope_map.html')
    mapa  # откроется в Jupyter или браузере
    print("Карта сохранена: alos_slope_map.html")