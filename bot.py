import telebot
from telebot import types
import datetime
import time
import json
from PIL import Image
import os

# Замените 'YOUR_BOT_TOKEN' на ваш токен бота
bot = telebot.TeleBot('7570956742:AAE3NLprO8RO96hfVTpnmE3UqQZRWlK3XH8')

user_data = {}

try:
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
except FileNotFoundError:
    pass

async def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)

async def get_wish_list(user_id, category=None):
    # ... (предыдущий код get_wish_list)

async def add_wish(user_id, wish, category, deadline=None, image=None):
    # ... (предыдущий код add_wish)

async def edit_wish(user_id, category, wish_index, new_wish, new_deadline=None, new_image=None):
    # ... (предыдущий код edit_wish)

async def delete_wish(user_id, category, wish_index):
    # ... (предыдущий код delete_wish)

# --- Обработчики команд и сообщений ---
@bot.message_handler(commands=['start'])
async def start_message(message):
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
async def handle_message(message):
    user_id = str(message.chat.id)
    user_data.setdefault(user_id, {"categories": {}, "last_interaction": time.time()})
    user_data[user_id]["last_interaction"] = time.time()
    save_user_data()

    if message.text == "✨ Добавить желание":
        bot.send_message(message.chat.id, "В какую категорию добавить желание? (Если категории нет, создай ее через меню '🗂️ Категории')")
        bot.register_next_step_handler(message, add_wish_category_handler)

    elif message.text == "📝 Редактировать желание":
        categories = list(user_data[user_id]["categories"].keys())
        if categories:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(cat) for cat in categories])
            bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)
            bot.register_next_step_handler(message, edit_wish_category_handler)
        else:
            bot.send_message(message.chat.id, "У тебя пока нет категорий. Создай категорию через меню '🗂️ Категории'.")

    elif message.text == "❌ Удалить желание":
        # ... (логика, аналогичная редактированию, но с удалением) - см. ниже

    elif message.text == "👀 Просмотреть желания":
        categories = list(user_data[user_id]["categories"].keys())
        if categories:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(cat) for cat in categories + ["Все категории"]]) # Добавляем кнопку "Все категории"
            bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)
            bot.register_next_step_handler(message, view_wishes_category_handler)
        else:
            bot.send_message(message.chat.id, "У тебя пока нет категорий. Создай категорию через меню '🗂️ Категории'.")

    elif message.text == "🗂️ Категории":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton("➕ Создать категорию"), types.KeyboardButton("➖ Удалить категорию"), types.KeyboardButton("✏️ Переименовать категорию"), types.KeyboardButton("⬅️ Назад"))
        bot.send_message(message.chat.id, "Управление категориями:", reply_markup=markup)
        bot.register_next_step_handler(message, manage_categories_handler)

# --- Функции для добавления желаний ---
async def add_wish_category_handler(message):
    user_id = str(message.chat.id)
    category = message.text
    bot.send_message(message.chat.id, "Напиши свое желание:")
    bot.register_next_step_handler(message, lambda msg: add_wish_text_handler(msg, user_id, category))

async def add_wish_text_handler(message, user_id, category):
    wish_text = message.text
    bot.send_message(message.chat.id, "Укажи дедлайн в формате ГГГГ-ММ-ДД (опционально):")
    bot.register_next_step_handler(message, lambda msg: add_wish_deadline_handler(msg, user_id, category, wish_text))

async def add_wish_deadline_handler(message, user_id, category, wish_text):
    deadline = message.text
    if deadline.lower() == "нет" or deadline == "" or deadline.lower() == "пропустить":
        deadline = None
    add_wish(user_id, wish_text, category, deadline) # Добавляем deadline
    bot.send_message(message.chat.id, f"Желание '{wish_text}' добавлено в категорию '{category}'!")

# --- Функции для редактирования желаний ---
async def edit_wish_category_handler(message):
    user_id = str(message.chat.id)
    category = message.text
    wishes = get_wish_list(user_id, category)
    if wishes:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i, wish_data in enumerate(wishes):
            markup.add(types.KeyboardButton(f"{i+1}. {wish_data['wish']}"))
        bot.send_message(message.chat.id, "Выбери желание для редактирования:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: edit_wish_select_handler(msg, user_id, category))
    else:
        bot.send_message(message.chat.id, "В этой категории нет желаний.")

async def edit_wish_select_handler(message, user_id, category):
    try:
        wish_index = int(message.text.split(".")[0]) - 1
        bot.send_message(message.chat.id, "Введи новый текст желания:")
        bot.register_next_step_handler(message, lambda msg: edit_wish_text_handler(msg, user_id, category, wish_index))
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный номер желания.")

async def edit_wish_text_handler(message, user_id, category, wish_index):
    new_wish_text = message.text
    bot.send_message(message.chat.id, "Введи новый дедлайн в формате ГГГГ-ММ-ДД (опционально, 'пропустить' чтобы оставить прежний):")
    bot.register_next_step_handler(message, lambda msg: edit_wish_deadline_handler(msg, user_id, category, wish_index, new_wish_text))

async def edit_wish_deadline_handler(message, user_id, category, wish_index, new_wish_text):
    new_deadline = message.text
    if new_deadline.lower() == "нет" or new_deadline == "" or new_deadline.lower() == "пропустить":
        new_deadline = None # Или можно взять старый дедлайн из данных
    if edit_wish(user_id, category, wish_index, new_wish_text, new_deadline):
        bot.send_message(message.chat.id, "Желание успешно изменено!")
    else:
        bot.send_message(message.chat.id, "Не удалось изменить желание.")

# --- Функции для удаления желаний ---
# ... (аналогично редактированию, но с удалением)

# --- Функции для просмотра желаний ---
async def view_wishes_category_handler(message):
    user_id = str(message.chat.id)
    chosen_category = message.text
    if chosen_category == "Все категории":
        wishes = get_wish_list(user_id)
    else:
        wishes = get_wish_list(user_id, chosen_category)

    if wishes:
        response = ""
        for i, wish_data in enumerate(wishes):
            response += f"{i+1}. {wish_data['wish']}"
            if wish_data['deadline']:
                response += f" (Дедлайн: {wish_data['deadline']})"
            response += "\n"
        bot.send_message(message.chat.id, response if response else "Желаний нет.")
    else:
        bot.send_message(message.chat.id, "В этой категории нет желаний." if chosen_category != "Все категории" else "У тебя пока нет желаний.")

# --- Функции для управления категориями ---
async def manage_categories_handler(message):
    user_id = str(message.chat.id)
    if message.text == "➕ Создать категорию":
        bot.send_message(message.chat.id, "Введите название новой категории:")
        bot.register_next_step_handler(message, create_category_handler)

    elif message.text == "➖ Удалить категорию":
         # ... (логика для удаления категории)

    elif message.text == "✏️ Переименовать категорию":
         # ... (логика для переименования категории)

    elif message.text == "⬅️ Назад":
        start_message(message) # Возвращаемся к главному меню

async def create_category_handler(message):
    user_id = str(message.chat.id)
    category_name = message.text
    user_data.setdefault(user_id, {"categories": {}})
    if category_name not in user_data[user_id]["categories"]:
        user_data[user_id]["categories"][category_name] = []
        save_user_data()
        bot.send_message(message.chat.id, f"Категория '{category_name}' создана!")
    else:
        bot.send_message(message.chat.id, f"Категория '{category_name}' уже существует!")

# ... (остальной код handle_photo, цикл напоминаний)
# ... (аналогичная обработка для уasync даления и переименования категорий)

bot.polling()