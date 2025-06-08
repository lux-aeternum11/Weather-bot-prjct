from weather_bot.config import settings

def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS