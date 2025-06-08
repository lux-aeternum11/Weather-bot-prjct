import asyncio
import requests
import time
import json
import os
from weather_bot.utils.logger import log
from weather_bot.utils.cache import get_cached_weather, set_cached_weather
from weather_bot.config.settings import OPENWEATHER_API_KEY, REQUEST_TIMEOUT


async def get_weather_data(city: str, lang: str) -> dict:
    cached = get_cached_weather(city, lang)
    if cached:
        log(f"Использован кэш для {city} ({lang})")
        return cached

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang={lang}"

    try:
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(url, timeout=REQUEST_TIMEOUT)),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        if data.get('cod') != 200:
            raise Exception(f"API error: {data.get('message', 'Unknown error')}")
        set_cached_weather(city, lang, data)
        return data
    except asyncio.TimeoutError:
        log(f"Таймаут при запросе погоды для {city}")
        raise Exception("timeout")
    except requests.exceptions.RequestException as e:
        log(f"Ошибка сети: {str(e)}")
        raise Exception("connection_error")
    except Exception as e:
        log(f"Ошибка API: {str(e)}")
        raise Exception("weather_error")