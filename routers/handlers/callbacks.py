from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from weather_bot.utils.logger import log
from weather_bot.utils.storage import is_user_banned, add_favorite, remove_favorite, get_favorites, load_data, save_data
from weather_bot.utils.locale_utils import get_user_locale, set_user_language
from weather_bot.utils.formatters import format_weather
from weather_bot.services.api_client import get_weather_data
from weather_bot.routers.commands import send_forecast
from weather_bot.services.forecast_service import send_forecast
from weather_bot.keyboards import KeyboardBuilder

async def handle_city_selection(query, city, user_id):
    tr = get_user_locale(user_id)
    try:
        lang = tr['lang_code']
        weather_data = await get_weather_data(city, lang)
        response = format_weather(weather_data, tr)
        fav_list = get_favorites(user_id)
        is_favorite = city in fav_list
        keyboard = [
            [InlineKeyboardButton(tr['button_forecast'], callback_data=f"forecast_{city}")]
        ]
        if is_favorite:
            keyboard.append([InlineKeyboardButton(tr['button_remove_fav'], callback_data=f"removefav_{city}")])
        else:
            keyboard.append([InlineKeyboardButton(tr['button_add_fav'], callback_data=f"addfav_{city}")])
        await query.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        error_key = str(e)
        await query.message.reply_text(tr.get(error_key, tr['weather_error']))

async def button_handler(update, context):
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
            await handle_city_selection(query, city, user_id)
        elif data.startswith("forecast_"):
            city = data.split("_", 1)[1]
            await send_forecast(query, city, user_id)
    except Exception as e:
        log(f"Ошибка обработки callback: {str(e)}")
        await query.message.reply_text(tr['general_error'])