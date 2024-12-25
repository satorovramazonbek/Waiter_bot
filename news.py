import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Admin ID (buyurtmalarni qabul qiladigan shaxsning Telegram IDsi)
ADMIN_ID = 6394467123  # Admin ID ni o'zgartiring

# Menyu va taomlar
menu = {
    "Ichimliklar": ["Coca-Cola", "Fanta", "Sprite", "Choy"],
    "Issiq ovqatlar": ["Shashlik", "Palov", "Lag'mon", "Manti"],
    "Shirinliklar": ["Tort", "Pirojnoe", "Shirin non"],
}

# Foydalanuvchi tanlagan buyurtma
user_orders = {}

# Admin buyurtmalarini saqlash
admin_orders = {}

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)

# Botni va Dispatcherni yaratish
API_TOKEN = '7224569832:AAFK030r_FPufSFLnusDNbi3xrggTepkWhw'  # Bot tokeningizni kiriting
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


# Start komandasi
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = [
        [InlineKeyboardButton("Buyurtma berish", callback_data="order_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Xush kelibsiz! Buyurtma berishni boshlash uchun tugmani bosing.", reply_markup=reply_markup)


# "Buyurtma berish" tugmasi bosilganda
@dp.callback_query_handler(lambda c: c.data == "order_menu")
async def order_menu(callback_query: types.CallbackQuery):
    keyboard = [[InlineKeyboardButton(category, callback_data=category)] for category in menu.keys()]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text("Menyudan birini tanlang:", chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id, reply_markup=reply_markup)


# Kategoriya tanlanganda
@dp.callback_query_handler(lambda c: c.data in menu.keys())
async def handle_menu(callback_query: types.CallbackQuery):
    category = callback_query.data
    items = menu.get(category, [])

    keyboard = [[InlineKeyboardButton(item, callback_data=f"order:{item}")] for item in items]
    keyboard.append([InlineKeyboardButton("🔙 Ortga", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(f"{category} menyusi:", chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id, reply_markup=reply_markup)


# Buyurtma tanlash
@dp.callback_query_handler(lambda c: c.data.startswith('order:'))
async def handle_order(callback_query: types.CallbackQuery):
    item = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id

    if user_id not in user_orders:
        user_orders[user_id] = []
    user_orders[user_id].append(item)

    await bot.answer_callback_query(callback_query.id, text=f"{item} buyurtmangizga qo‘shildi!")
    await bot.edit_message_text(f"{item} tanlandi. Davom etishingiz mumkin.", chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id)


# Buyurtmani tasdiqlash
@dp.message_handler(lambda message: message.text.lower() == 'buyurtma')
async def confirm_order(message: types.Message):
    user_id = message.from_user.id
    orders = user_orders.get(user_id, [])

    if not orders:
        await message.answer("Hozircha buyurtmangiz yo‘q.")
        return

    order_text = "\n".join(orders)

    # Admin buyurtmalarini ro'yxatga olish
    if ADMIN_ID not in admin_orders:
        admin_orders[ADMIN_ID] = []
    admin_orders[ADMIN_ID].append(f"Foydalanuvchi @{message.from_user.username}: \n{order_text}")

    await bot.send_message(ADMIN_ID, f"Yangi buyurtma:\n\n{order_text}\n\nFoydalanuvchi: @{message.from_user.username}")

    await message.answer("Buyurtmangiz 15 daqiqada tayyor bo‘ladi! 😊")
    user_orders[user_id] = []  # Buyurtma ro‘yxatini tozalash


# Admin uchun buyurtmalarni ko'rish
@dp.message_handler(commands=['orders'])
async def view_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Sizda buyurtmalarni ko‘rish huquqi yo‘q.")
        return

    if ADMIN_ID in admin_orders and admin_orders[ADMIN_ID]:
        orders = "\n\n".join(admin_orders[ADMIN_ID])
        await message.answer(f"Buyurtmalar:\n\n{orders}")
    else:
        await message.answer("Hozircha yangi buyurtmalar yo'q.")


# Ortga qaytish
@dp.callback_query_handler(lambda c: c.data == 'back')
async def handle_back(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await start(callback_query.message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
