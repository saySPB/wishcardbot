# ... (импорты, функции add_wish, edit_wish, delete_wish) 
from telebot import types
from utils import bot, get_wish_list, edit_wish, delete_wish, add_wish
def add_wish_start(message, bot):
    user_id = str(message.chat.id)
    bot.send_message(message.chat.id, "В какую категорию добавить желание? (Если категории нет, создай ее через меню '🗂️ Категории')")
    bot.register_next_step_handler(message, add_wish_category_handler) # Передача user_data edit_wish_start, delete_wish_start, view_wishes_start, manage_categories_start
def add_wish_category_handler(message):
    user_id = str(message.chat.id)
    category = message.text
    bot.send_message(message.chat.id, "Напиши свое желание:")
    bot.register_next_step_handler(message, lambda msg: add_wish_text_handler(msg, user_id, category))

def add_wish_text_handler(message, user_id, category):
    wish_text = message.text
    bot.send_message(message.chat.id, "Укажи дедлайн в формате ГГГГ-ММ-ДД (опционально):")
    bot.register_next_step_handler(message, lambda msg: add_wish_deadline_handler(msg, user_id, category, wish_text))

def add_wish_deadline_handler(message, user_id, category, wish_text):
    deadline = message.text
    if deadline.lower() == "нет" or deadline == "" or deadline.lower() == "пропустить":
        deadline = None
    add_wish(user_id, wish_text, category, deadline) # Добавляем deadline
    bot.send_message(message.chat.id, f"Желание '{wish_text}' добавлено в категорию '{category}'!")

def edit_wish_start(message, bot, user_data):
    user_id = str(message.chat.id)
    categories = list(user_data[user_id]["categories"].keys())
    if categories:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(cat) for cat in categories])
        bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: edit_wish_category_handler(msg, bot, user_data))
    else:
        bot.send_message(message.chat.id, "У тебя пока нет категорий. Создай категорию через меню '🗂️ Категории'.")

def edit_wish_category_handler(message, bot, user_data):
    user_id = str(message.chat.id)
    category = message.text
    wishes = get_wish_list(user_id, category)
    if wishes:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i, wish_data in enumerate(wishes):
            markup.add(types.KeyboardButton(f"{i+1}. {wish_data['wish']}"))
        bot.send_message(message.chat.id, "Выбери желание для редактирования:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: edit_wish_select_handler(msg, bot, user_data, category))
    else:
        bot.send_message(message.chat.id, "В этой категории нет желаний.")

def edit_wish_select_handler(message, bot, user_data, category):
    user_id = str(message.chat.id)
    try:
        wish_index = int(message.text.split(".")[0]) - 1
        bot.send_message(message.chat.id, "Введи новый текст желания:")
        bot.register_next_step_handler(message, lambda msg: edit_wish_text_handler(msg, bot, user_data, category, wish_index))
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный номер желания.")

def edit_wish_text_handler(message, bot, user_data, category, wish_index):
    user_id = str(message.chat.id)
    new_wish_text = message.text
    bot.send_message(message.chat.id, "Введи новый дедлайн в формате ГГГГ-ММ-ДД (опционально, 'пропустить' чтобы оставить прежний):")
    bot.register_next_step_handler(message, lambda msg: edit_wish_deadline_handler(msg, bot, user_data, category, wish_index, new_wish_text))

def edit_wish_deadline_handler(message, bot, user_data, category, wish_index, new_wish_text):
    user_id = str(message.chat.id)
    new_deadline = message.text
    if new_deadline.lower() == "нет" or new_deadline == "" or new_deadline.lower() == "пропустить":
        new_deadline = None
    
    if edit_wish(user_id, category, wish_index, new_wish_text, new_deadline): # Передача user_id
        bot.send_message(message.chat.id, "Желание успешно изменено!")
    else:
        bot.send_message(message.chat.id, "Не удалось изменить желание.")

def view_wishes_start(message, bot, user_data):
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

def delete_wish_start(message, bot, user_data):
    user_id = str(message.chat.id)
    categories = list(user_data[user_id]["categories"].keys())
    if categories:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(cat) for cat in categories])
        bot.send_message(message.chat.id, "Выбери категорию:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: delete_wish_category_handler(msg, bot, user_data))
    else:
        bot.send_message(message.chat.id, "У тебя пока нет категорий. Создай категорию через меню '🗂️ Категории'.")

def delete_wish_category_handler(message, bot, user_data):
    user_id = str(message.chat.id)
    category = message.text
    wishes = get_wish_list(user_id, category)
    if wishes:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i, wish_data in enumerate(wishes):
            markup.add(types.KeyboardButton(f"{i+1}. {wish_data['wish']}"))
        bot.send_message(message.chat.id, "Выбери желание для удаления:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: delete_wish_select_handler(msg, bot, user_data, category))
    else:
        bot.send_message(message.chat.id, "В этой категории нет желаний.")


def delete_wish_select_handler(message, bot, user_data, category):
    user_id = str(message.chat.id)
    try:
        wish_index = int(message.text.split(".")[0]) - 1
        if delete_wish(user_id, category, wish_index):
            bot.send_message(message.chat.id, "Желание успешно удалено!")
        else:
            bot.send_message(message.chat.id, "Не удалось удалить желание.") # Более информативное сообщение об ошибке
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный номер желания.")