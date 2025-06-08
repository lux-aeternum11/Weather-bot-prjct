import json
import os
from weather_bot.config import settings

# ===== Постоянное хранилище данных =====
def load_data():
    """Загрузка данных из файла хранилища"""
    try:
        if os.path.exists(settings.STORAGE_FILE):
            with open(settings.STORAGE_FILE, 'r') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {
        "history": {},
        "favorites": {},
        "settings": {},
        "banned_users": {},  # Новое поле для блокировок
        "user_count": 0  # Счетчик пользователей
    }



def save_data(data):
    """Сохранение данных в файл хранилища"""
    with open(settings.STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def is_user_banned(user_id: int) -> bool:
    """Проверка блокировки пользователя"""
    user_id = str(user_id)
    storage = load_data()
    return user_id in storage.get("banned_users", {})


def ban_user(user_id: int, reason: str = "No reason provided"):
    """Блокировка пользователя"""
    user_id = str(user_id)
    storage = load_data()

    if "banned_users" not in storage:
        storage["banned_users"] = {}

    storage["banned_users"][user_id] = reason
    save_data(storage)


def unban_user(user_id: int):
    """Разблокировка пользователя"""
    user_id = str(user_id)
    storage = load_data()

    if "banned_users" in storage and user_id in storage["banned_users"]:
        del storage["banned_users"][user_id]
        save_data(storage)
        return True
    return False


def get_user_stats():
    """Получение статистики пользователей"""
    storage = load_data()
    stats = {
        "total_users": len(storage.get("history", {})),
        "active_users": sum(1 for user in storage.get("history", {}) if len(storage["history"][user]) > 0),
        "banned_users": len(storage.get("banned_users", {})),
        "with_favorites": sum(1 for user in storage.get("favorites", {}) if storage["favorites"][user])
    }
    return stats


def increment_user_count():
    """Увеличение счетчика пользователей"""
    storage = load_data()
    storage["user_count"] = storage.get("user_count", 0) + 1
    save_data(storage)


def get_all_users():
    """Получение списка всех пользователей"""
    storage = load_data()
    return list(storage.get("history", {}).keys())


def add_to_history(user_id, city):
    """Добавление города в историю запросов"""
    user_id = str(user_id)
    storage = load_data()

    if user_id not in storage["history"]:
        storage["history"][user_id] = []
        increment_user_count()  # Новый пользователь

    city = city.title()
    if city in storage["history"][user_id]:
        storage["history"][user_id].remove(city)

    storage["history"][user_id].insert(0, city)

    # Ограничиваем историю
    if len(storage["history"][user_id]) > 5:
        storage["history"][user_id] = storage["history"][user_id][:5]

    save_data(storage)


def get_history(user_id):
    """Получение истории запросов пользователя"""
    user_id = str(user_id)
    storage = load_data()
    return storage["history"].get(user_id, [])


def add_favorite(user_id, city):
    """Добавление города в избранное"""
    user_id = str(user_id)
    storage = load_data()

    if user_id not in storage["favorites"]:
        storage["favorites"][user_id] = []

    city = city.title()
    if city not in storage["favorites"][user_id]:
        storage["favorites"][user_id].append(city)
        save_data(storage)
        return True
    return False


def get_favorites(user_id):
    """Получение списка избранных городов"""
    user_id = str(user_id)
    storage = load_data()
    return storage["favorites"].get(user_id, [])


def remove_favorite(user_id, city):
    """Удаление города из избранного"""
    user_id = str(user_id)
    storage = load_data()

    if user_id in storage["favorites"]:
        city = city.title()
        if city in storage["favorites"][user_id]:
            storage["favorites"][user_id].remove(city)
            save_data(storage)
            return True
    return False

