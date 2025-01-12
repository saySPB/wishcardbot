import json
import telebot
from telebot import types
user_data = {}

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)
def load_user_data():
    """Загружает данные пользователей из файла user_data.json."""
    global user_data # Изменяем глобальную переменную user_data
    try:
        with open("user_data.json", "r") as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

def get_wish_list(user_id, category=None):
    user_categories = user_data.get(str(user_id), {}).get("categories", {})
    if category:
        return user_categories.get(category, [])
    else:
        all_wishes = []
        for wishes in user_categories.values():
            all_wishes.extend(wishes)
        return all_wishes


def add_wish(user_id, wish, category, deadline=None):
    """Добавляет новое желание в список желаний пользователя."""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {"categories": {}}
    if category not in user_data[str(user_id)]["categories"]:
        user_data[str(user_id)]["categories"][category] = []
    user_data[str(user_id)]["categories"][category].append({"wish": wish, "deadline": deadline})
    save_user_data()


def edit_wish(user_id, category, wish_index, new_wish, new_deadline=None):
    """Редактирует существующее желание."""
    try:
        user_data[str(user_id)]["categories"][category][wish_index] = {"wish": new_wish, "deadline": new_deadline}
        save_user_data()
        return True
    except (KeyError, IndexError): # Обработка ошибок, если категория или индекс не существуют
        return False

def delete_wish(user_id, category, wish_index):
    """Удаляет желание из списка."""
    try:
        del user_data[str(user_id)]["categories"][category][wish_index]
        save_user_data()
        return True
    except (KeyError, IndexError):
        return False

bot = telebot.TeleBot('7570956742:AAE3NLprO8RO96hfVTpnmE3UqQZRWlK3XH8')
