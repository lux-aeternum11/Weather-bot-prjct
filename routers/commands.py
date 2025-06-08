from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from weather_bot.utils.logger import log
from weather_bot.utils.storage import is_user_banned, add_to_history, get_history, add_favorite, get_favorites, remove_favorite
from weather_bot.utils.storage import get_user_stats, get_all_users, ban_user, unban_user
from weather_bot.utils.locale_utils import get_user_locale, set_user_language
from weather_bot.utils.formatters import format_weather
from weather_bot.services.api_client import get_weather_data
from weather_bot.config.settings import ADMIN_IDS
from weather_bot.services.forecast_service import send_forecast
from weather_bot.keyboards import KeyboardBuilder
import asyncio
from weather_bot.keyboards import KeyboardBuilder
# ===== Команды бота =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Проверка блокировки
    if is_user_banned(user.id):
        log(f"Заблокированный пользователь попытался начать: {user.id}")
        return

    log(f"Пользователь {user.id} начал работу")
    tr = get_user_locale(user.id)

    keyboard = [
        [tr['button_weather'], tr['button_forecast']],
        [tr['button_history'], tr['button_favorites']],
        [tr['button_help']]
    ]

    await update.message.reply_text(
        tr['start'].format(name=user.first_name),
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    log(f"Пользователь {user_id} запросил помощь")
    tr = get_user_locale(user_id)

    await update.message.reply_text(tr['help'])


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    tr = get_user_locale(user_id)
    args = context.args

    if not args:
        log(f"Пользователь {user_id} не указал город для погоды")
        await update.message.reply_text(tr['weather_city_missing'])
        return

    city = " ".join(args)
    log(f"Пользователь {user_id} запросил погоду для {city}")

    try:
        add_to_history(user_id, city)
        lang = tr['lang_code']
        weather_data = await get_weather_data(city, lang)
        response = format_weather(weather_data, tr)

        # Проверяем, есть ли город в избранном
        fav_list = get_favorites(user_id)
        is_favorite = city in fav_list

        # Создаем кнопки
        keyboard = [
            [InlineKeyboardButton(tr['button_forecast'], callback_data=f"forecast_{city}")]
        ]

        # Кнопка для добавления/удаления из избранного
        if is_favorite:
            keyboard.append([InlineKeyboardButton(tr['button_remove_fav'], callback_data=f"removefav_{city}")])
        else:
            keyboard.append([InlineKeyboardButton(tr['button_add_fav'], callback_data=f"addfav_{city}")])

        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        error_key = str(e)
        await update.message.reply_text(tr.get(error_key, tr['weather_error']))


async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    tr = get_user_locale(user_id)
    args = context.args

    if not args:
        log(f"Пользователь {user_id} не указал город для прогноза")
        await update.message.reply_text(tr['forecast_city_missing'])
        return

    city = " ".join(args)
    log(f"Пользователь {user_id} запросил прогноз для {city}")
    # await send_forecast(update, city, user_id)


# async def send_forecast(update, city, user_id):
#     tr = get_user_locale(user_id)
#     lang = tr['lang_code']
#
#     try:
#         add_to_history(user_id, city)
#         url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang={lang}"
#
#         response = await asyncio.wait_for(
#             asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(url, timeout=REQUEST_TIMEOUT)),
#             timeout=REQUEST_TIMEOUT
#         )
#         response.raise_for_status()
#         data = response.json()
#
#         if data.get('cod') != '200':
#             raise Exception(f"API error: {data.get('message', 'Unknown error')}")
#
#         forecast_text = tr['forecast_title'].format(city=city)
#         day_counter = 0
#         prev_date = ""
#
#         for item in data['list']:
#             date = item['dt_txt'].split()[0]
#             if date != prev_date:
#                 if day_counter >= 5:
#                     break
#                 prev_date = date
#                 day_counter += 1
#                 temp = item['main']['temp']
#                 desc = item['weather'][0]['description'].capitalize()
#                 forecast_text += tr['forecast_item'].format(date=date, desc=desc, temp=temp)
#
#         await update.message.reply_text(forecast_text)
#
#     except asyncio.TimeoutError:
#         await update.message.reply_text(tr['forecast_timeout'])
#         log(f"Таймаут прогноза для {city}")
#     except requests.exceptions.RequestException as e:
#         await update.message.reply_text(tr['forecast_network_error'].format(error=str(e)))
#         log(f"Ошибка сети при прогнозе: {str(e)}")
#     except Exception as e:
#         await update.message.reply_text(tr['forecast_error'].format(error=str(e)))
#         log(f"Ошибка прогноза: {str(e)}")
#

# ===== История запросов =====
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        return
    tr = get_user_locale(user_id)
    history_list = get_history(user_id)

    if not history_list:
        await update.message.reply_text(tr['history_empty'])
    else:
        await update.message.reply_text(
            tr['history_title'],
            reply_markup=KeyboardBuilder.history_list(tr, history_list)
        )


# ===== Избранные города =====
async def favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_user_banned(user_id):
        return
    tr = get_user_locale(user_id)
    fav_list = get_favorites(user_id)

    if not fav_list:
        await update.message.reply_text(tr['favorites_empty'])
    else:
        await update.message.reply_text(
            tr['favorites_title'],
            reply_markup=KeyboardBuilder.favorites_list(tr, fav_list)
        )

    # Создаем кнопки с действиями для каждого города
    buttons = []
    for city in fav_list:
        buttons.append([
            InlineKeyboardButton(f"🌤 {city}", callback_data=f"weather_{city}"),
            InlineKeyboardButton(tr['button_remove_fav'], callback_data=f"removefav_{city}")
        ])

    # Добавляем кнопку "Очистить все"
    buttons.append([InlineKeyboardButton(tr['button_clear_favorites'], callback_data="clear_favorites")])

    await update.message.reply_text(
        tr['favorites_title'],
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def add_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    tr = get_user_locale(user_id)
    args = context.args

    if not args:
        log(f"Пользователь {user_id} не указал город для добавления в избранное")
        await update.message.reply_text(tr['weather_city_missing'])
        return

    city = " ".join(args)
    if add_favorite(user_id, city):
        log(f"Пользователь {user_id} добавил в избранное: {city}")
        await update.message.reply_text(tr['city_added_to_fav'].format(city=city))
    else:
        await update.message.reply_text(tr['city_already_in_fav'].format(city=city))


async def remove_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    tr = get_user_locale(user_id)
    args = context.args

    if not args:
        log(f"Пользователь {user_id} не указал город для удаления из избранного")
        await update.message.reply_text(tr['weather_city_missing'])
        return

    city = " ".join(args)
    if remove_favorite(user_id, city):
        log(f"Пользователь {user_id} удалил из избранного: {city}")
        await update.message.reply_text(tr['city_removed_from_fav'].format(city=city))
    else:
        await update.message.reply_text(tr['city_not_in_fav'].format(city=city))


# ===== Команда переключения языка =====
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка блокировки
    if is_user_banned(user_id):
        return

    tr = get_user_locale(user_id)

    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]

    await update.message.reply_text(
        tr['choose_language'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===== Админ-команды =====
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка прав администратора
    if user_id not in ADMIN_IDS:
        log(f"Неавторизованный доступ к /stats: {user_id}")
        return

    stats = get_user_stats()
    response = (
        "📊 Статистика бота:\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"👤 Активных пользователей: {stats['active_users']}\n"
        f"🔒 Заблокированных: {stats['banned_users']}\n"
        f"⭐ Пользователей с избранным: {stats['with_favorites']}"
    )

    await update.message.reply_text(response)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка прав администратора
    if user_id not in ADMIN_IDS:
        log(f"Неавторизованный доступ к /broadcast: {user_id}")
        return

    # Проверка наличия сообщения для рассылки
    if not context.args:
        await update.message.reply_text("Укажите сообщение для рассылки: /broadcast Ваше сообщение")
        return

    message = " ".join(context.args)
    all_users = get_all_users()
    total = len(all_users)
    success = 0
    failed = 0

    status_msg = await update.message.reply_text(f"Рассылка начата... 0/{total}")

    for i, user_id_str in enumerate(all_users):
        try:
            await context.bot.send_message(
                chat_id=int(user_id_str),
                text=f"📢 Рассылка от администратора:\n\n{message}"
            )
            success += 1
        except Exception as e:
            log(f"Ошибка рассылки для {user_id_str}: {str(e)}")
            failed += 1

        # Обновляем статус каждые 10 сообщений
        if i % 10 == 0:
            await status_msg.edit_text(
                f"Рассылка... Отправлено: {i + 1}/{total}\n"
                f"✅ Успешно: {success}\n"
                f"❌ Ошибок: {failed}"
            )
        await asyncio.sleep(0.3)  # Задержка для избежания лимитов

    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n"
        f"👥 Всего получателей: {total}\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}"
    )


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка прав администратора
    if user_id not in ADMIN_IDS:
        log(f"Неавторизованный доступ к /ban: {user_id}")
        return

    # Проверка аргументов
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /ban <user_id> [причина]")
        return

    try:
        target_id = int(context.args[0])
        reason = " ".join(context.args[1:]) or "Причина не указана"

        # Нельзя блокировать администраторов
        if target_id in ADMIN_IDS:
            await update.message.reply_text("❌ Нельзя блокировать администраторов!")
            return

        ban_user(target_id, reason)
        log(f"Пользователь {target_id} заблокирован администратором {user_id}. Причина: {reason}")

        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"⛔ Ваш аккаунт заблокирован администратором.\nПричина: {reason}"
            )
        except Exception as e:
            log(f"Не удалось уведомить пользователя {target_id} о блокировке: {str(e)}")

        await update.message.reply_text(f"✅ Пользователь {target_id} заблокирован.\nПричина: {reason}")

    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID пользователя")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка прав администратора
    if user_id not in ADMIN_IDS:
        log(f"Неавторизованный доступ к /unban: {user_id}")
        return

    # Проверка аргументов
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /unban <user_id>")
        return

    try:
        target_id = int(context.args[0])

        if unban_user(target_id):
            log(f"Пользователь {target_id} разблокирован администратором {user_id}")

            try:
                await context.bot.send_message(
                    chat_id=target_id,
                    text="✅ Ваш аккаунт разблокирован администратором"
                )
            except Exception as e:
                log(f"Не удалось уведомить пользователя {target_id} о разблокировке: {str(e)}")

            await update.message.reply_text(f"✅ Пользователь {target_id} разблокирован")
        else:
            await update.message.reply_text("ℹ️ Пользователь не был заблокирован")

    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID пользователя")

