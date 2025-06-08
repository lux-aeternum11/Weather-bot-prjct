
from telegram import Update
from telegram.ext import ContextTypes
from weather_bot.utils.logger import log
from weather_bot.utils.storage import (
    is_user_banned, add_favorite, remove_favorite,
    get_favorites, load_data, save_data
)
from weather_bot.utils.locale_utils import get_user_locale, set_user_language
from weather_bot.utils.formatters import format_weather
from weather_bot.services.api_client import get_weather_data
from weather_bot.services.forecast_service import send_forecast
from weather_bot.keyboards import KeyboardBuilder


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if is_user_banned(user_id):
        return

    data = query.data
    tr = get_user_locale(user_id)

    try:
        if data.startswith("weather_"):
            city = data.split("_", 1)[1]
            log(f"Пользователь {user_id} выбрал город: {city}")
            await handle_city_selection(query, city, user_id)

        elif data.startswith("forecast_"):
            city = data.split("_", 1)[1]
            log(f"Пользователь {user_id} запросил прогноз для {city}")
            await send_forecast(query, city, user_id)

        elif data.startswith("addfav_"):
            city = data.split("_", 1)[1]
            if add_favorite(user_id, city):
                log(f"Пользователь {user_id} добавил в избранное: {city}")
                await query.message.reply_text(tr['city_added_to_fav'].format(city=city))
            else:
                await query.message.reply_text(tr['city_already_in_fav'].format(city=city))

        elif data.startswith("removefav_"):
            city = data.split("_", 1)[1]
            if remove_favorite(user_id, city):
                log(f"Пользователь {user_id} удалил из избранного: {city}")
                await query.message.reply_text(tr['city_removed_from_fav'].format(city=city))
                # Обновляем сообщение с избранным
                await refresh_favorites(query, user_id)
            else:
                await query.message.reply_text(tr['city_not_in_fav'].format(city=city))

        elif data == "clear_favorites":
            storage = load_data()
            user_id_str = str(user_id)
            if user_id_str in storage["favorites"] and storage["favorites"][user_id_str]:
                storage["favorites"][user_id_str] = []
                save_data(storage)
                log(f"Пользователь {user_id} очистил избранное")
                await query.message.reply_text(tr['all_fav_removed'])
            else:
                await query.message.reply_text(tr['fav_already_empty'])

        elif data.startswith("lang_"):
            lang_code = data.split('_')[1]
            set_user_language(user_id, lang_code)
            tr = get_user_locale(user_id)  # Обновляем перевод
            await query.message.reply_text(tr['language_set'].format(language=tr[lang_code]))

        # Обработка основных команд через inline-кнопки
        elif data == "weather":
            await query.message.reply_text(tr['weather_prompt'])
        elif data == "forecast":
            await query.message.reply_text(tr['forecast_prompt'])
        elif data == "history":
            await show_history(query, user_id)
        elif data == "favorites":
            await show_favorites(query, user_id)
        elif data == "help":
            await query.message.reply_text(tr['help'])

    except Exception as e:
        log(f"Ошибка обработки callback: {str(e)}")
        await query.message.reply_text(tr['general_error'])


async def handle_city_selection(query, city, user_id):
    tr = get_user_locale(user_id)
    try:
        lang = tr['lang_code']
        weather_data = await get_weather_data(city, lang)
        response = format_weather(weather_data, tr)
        fav_list = get_favorites(user_id)
        is_favorite = city in fav_list

        await query.message.reply_text(
            response,
            reply_markup=KeyboardBuilder.weather_options(tr, city, is_favorite)
        )
    except Exception as e:
        error_key = str(e)
        await query.message.reply_text(tr.get(error_key, tr['weather_error']))


async def refresh_favorites(query, user_id):
    tr = get_user_locale(user_id)
    fav_list = get_favorites(user_id)

    if not fav_list:
        await query.message.reply_text(tr['favorites_empty'])
    else:
        await query.message.reply_text(
            tr['favorites_title'],
            reply_markup=KeyboardBuilder.favorites_list(tr, fav_list)
        )


async def show_history(query, user_id):
    tr = get_user_locale(user_id)
    history_list = get_history(user_id)

    if not history_list:
        await query.message.reply_text(tr['history_empty'])
    else:
        await query.message.reply_text(
            tr['history_title'],
            reply_markup=KeyboardBuilder.history_list(tr, history_list)
        )


async def show_favorites(query, user_id):
    tr = get_user_locale(user_id)
    fav_list = get_favorites(user_id)

    if not fav_list:
        await query.message.reply_text(tr['favorites_empty'])
    else:
        await query.message.reply_text(
            tr['favorites_title'],
            reply_markup=KeyboardBuilder.favorites_list(tr, fav_list)
        )