import os
import telebot
from telebot import types
from utils import save_user_data, get_wish_list, bot, user_data

@bot.message_handler(content_types=['photo']) # Это нужно перенести в photo_functions.py

def handle_photo(message):
    user_id = str(message.chat.id)
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filepath = os.path.join("user_images", f"{user_id}_{message.photo[-1].file_id}.jpg")
    os.makedirs("user_images", exist_ok=True)

    with open(filepath, 'wb') as new_file:
        new_file.write(downloaded_file)

    categories = list(user_data[user_id]["categories"].keys())
    if not categories:
        bot.send_message(message.chat.id, "У тебя нет категорий. Создай категорию, прежде чем добавлять фото.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[types.KeyboardButton(cat) for cat in categories])
    bot.send_message(message.chat.id, "Выбери категорию для добавления фото:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_photo_category(msg, user_id, filepath))

def handle_photo_category(message, user_id, filepath):
    category = message.text
    wishes = get_wish_list(user_id, category)
    if not wishes:
        bot.send_message(message.chat.id, "В этой категории нет желаний. Добавь желание перед добавлением фото.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i, wish_data in enumerate(wishes):
        markup.add(types.KeyboardButton(f"{i+1}. {wish_data['wish']}"))
    bot.send_message(message.chat.id, "Выбери желание, к которому прикрепить фото:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_photo_wish(msg, user_id, category, filepath))

def handle_photo_wish(message, user_id, category, filepath):
    try:
        wish_index = int(message.text.split(".")[0]) - 1
        wishes = get_wish_list(user_id, category)
        wishes[wish_index]["image"] = filepath
        user_data[str(user_id)]["categories"][category] = wishes
        save_user_data()
        bot.send_message(message.chat.id, "Фотография успешно прикреплена!")
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный номер желания.")