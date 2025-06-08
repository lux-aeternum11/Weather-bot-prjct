import json
import os
from weather_bot.config.settings import LOCALES_DIR
from weather_bot.utils.storage import load_data, save_data

def load_locale(lang: str) -> dict:
    file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return load_locale("ru")
    except Exception:
        return {}

def get_user_locale(user_id: int) -> dict:
    user_id = str(user_id)
    storage = load_data()
    default_lang = "ru"
    if "settings" in storage and user_id in storage["settings"]:
        user_lang = storage["settings"][user_id].get("lang", default_lang)
        return load_locale(user_lang)
    return load_locale(default_lang)

def set_user_language(user_id: int, lang: str):
    user_id = str(user_id)
    storage = load_data()
    if "settings" not in storage:
        storage["settings"] = {}
    if user_id not in storage["settings"]:
        storage["settings"][user_id] = {}
    storage["settings"][user_id]["lang"] = lang
    save_data(storage)