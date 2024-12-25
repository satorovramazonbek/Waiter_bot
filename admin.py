from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup
from keyboards import food_category, insert_food  # Kerakli klaviaturalarni import qilish
from database import *  # Ma'lumotlar bazasiga oid funksiyalarni import qilish
from aiogram.dispatcher.filters.state import State, StatesGroup
from main import dp  # main.py faylidan dp ni import qilish

class sequence(StatesGroup):
    phone_number = State()
    and_others = State()
    edg = State()

# Admin uchun maxsus menyu
@dp.message_handler(commands='admin_for_food')
async def admin_menu(message: types.Message):
    if message.from_user.id == 6394467123:  # Adminning user_id sini tekshirish
        await message.answer(
            text=f"Assalomu-aleykum admin bo'limiga xush kelibsiz tovar qo'shish uchun pasdagi \n<b>Tovar qo'shish ➕</b> tugmasini bosing",
            parse_mode="HTML",
            reply_markup=food_category()  # Admin uchun menyu
        )
    else:
        await message.answer(text="Sizda admin huquqlari yo'q.")

@dp.message_handler(Text("Tovar turini qo'shish ➕"))
async def add_category(message: types.Message):
    # Admin kategoriya qo'shishi mumkin
    await message.answer(text="Tovar turi nomini uzating\nTovar turini qo'shishni to'xtatish uchun <b>Saqlash  ✅</b>tugmasini bosing",
                         parse_mode='HTML')
    await sequence.edg.set()

@dp.message_handler(Text("Tovar turlarini ko'rish ⚙️"))
async def add_category(message: types.Message):
    # Admin barcha kategoriyalarni ko'rishi mumkin
    id1 = await get_item_count('food_table')
    item = await get_category_by_id(id1, 'food_table')
    await message.answer(text=item, reply_markup=insert_food())

@dp.message_handler(Text("Tovar qo'shish ➕"))
async def add_item(message: types.Message):
    # Admin yangi tovar qo'shish uchun buyruq beradi
    await message.answer(text="Tovar qo'shish uchun quyidagi misoldan foydalaning '*' belgilari qo'yilishi shart")
    await message.answer(text="*tovar*Coca-Cola 1.5litr *narxi*12000 *index1*2")
    await sequence.phone_number.set()

@dp.message_handler(state=sequence.edg)
async def category(message: types.Message):
    if message.text == "Saqlash ✅":
        await message.answer(text="Yoqimli ishtaha 🍽 ", reply_markup=food_category())
    else:
        await insert_food_table(message.text)
        await message.answer(text="Tovar turi qo'shildi")
        await message.answer(text="Yana tovar turini qo'shmoqchi bo'lsangiz nomini yozib uzating!")
