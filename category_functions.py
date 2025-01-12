from utils import bot, user_data, save_user_data
from telebot import types


def manage_categories_handler(message, start_message):
    if message.text == "➕ Создать категорию":
        bot.send_message(message.chat.id, "Введи название новой категории:")
        bot.register_next_step_handler(message, create_category_handler)

    elif message.text == "➖ Удалить категорию":
        user_id = str(message.chat.id)
        categories = list(user_data[user_id]["categories"].keys())
        if categories:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(cat) for cat in categories])
            bot.send_message(message.chat.id, "Выбери категорию для удаления:", reply_markup=markup)
            bot.register_next_step_handler(message, delete_category_handler)
        else:
            bot.send_message(message.chat.id, "У тебя пока нет категорий.")

    elif message.text == "✏️ Переименовать категорию":
        user_id = str(message.chat.id)
        categories = list(user_data[user_id]["categories"].keys())
        if categories:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(cat) for cat in categories])
            bot.send_message(message.chat.id, "Выбери категорию для переименования:", reply_markup=markup)
            bot.register_next_step_handler(message, rename_category_handler)
        else:
            bot.send_message(message.chat.id, "У тебя пока нет категорий.")

    elif message.text == "⬅️ Назад":
        start_message(message) # Здесь нужно вызвать функцию start_message из main.py
def manage_categories_start(message, bot, user_data):
    user_id = str(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Создать категорию", "➖ Удалить категорию", "✏️ Переименовать категорию", "⬅️ Назад")
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup)
    #bot.register_next_step_handler(message, manage_categories_handler)
    bot.register_next_step_handler(message, lambda msg: create_category_handler(msg, bot, user_data))

def create_category_handler(message, bot, user_data):
    print("create_category_handler вызвана!")
    user_id = str(message.chat.id)
    category_name = message.text
    user_data[user_id]["categories"][category_name] = {} # Создаем новую категорию
    save_user_data()
    bot.send_message(message.chat.id, f"Категория '{category_name}' создана!")

def delete_category_handler(message):
    user_id = str(message.chat.id)
    category_name = message.text
    if category_name in user_data[user_id]["categories"]:
        del user_data[user_id]["categories"][category_name]
        save_user_data()
        bot.send_message(message.chat.id, f"Категория '{category_name}' удалена!")
    else:
        bot.send_message(message.chat.id, f"Категории '{category_name}' не существует.")

def rename_category_handler(message):
    user_id = str(message.chat.id)
    old_category_name = message.text
    if old_category_name in user_data[user_id]["categories"]:
        bot.send_message(message.chat.id, "Введи новое название категории:")
        bot.register_next_step_handler(message, lambda msg: rename_category_confirm_handler(msg, user_id, old_category_name))
    else:
        bot.send_message(message.chat.id, f"Категории '{old_category_name}' не существует.")

def rename_category_confirm_handler(message, user_id, old_category_name):
    new_category_name = message.text
    user_data[user_id]["categories"][new_category_name] = user_data[user_id]["categories"].pop(old_category_name)
    save_user_data()
    bot.send_message(message.chat.id, f"Категория '{old_category_name}' переименована в '{new_category_name}'!")