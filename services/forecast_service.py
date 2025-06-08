# services/forecast_service.py
import asyncio
import requests
from weather_bot.utils.logger import log
from weather_bot.utils.locale_utils import get_user_locale
from weather_bot.config.settings import OPENWEATHER_API_KEY, REQUEST_TIMEOUT

async def send_forecast(update, city, user_id):
    tr = get_user_locale(user_id)
    lang = tr['lang_code']

    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang={lang}"

        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(url, timeout=REQUEST_TIMEOUT)),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if data.get('cod') != '200':
            raise Exception(f"API error: {data.get('message', 'Unknown error')}")

        forecast_text = tr['forecast_title'].format(city=city)
        day_counter = 0
        prev_date = ""

        for item in data['list']:
            date = item['dt_txt'].split()[0]
            if date != prev_date:
                if day_counter >= 5:
                    break
                prev_date = date
                day_counter += 1
                temp = item['main']['temp']
                desc = item['weather'][0]['description'].capitalize()
                forecast_text += tr['forecast_item'].format(date=date, desc=desc, temp=temp)

        await update.message.reply_text(forecast_text)

    except asyncio.TimeoutError:
        await update.message.reply_text(tr['forecast_timeout'])
        log(f"Таймаут прогноза для {city}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(tr['forecast_network_error'].format(error=str(e)))
        log(f"Ошибка сети при прогнозе: {str(e)}")
    except Exception as e:
        await update.message.reply_text(tr['forecast_error'].format(error=str(e)))
        log(f"Ошибка прогноза: {str(e)}")