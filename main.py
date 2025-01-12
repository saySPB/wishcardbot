#Файл `main.py` содержит основной цикл бота и обработчики команд. Главная проблема, влияющая на производительность, — это цикл напоминаний, находящийся *внутри* обработчика `handle_message`.
import telebot
from telebot import types
import time
import json
import os

from utils import bot, save_user_data
from wish_functions import add_wish_start, edit_wish_start, delete_wish_start, view_wishes_start
from category_functions import manage_categories_start 
#from photo_functions import *
#from wish_functions import *


try:
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["✨ Добавить желание", "📝 Редактировать желание", "❌ Удалить желание", "👀 Просмотреть желания", "🗂️ Категории"]
    markup.add(*[types.KeyboardButton(text) for text in buttons])

    user_id = str(message.chat.id)
    if user_id not in user_data:
        user_data[user_id] = {"categories": {}, "last_interaction": time.time()}
    else:
        user_data[user_id]["last_interaction"] = time.time()
    save_user_data()

    bot.send_message(message.chat.id, "🌟 Привет! Я твой помощник в достижении целей! ✨\nВыбери действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global user_data
    user_id = str(message.chat.id) # получаем user_id

    if user_id not in user_data: # проверяем есть ли данные по этому пользователю
        user_data[user_id] = {"categories": {}}

    if message.text == "✨ Добавить желание":
        add_wish_start(message, bot)
    elif message.text == "📝 Редактировать желание":
        edit_wish_start(message, bot, user_data)
    elif message.text == "❌ Удалить желание":
        delete_wish_start(message, bot, user_data)
    elif message.text == "👀 Просмотреть желания":
        user_id = str(message.chat.id)
        categories = list(user_data[user_id]["categories"].keys())
        if categories:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(cat) for cat in categories])
            markup.add(types.KeyboardButton("Все категории")) # Добавляем кнопку "Все категории"
            bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: view_wishes_start(msg, bot, user_data))
        else:
            bot.send_message(message.chat.id, "У тебя пока нет категорий. Создай категорию через меню '🗂️ Категории'.")

    elif message.text == "🗂️ Категории":
        manage_categories_start(message, bot, user_data)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id # Получаем chat_id из сообщения

    markup = telebot.types.InlineKeyboardMarkup()
    add_button = telebot.types.InlineKeyboardButton(text="Добавить", callback_data="add")
    delete_button = telebot.types.InlineKeyboardButton(text="Удалить", callback_data="delete")
    edit_button = telebot.types.InlineKeyboardButton(text="Редактировать", callback_data="edit")
    markup.row(add_button, delete_button, edit_button)

    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(state="waiting_for_category_name") # Обработчик для состояния ожидания названия
def handle_new_category_name(message):
    chat_id = message.chat.id
    category_name = message.text
    # ... (ваш код для создания категории с именем category_name)
    bot.send_message(chat_id, f"Категория '{category_name}' создана!")
    bot.delete_state(chat_id, chat_id) # Сбрасываем состояние после получения названия

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "add_category": # Изменено: callback_data для кнопки "Добавить"
        # Запоминаем chat_id, чтобы знать, куда отправить следующий вопрос
        bot.set_state(chat_id, "waiting_for_category_name", chat_id) # Устанавливаем состояние ожидания названия
        bot.send_message(chat_id, "Введите название новой категории:")
    elif call.data == "delete":
        # Логика для удаления категории
        bot.send_message(chat_id, "Вы нажали кнопку Удалить!")
    elif call.data == "edit":
        # Логика для редактирования категории
        bot.send_message(chat_id, "Вы нажали кнопку Редактировать!")

# --- Цикл напоминаний ---

    while True:
        current_time = time.time()
        for user_id, data in user_data.items():
            if current_time - data.get("last_interaction", 0) >= 24 * 60 * 60: # 24 часа
                bot.send_message(int(user_id), "👋 Привет! Не забывай о своих мечтах! ✨ Загляни в приложение, чтобы вспомнить свои желания. 😉")
                data["last_interaction"] = current_time
                save_user_data()
        time.sleep(60 * 60) # проверка каждый час


bot.infinity_polling()

