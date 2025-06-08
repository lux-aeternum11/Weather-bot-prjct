import os
import json
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from weather_bot.utils.logger import setup_logger, log
from config import settings
from routers import commands
from routers.handlers import callbacks
from keyboards import handle_callback


def create_locale_files():
    """Создает файлы локализаций, если они отсутствуют"""
    locales = {
        "ru.json": {
            "lang_code": "ru",
            "ru": "русский",
            "en": "английский",
            "start": "Привет, {name}! Я Погодный Помощник 🌤\nУзнай погоду в любом городе мира!\n\nНовые возможности:\n- Сохраняй города в Избранное ★\n- Просматривай историю запросов",
            "help": "📚 Доступные команды:\n/start - Начать работу\n/weather [город] - Текущая погода\n/forecast [город] - Прогноз на 5 дней\n/history - История запросов\n/favorites - Управление избранными городами\n/add_fav [город] - Добавить в избранное\n/remove_fav [город] - Удалить из избранного\n/language - Сменить язык\n/help - Справка\n\nПримеры:\n/weather Москва\n/add_fav Париж\n/forecast Лондон",
            "weather_city_missing": "Пожалуйста, укажите город:\n/weather Москва",
            "forecast_city_missing": "Пожалуйста, укажите город:\n/forecast Санкт-Петербург",
            "history_empty": "История запросов пуста.",
            "favorites_empty": "У вас пока нет избранных городов.\nДобавьте их командой /add_fav [город] или через кнопку в прогнозе погоды.",
            "city_added_to_fav": "★ Город '{city}' добавлен в избранное!",
            "city_already_in_fav": "⚠️ Город '{city}' уже есть в вашем избранном",
            "city_removed_from_fav": "🗑️ Город '{city}' удален из избранного!",
            "city_not_in_fav": "⚠️ Город '{city}' не найден в вашем избранном",
            "all_fav_removed": "★ Все города удалены из избранного!",
            "fav_already_empty": "⚠️ В вашем избранном и так пусто",
            "timeout": "⏳ Сервер погоды не отвежает. Попробуйте позже.",
            "connection_error": "⚠️ Проблемы с подключением к сервису погоды.",
            "weather_error": "❌ Не удалось получить данные о погоде.",
            "forecast_timeout": "⏳ Превышено время ожидания прогноза",
            "forecast_network_error": "⚠️ Ошибка сети: {error}",
            "forecast_error": "❌ Ошибка прогноза: {error}",
            "choose_language": "Выберите язык:",
            "language_set": "✅ Язык изменен на {language}.",
            "weather_format": "🌆 Город: {city}\n🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n📛 Влажность: {humidity}%\n💨 Ветер: {wind} м/с\n🌈 Погода: {description}",
            "forecast_title": "📅 Прогноз на 5 дней для {city}:\n\n",
            "forecast_item": "📅 {date}: {desc}, {temp}°C\n",
            "history_title": "🕐 История ваших запросов:",
            "favorites_title": "★ Ваши избранные города:",
            "button_weather": "/weather",
            "button_forecast": "/forecast",
            "button_history": "/history",
            "button_favorites": "/favorites",
            "button_help": "/help",
            "button_forecast": "Прогноз на 5 дней",
            "button_add_fav": "★ Добавить в избранное",
            "button_remove_fav": "★ Удалить из избранного",
            "button_clear_favorites": "🗑️ Очистить все избранное",
            "general_error": "⚠️ Произошла ошибка при обработке запроса"
        },
        "en.json": {
            "lang_code": "en",
            "ru": "Russian",
            "en": "English",
            "start": "Hello, {name}! I'm Weather Assistant 🌤\nGet weather in any city of the world!\n\nNew features:\n- Save cities to Favorites ★\n- View request history",
            "help": "📚 Available commands:\n/start - Start the bot\n/weather [city] - Current weather\n/forecast [city] - 5-day forecast\n/history - Request history\n/favorites - Manage favorite cities\n/add_fav [city] - Add to favorites\n/remove_fav [city] - Remove from favorites\n/language - Change language\n/help - Help\n\nExamples:\n/weather Moscow\n/add_fav Paris\n/forecast London",
            "weather_city_missing": "Please specify a city:\n/weather Moscow",
            "forecast_city_missing": "Please specify a city:\n/forecast London",
            "history_empty": "History is empty.",
            "favorites_empty": "You don't have any favorite cities yet.\nAdd them with /add_fav [city] or via button in weather forecast.",
            "city_added_to_fav": "★ City '{city}' added to favorites!",
            "city_already_in_fav": "⚠️ City '{city}' is already in your favorites",
            "city_removed_from_fav": "🗑️ City '{city}' removed from favorites!",
            "city_not_in_fav": "⚠️ City '{city}' not found in your favorites",
            "all_fav_removed": "★ All cities removed from favorites!",
            "fav_already_empty": "⚠️ Your favorites are already empty",
            "timeout": "⏳ Weather server is not responding. Try again later.",
            "connection_error": "⚠️ Problem connecting to the weather service.",
            "weather_error": "❌ Failed to get weather data.",
            "forecast_timeout": "⏳ Forecast request timed out",
            "forecast_network_error": "⚠️ Network error: {error}",
            "forecast_error": "❌ Forecast error: {error}",
            "choose_language": "Choose language:",
            "language_set": "✅ Language changed to {language}.",
            "weather_format": "🌆 City: {city}\n🌡 Temperature: {temp}°C (feels like {feels_like}°C)\n📛 Humidity: {humidity}%\n💨 Wind: {wind} m/s\n🌈 Weather: {description}",
            "forecast_title": "📅 5-day forecast for {city}:\n\n",
            "forecast_item": "📅 {date}: {desc}, {temp}°C\n",
            "history_title": "🕐 Your request history:",
            "favorites_title": "★ Your favorite cities:",
            "button_weather": "/weather",
            "button_forecast": "/forecast",
            "button_history": "/history",
            "button_favorites": "/favorites",
            "button_help": "/help",
            "button_forecast": "5-day forecast",
            "button_add_fav": "★ Add to favorites",
            "button_remove_fav": "★ Remove from favorites",
            "button_clear_favorites": "🗑️ Clear all favorites",
            "general_error": "⚠️ An error occurred while processing your request"
        }
    }

    for filename, content in locales.items():
        file_path = os.path.join(settings.LOCALES_DIR, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            log(f"Создан файл локализации: {filename}")


def main():
    setup_logger()
    os.makedirs(settings.LOCALES_DIR, exist_ok=True)
    os.makedirs("storage", exist_ok=True)
    create_locale_files()

    if not os.path.exists(settings.STORAGE_FILE):
        with open(settings.STORAGE_FILE, 'w') as f:
            json.dump({"history": {}, "favorites": {}, "settings": {}, "banned_users": {}, "user_count": 0}, f)

    application = Application.builder().token("7527150739:AAH4xvQ7D197oqop8GMp4BxSXl8aiH_0avg").build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("weather", commands.weather))
    application.add_handler(CommandHandler("forecast", commands.forecast))
    application.add_handler(CommandHandler("history", commands.history))
    application.add_handler(CommandHandler("favorites", commands.favorites))
    application.add_handler(CommandHandler("add_fav", commands.add_fav))
    application.add_handler(CommandHandler("remove_fav", commands.remove_fav))
    application.add_handler(CommandHandler("language", commands.language_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Админ-команды
    application.add_handler(CommandHandler("stats", commands.stats_command))
    application.add_handler(CommandHandler("broadcast", commands.broadcast_command))
    application.add_handler(CommandHandler("ban", commands.ban_command))
    application.add_handler(CommandHandler("unban", commands.unban_command))

    log("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()