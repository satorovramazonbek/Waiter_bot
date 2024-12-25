from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton


def c1ontact_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(text="📱 Raqamni ulashish", request_contact=True))


def insert_food():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Tovar qo'shish ➕")).insert(
        KeyboardButton(text="Saqlash ✅"))


def food_category():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Tovar turini qo'shish ➕")).insert(
        KeyboardButton(text="Tovar turlarini ko'rish ⚙️")).insert(KeyboardButton(text="Tovarlarni ko'rish")).insert(
        KeyboardButton(text="Saqlash ✅"))


def book_food():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Buyurtma berish 🔸")).insert(
        KeyboardButton(text="Xotirani ko'rish"))


def end_of():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Buyurtmalarni rasmiylashtirish")).insert(
        KeyboardButton(text="Buyurtmani tahrirlash")).add(KeyboardButton(text="Yangi buyurtma"))


def number_keyboard(count):
    ikb = InlineKeyboardMarkup(row_width=count // 2 + 1)
    for i in range(1, count + 1):
        if i == 6:
            ikb.add(InlineKeyboardButton(text=str(i), callback_data=str(i)))
        else:
            ikb.insert(InlineKeyboardButton(text=str(i), callback_data=str(i)))
    return ikb


def create_keyboard(name, num):
    # Removing empty lines
    lines = [line.strip() for line in name.splitlines() if line.strip()]

    # Creating keyboard
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # Validating num
    if num > 0 and num <= len(lines):
        for i in range(num):
            # Creating button
            button = KeyboardButton(text=lines[i])  # Creating button with text from line
            keyboard.add(button)  # Adding button to the keyboard
    else:
        return None  # Return None if num is not valid
    return keyboard


def create_number_buttons(count):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1, count + 1):
        button = InlineKeyboardButton(
            text=str(i),
            callback_data=f"inb{i}"
        )
        keyboard.insert(button)
    return keyboard

def create_insert():
    keyboard = InlineKeyboardMarkup(row_width=3)  # Row width - 3, har bir qatorda 3 tugma
    # Tugmalarni yaratish
    button_add = InlineKeyboardButton(text="➕", callback_data="add_food")
    button_minus = InlineKeyboardButton(text="➖", callback_data="minus_food")
    button_check = InlineKeyboardButton(text="✔️", callback_data="confirm_food")

    # Tugmalarni keyin to'g'ridan-to'g'ri qo'shish
    keyboard.add(button_add, button_minus, button_check)  # add() methodi yordamida tugmalarni qo'shamiz

    return keyboard

def create_food_button(count, number):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1, count + 1):
        button = InlineKeyboardButton(
            text=str(i),
            callback_data=f"finb{number}_{i}"
        )
        keyboard.insert(button)
    keyboard.insert(InlineKeyboardButton(text="👈", callback_data='exit'))
    return keyboard


def create_history_button(count):
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(1, count + 1):
        button = InlineKeyboardButton(
            text=str(i),
            callback_data=f"hinb_{i}"
        )
        keyboard.insert(button)
    keyboard.insert(InlineKeyboardButton(text="👈", callback_data='exit'))
    return keyboard
