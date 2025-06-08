import os

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Настройки API
OPENWEATHER_API_KEY = "f5fdee069748d1599cb4d69d4d3a7f2c"
CACHE_EXPIRATION = 600
REQUEST_TIMEOUT = 7
ADMIN_IDS = [718117904]

# Пути к файлам
STORAGE_FILE = os.path.join(BASE_DIR, "storage", "user_data.json")
CACHE_FILE = os.path.join(BASE_DIR, "storage", "weather_cache.json")
LOCALES_DIR = os.path.join(BASE_DIR, "locales")