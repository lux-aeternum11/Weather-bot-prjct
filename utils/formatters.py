# ===== Форматирование данных =====
def format_weather(weather_data: dict, tr: dict) -> str:
    city = weather_data['name']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    wind = weather_data['wind']['speed']
    description = weather_data['weather'][0]['description'].capitalize()

    return tr['weather_format'].format(
        city=city,
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        wind=wind,
        description=description
    )
