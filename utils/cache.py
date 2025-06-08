import json
import time
from weather_bot.config.settings import CACHE_FILE, CACHE_EXPIRATION

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_cached_weather(city, lang):
    cache = load_cache()
    city_key = f"{city.lower()}_{lang}"
    if city_key in cache:
        cached_data = cache[city_key]
        if time.time() - cached_data['timestamp'] < CACHE_EXPIRATION:
            return cached_data['data']
    return None

def set_cached_weather(city, lang, data):
    cache = load_cache()
    cache[f"{city.lower()}_{lang}"] = {
        'timestamp': time.time(),
        'data': data
    }
    save_cache(cache)