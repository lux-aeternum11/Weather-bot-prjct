from telegram import InlineKeyboardButton

# Основные кнопки для интерфейса
def weather_button(tr):
    return InlineKeyboardButton(tr['button_weather'], callback_data="weather")

def forecast_button(tr):
    return InlineKeyboardButton(tr['button_forecast'], callback_data="forecast")

def history_button(tr):
    return InlineKeyboardButton(tr['button_history'], callback_data="history")

def favorites_button(tr):
    return InlineKeyboardButton(tr['button_favorites'], callback_data="favorites")

def help_button(tr):
    return InlineKeyboardButton(tr['button_help'], callback_data="help")

# Кнопки действий
def add_favorite_button(tr, city):
    return InlineKeyboardButton(tr['button_add_fav'], callback_data=f"addfav_{city}")

def remove_favorite_button(tr, city):
    return InlineKeyboardButton(tr['button_remove_fav'], callback_data=f"removefav_{city}")

def city_weather_button(tr, city):
    return InlineKeyboardButton(f"🌤 {city}", callback_data=f"weather_{city}")

def forecast_for_city_button(tr, city):
    return InlineKeyboardButton(tr['button_forecast'], callback_data=f"forecast_{city}")

def clear_favorites_button(tr):
    return InlineKeyboardButton(tr['button_clear_favorites'], callback_data="clear_favorites")

# Кнопки выбора языка
def russian_language_button(tr):
    return InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")

def english_language_button(tr):
    return InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")