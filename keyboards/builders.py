from telegram import InlineKeyboardMarkup
from .inline import *


class KeyboardBuilder:
    @staticmethod
    def main_menu(tr):
        return InlineKeyboardMarkup([
            [weather_button(tr), forecast_button(tr)],
            [history_button(tr), favorites_button(tr)],
            [help_button(tr)]
        ])

    @staticmethod
    def weather_options(tr, city, is_favorite):
        buttons = [
            [forecast_for_city_button(tr, city)]
        ]
        if is_favorite:
            buttons.append([remove_favorite_button(tr, city)])
        else:
            buttons.append([add_favorite_button(tr, city)])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def history_list(tr, cities):
        return InlineKeyboardMarkup([
            [city_weather_button(tr, city)] for city in cities
        ])

    @staticmethod
    def favorites_list(tr, favorites):
        buttons = []
        for city in favorites:
            buttons.append([
                city_weather_button(tr, city),
                remove_favorite_button(tr, city)
            ])
        buttons.append([clear_favorites_button(tr)])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def language_selector(tr):
        return InlineKeyboardMarkup([
            [russian_language_button(tr)],
            [english_language_button(tr)]
        ])