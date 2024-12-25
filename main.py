from config import TOKEN_API, ADMIN_ID
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, \
    ReplyKeyboardRemove, InlineQuery
from database import *
from keyboards import *
from aiogram.utils.callback_data import CallbackData
import re

storage = MemoryStorage()
btn = ReplyKeyboardMarkup(resize_keyboard=True).add()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)
cb = CallbackData('ikb', 'action')


class sequence(StatesGroup):
    phone_number = State()
    and_others = State()
    edg = State()


async def on_startup(_):
    print('Bot ishladi')
    await db_start()
    await create_table_menyu()
    await create_food_table()
    await create_history()
    await create_sum_history()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    answe = await check_user(message.from_user.id)
    if answe:
        await message.answer(text="Yoqimli ishtaha 🍽 ",
                             reply_markup=book_food())
    else:
        await message.answer(
            text=f'Salom {message.from_user.full_name} \nbotga xush kelibsiz!\nIltimos telefon raqamingizni uzating',
            reply_markup=c1ontact_keyboard())
        await sequence.phone_number.set()


@dp.message_handler(Text("Saqlash ✅"), state='*')
async def order(message: types.Message, state: FSMContext):
    await message.answer(text="Tovar qo'shish tugatildi",
                         reply_markup=book_food())
    await state.finish()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=sequence.phone_number)
async def add_item(message: types.Message, state: FSMContext):
    contact = message.contact
    if contact.user_id == message.from_user.id:
        await message.answer(f"Raxmat, {contact.full_name}.\n"
                             f"Sizning nomeringiz {contact.phone_number} qabul qilindi",
                             reply_markup=book_food())
        await insert_base(user_id=message.from_user.id,
                          number=contact.phone_number)
        await state.finish()


@dp.message_handler(commands='admin_for_food')
async def add_item(message: types.Message):
    phone_number = await check_number(user_id=message.from_user.id)
    print(str(phone_number))
    if message.from_user.id == 6394467123:
        await message.answer(
            text=f"Assalomu-aleykum admin bo'limiga xush kelibsiz tovar qo'shish uchun pasdagi \n<b>Tovar qo'shish ➕</b> tugmasini bosing",
            parse_mode="HTML",
            reply_markup=food_category())
    else:
        await message.answer(text="Yoqimli ishtaha 🍽 ",
                             reply_markup=food_category())


@dp.message_handler(Text("Tovar turini qo'shish ➕"))
async def add_category(message: types.Message):
    await message.answer(
        text="Tovar turi nomini uzating\nTovar turini qo'shishni to'xtatish uchun <b>Saqlash  ✅</b>tugmasini bosing",
        parse_mode='HTML')
    await sequence.edg.set()


@dp.message_handler(Text("Tovar turlarini ko'rish ⚙️"))
async def add_category(message: types.Message):
    id1 = await get_item_count('food_table')
    item = await get_category_by_id(id1, 'food_table')
    await message.answer(text=item,
                         reply_markup=insert_food())


@dp.message_handler(state=sequence.edg)
async def category(message: types.Message):
    if message.text == "Saqlash ✅":
        await message.answer(text="Yoqimli ishtaha 🍽 ",
                             reply_markup=food_category())
    else:
        await insert_food_table(message.text)
        await message.answer(text="Tovar turi qo'shildi")
        await message.answer(text="Yana tovar turini qo'shmoqchi bo'lsangiz nomini yozib uzating!")


@dp.message_handler(Text("Tovar qo'shish ➕"))
async def add_item(message: types.Message):
    await message.answer(text="Tovar qo'shish uchun quyidagi misoldan foydalaning '*' belgilari qo'yilishi shart")
    await message.answer(text="*tovar*Coca-Cola 1.5litr *narxi*12000 *index1*2")
    await sequence.phone_number.set()


@dp.message_handler(Text("Yangi buyurtma"))
async def store(message: types.Message):
    await message.answer(text="Yoqimli ishtaha 🍽", reply_markup=book_food())


@dp.message_handler(Text("Buyurtmani tahrirlash"))
async def store(message: types.Message):
    orders = await get_user_orders(message.from_user.id)
    formatted_text = "\n".join([
        f"{idx + 1}. {item_name} --- {item_price} so'm, Soni: {item_count}"
        for idx, (item_name, item_price, item_count) in enumerate(orders)
    ])
    await message.answer(text=formatted_text, reply_markup=create_history_button(len(orders)))


@dp.message_handler(Text("Xotirani ko'rish"))
async def store(message: types.Message):
    user_id = message.from_user.id
    result = await get_incorrect_orders(user_id)
    await message.answer(result,
                         reply_markup=end_of())


@dp.message_handler(Text("Buyurtmalarni rasmiylashtirish"))
async def show_menu(message: types.Message):
    text = await get_and_delete_incorrect_orders(user_id=message.from_user.id)
    await bot.send_message(chat_id=6394467123, text=text, reply_markup=book_food())
    await message.answer(text="Buyurtmangiz qabul qilindi 15daqiqa oralig'ida tayyor bo'ladi")



    # Muntazam ifoda bilan tovar nomi, narxi va sonini ajratib olish
    pattern = r"^\d+\.\s(.+?)\s-\s(\d+)\sso'm,\sSoni:\s(\d+)$"

    # Har bir qatorni qayta ishlash
    orders = []
    for line in text.strip().split("\n"):
        match = re.match(pattern, line)
        if match:
            item_name = match.group(1)
            item_price = int(match.group(2))
            item_count = int(match.group(3))
            orders.append((item_name, item_price, item_count))

    # Natijani ko'rish
    for order in orders:
        await add_to_total_history(user_id=message.from_user.id,
                                   item_name=order[0],
                                   item_price=order[1],
                                   item_count=order[2])
        print(f"Tovar nomi: {order[0]}, Narxi: {order[1]} so'm, Soni: {order[2]}")
@dp.message_handler(Text("Tovarlarni ko'rish"))
async def show_menu(message: types.Message):
    items = await get_items_from_menyu()
    if items:
        await message.answer(text=f"Tovarlar ro'yxati:\n\n{items}", reply_markup=book_food())
    else:
        await message.answer(text="Tovarlar mavjud emas.", reply_markup=book_food())


@dp.message_handler(state=sequence.phone_number)
async def numb(message: types.Message, state: FSMContext):
    if message.text == "Saqlash ✅":
        await message.answer(text="Yoqimli ishtaha 🍽 ",
                             reply_markup=food_category())
        await state.finish()
    else:
        text = message.text
        await filtr(text)
        await message.answer(text="Tovar qo'shildi")
        await message.answer(text="Yana tovar qo'shmoqchi bo'lsangiz namunaga mos tarzda uzating!")


async def filtr(text):
    pattern = r"\*tovar\*(.*?)\s+\*narxi\*(\d+)\s+\*index1\*(\d+)"
    match = re.search(pattern, text)
    if match:
        tovar = match.group(1)
        narxi = int(match.group(2))
        index1 = int(match.group(3))
        await insert_food_base(tovar, narxi, index1)
    elif text == "Tovar qo'shish ➕":
        await sequence.phone_number.set()
    else:
        print("Сообщение не соответствует шаблону")


@dp.message_handler(Text("Buyurtma berish 🔸"))
async def add_item(message: types.Message):
    answer = await get_category()
    if answer:
        formatted_text = "\n".join([f"{idx + 1}. {item}" for idx, item in enumerate(answer)])
        ikb = create_number_buttons(len(answer))
        await message.answer(text=f"Quyidagi buyurtmalar mavjud:\n\n{formatted_text}", reply_markup=ikb)
    else:
        await message.answer(text="Hozircha hech qanday buyurtma mavjud emas.")


@dp.callback_query_handler(lambda c: c.data.startswith('inb'))
async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    try:
        number = int(callback_data[3:])
        await bot.answer_callback_query(callback_query.id)
        result = await select_items_by_index(number, "menyu")
        if not result:
            await callback_query.message.edit_text("Ushbu turdagi mahsulotlar topilmadi.")
            return
        rowline = len(result)
        keys = list(result.keys())
        values = list(result.values())
        items = "\n".join([f"{keys[i]} ---- {values[i]} so'm" for i in range(rowline)])
        await callback_query.message.answer(
            items,
            reply_markup=create_food_button(rowline, number)
        )


    except ValueError:
        await callback_query.message.answer("Noto'g'ri formatdagi ma'lumot!")
    except Exception as e:
        print(f"Xatolik: {e}")
        await callback_query.message.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")


@dp.callback_query_handler(lambda c: c.data.startswith('hinb'))
async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    number = int(callback_data[5:])
    await callback_query.answer(text=f"{number} raqam ostidagi tovar tanlandi ")
    orders = await get_user_orders(callback_query.from_user.id)

    formatted_text = "\n".join([
        f"{idx + 1}. {item_name} --- {item_price} so'm, Soni: {item_count}"
        for idx, (item_name, item_price, item_count) in enumerate(orders)
    ])

    lines = formatted_text.splitlines()

    if 1 <= number <= len(lines):
        selected_line = lines[number - 1]
        await callback_query.message.answer(selected_line, reply_markup=create_insert())
    else:
        await callback_query.message.answer("Noto'g'ri raqam tanlandi!")


@dp.callback_query_handler(lambda c: c.data.startswith('add_food'))
async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    item = callback_query.message.text
    pattern = r"(\d+)\.\s*(.*?)\s*---\s*(\d+)\s*so'm,\s*Soni:\s*(\d+)"
    match = re.match(pattern, item.strip())

    item_index = int(match.group(1))
    item_name = match.group(2)
    item_price = int(match.group(3))
    item_count = int(match.group(4))
    new_count = item_count + 1
    await callback_query.message.edit_text(text=f"{item_index}. {item_name} --- {item_price} so'm, Soni: {new_count}",
                                           reply_markup=create_insert())
    await update_item_count(user_id=callback_query.from_user.id,
                            item_name=item_name,
                            count_to_add=new_count)
    await callback_query.answer(text=f"{item_name} ga yana bitta qo'shildi")


@dp.callback_query_handler(lambda c: c.data.startswith('confirm_food'))
async def handle_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(text="O'zgarishlar tasdiqlandi")
    orders = await get_user_orders(callback_query.from_user.id)
    await callback_query.message.delete()

    formatted_text = "\n".join([
        f"{idx + 1}. {item_name} --- {item_price} so'm, Soni: {item_count}"
        for idx, (item_name, item_price, item_count) in enumerate(orders)
    ])
    await callback_query.message.answer(
        text=formatted_text,
        reply_markup=create_history_button(len(orders))
    )


@dp.callback_query_handler(lambda c: c.data.startswith('minus_food'))
async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    item = callback_query.message.text
    pattern = r"(\d+)\.\s*(.*?)\s*---\s*(\d+)\s*so'm,\s*Soni:\s*(\d+)"
    match = re.match(pattern, item.strip())

    item_index = int(match.group(1))
    item_name = match.group(2)
    item_price = int(match.group(3))
    item_count = int(match.group(4))

    if item_count > 0:
        new_count = item_count - 1
        await update_item_count(user_id=callback_query.from_user.id, item_name=item_name,
                                count_to_add=-1)
        await callback_query.answer(text=f"{item_name} dan bitta ayirildi")
    else:
        new_count = item_count
        await callback_query.answer(f"{item_name} dan qolmadi")
    new_text = f"{item_index}. {item_name} --- {item_price} so'm, Soni: {new_count}"
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(
            text=new_text,
            reply_markup=create_insert()
        )


@dp.callback_query_handler(lambda c: c.data.startswith('exit'))
async def handle_callback(callback_query: types.CallbackQuery):
    answer = await get_category()
    await callback_query.message.delete()
    await callback_query.message.answer(text="Yangi ovqat buyurtma berishingiz mumkin ", reply_markup=book_food())


@dp.callback_query_handler(lambda c: c.data.startswith('finb'))
async def handle_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    parts = callback_data[4:].split('_')
    if len(parts) != 2:
        await callback_query.message.answer("Noto'g'ri ma'lumot formati!")
        return

    index = int(parts[0])
    item_number = int(parts[1])

    result = await select_items_by_index(index, "menyu")
    if not result:
        await callback_query.message.answer("Kechirasiz, ushbu turdagi ovqat topilmadi.")
        return

    keys = list(result.keys())
    values = list(result.values())
    total_items = len(keys)

    if total_items == 0:
        await callback_query.message.answer("Hech qanday ovqat mavjud emas.")
        return

    if item_number > total_items or item_number < 1:
        await callback_query.message.answer(
            f"Kechirasiz, noto'g'ri raqam tanlandi. Tanlash mumkin: 1-{total_items}."
        )
        return
    selected_item = keys[item_number - 1]
    selected_price = values[item_number - 1]
    await add_or_update_history(user_id=callback_query.from_user.id,
                                item_name=selected_item,
                                item_price=selected_price
                                )
    await callback_query.answer(
        f"Siz tanladingiz: {selected_item}\nNarxi: {selected_price} so'm"
    )


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)
