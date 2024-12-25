import sqlite3 as sq
import aiosqlite


async def db_start():
    global cur, db
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, user_id INTEGER, number INTEGER, give_item TEXT, count_items INTEGER, overal_price INTEGER)")
    db.commit()


async def create_sum_history():
    global cur, db
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS total_history(id INTEGER PRIMARY KEY, user_id INTEGER, item_name TEXT, item_prise INTEGER, count_items INTEGER, overal_price INTEGER)")
    db.commit()


async def create_table_menyu():
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS menyu(id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, item_price INTEGER, url TEXT, index1 INTEGER)")
    db.commit()


async def create_food_table():
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS food_table(id INTEGER PRIMARY KEY AUTOINCREMENT, table_type_name TEXT)"
    )


async def create_history():
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, item_name TEXT, item_price INT, item_count INT, correct BOOL)")
    db.commit()


async def insert_food_base(item_name, price, index1):
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute("INSERT INTO menyu(item_name, item_price, url, index1) VALUES(?, ?, ?, ?)",
                (item_name, price, 'default_url',
                 index1))
    db.commit()

async def insert_food_table(name):
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        f"INSERT INTO food_table(table_type_name) VALUES(?)", (str(name),))
    db.commit()


async def insert_base(user_id, number):
    existing_user = await check_user(user_id=user_id)
    if existing_user != True:
        cur.execute("INSERT INTO users (user_id, number, give_item, count_items, overal_price) VALUES (?, ?, ?, ?, ?)",
                    (user_id, number, '1', 1, 1))
        db.commit()


async def select_items_by_index(index, table_name):
    global db, cur
    try:
        db = sq.connect("database.db")
        cur = db.cursor()
        query = f"SELECT item_name, item_price FROM {table_name} WHERE index1 = ?"
        cur.execute(query, (index,))
        items = cur.fetchall()
        if items:
            result = {item[0]: item[1] for item in items}
            return result
        else:
            return {}
    except Exception as e:
        print(f"Xato: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if db:
            db.close()

async def get_correct_items(user_id):
    global db, cur
    db = sq.connect("database.db", timeout=5)
    cur = db.cursor()
    cur.execute("SELECT * FROM history WHERE user_id = ? AND correct = 1", (user_id,))
    items = cur.fetchall()
    print(user_id)
    result = ""
    c = 1
    if items:
        for item in items:
            result += f"{c}Tovar Nomi: {item[2]}, Tovar narxi: {item[3]}\n"
            c += 1
    else:
        result = "Ushbu user_id uchun correct qiymati 1 bo'lgan tovarlar topilmadi."
    db.close()
    return result


async def get_category_by_id(item_id, table_name):
    global db, cur
    db = sq.connect("database.db", timeout=5)
    cur = db.cursor()

    result = ""
    tovar_topildi = False

    for i in range(1, item_id + 1):
        cur.execute(f"SELECT * FROM {table_name} WHERE id = ?", (i,))
        item = cur.fetchone()

        if item:
            result += f"{item[0]} Tovar nomi: {item[1]}\n"
            tovar_topildi = True
        else:
            result += f"Товар с ID {i} не найден.\n"
    if not tovar_topildi:
        result = "Tovar yo'q."
    db.close()
    return result


async def get_items_from_menyu():
    async with aiosqlite.connect("database.db") as db:
        async with db.cursor() as cur:
            await cur.execute("SELECT * FROM menyu")
            items = await cur.fetchall()
            if items:
                result = ""
                for item in items:
                    item_id = item[0]
                    item_name = item[1]
                    item_price = item[2]
                    index = item[4]
                    category = await get_category_from_food_table(index)
                    result += f"ID: {item_id} - Tovar nomi: {item_name}, Narxi: {item_price} so'm, Kategoriya: {category}\n"
                return result
            else:
                return None


async def get_category_from_food_table(index1):
    async with aiosqlite.connect("database.db") as db:
        async with db.cursor() as cur:
            await cur.execute("SELECT table_type_name FROM food_table WHERE id = ?", (index1,))
            category = await cur.fetchone()
            if category:
                return category[0]
            else:
                return "Kategoriya mavjud emas"


async def get_item_count(table_name):
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]

    return count


async def check_user(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    existing_user = cur.fetchone()
    return existing_user


async def check_number(user_id):
    cur.execute(
        "SELECT number FROM users WHERE user_id = ?", (int(user_id),)
    )
    phone_number = cur.fetchone()
    return phone_number


async def get_category():
    global db, cur
    db = sq.connect("database.db")
    cur = db.cursor()
    cur.execute(
        "SELECT table_type_name FROM food_table"
    )
    data = cur.fetchall()
    return [row[0] for row in data]


async def get_products_by_index(index):
    try:
        cur.execute("SELECT product_name FROM menu WHERE index1=?", (index,))
        products = cur.fetchall()
        return [product[0] for product in products]
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

async def add_to_total_history(user_id, item_name, item_price, item_count):
    try:
        # Bazaga ulanish
        db = sq.connect("database.db")
        cur = db.cursor()

        # Hisoblash: umumiy narx (overal_price)
        overal_price = item_price * item_count

        # Ma'lumotlarni qo'shish
        query_insert = """
            INSERT INTO total_history (user_id, item_name, item_prise, count_items, overal_price)
            VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(query_insert, (user_id, item_name, item_price, item_count, overal_price))

        # O'zgarishlarni saqlash
        db.commit()
        print("Ma'lumot muvaffaqiyatli qo'shildi!")

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

    finally:
        # Resurslarni yopish
        if cur:
            cur.close()
        if db:
            db.close()

async def get_incorrect_orders(user_id, table_name="history"):
    try:
        db = sq.connect("database.db")
        cur = db.cursor()
        query = f"""
            SELECT id, item_name, item_price, item_count 
            FROM {table_name} 
            WHERE user_id=? AND correct=0
        """
        cur.execute(query, (user_id,))
        result = cur.fetchall()
        if not result:
            return "Sizning yangi buyurtmalaringiz yo'q."
        message = "Buyurtmalar:\n"
        for index, row in enumerate(result, start=1):
            item_name, item_price, item_count = row[1], row[2], row[3]
            message += f"{index}. {item_name} - {item_price} so'm, Soni: {item_count}\n"
        return message
    except Exception as e:
        print(f"Xatolik: {e}")
        return "Xatolik yuz berdi."
    finally:
        if cur:
            cur.close()
        if db:
            db.close()

async def add_or_update_history(user_id, item_name, item_price, correct=0, table_name="history"):
    try:
        db = sq.connect("database.db")
        cur = db.cursor()
        query_check = f"SELECT item_count FROM {table_name} WHERE user_id=? AND item_name=?"
        cur.execute(query_check, (user_id, item_name))
        result = cur.fetchone()
        if result:
            new_count = result[0] + 1
            query_update = f"""
                UPDATE {table_name} 
                SET item_count=?, item_price=?, correct=? 
                WHERE user_id=? AND item_name=?
            """
            cur.execute(query_update, (new_count, item_price, correct, user_id, item_name))
        else:
            query_insert = f"""
                INSERT INTO {table_name} 
                (user_id, item_name, item_price, item_count, correct) 
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(query_insert, (user_id, item_name, item_price, 1, correct))

        db.commit()
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        if cur:
            cur.close()
        if db:
            db.close()


async def get_and_delete_incorrect_orders(user_id, table_name="history"):
    db = None
    cur = None
    try:
        db = sq.connect("database.db")
        cur = db.cursor()
        query_select = f"""
            SELECT id, item_name, item_price, item_count 
            FROM {table_name} 
            WHERE user_id=? AND correct=0
        """
        cur.execute(query_select, (user_id,))
        incorrect_orders = cur.fetchall()
        if incorrect_orders:
            orders_text = "Buyurtmalar:\n"
            for idx, order in enumerate(incorrect_orders, start=1):
                item_name = order[1]
                item_price = order[2]
                item_count = order[3]
                orders_text += f"{idx}. {item_name} - {item_price} so'm, Soni: {item_count}\n"

            query_delete = f"""
                DELETE FROM {table_name} 
                WHERE user_id=? AND correct=0
            """
            cur.execute(query_delete, (user_id,))
            db.commit()

            return orders_text
        else:
            return "Noto'g'ri buyurtmalar mavjud emas."

    except Exception as e:
        print(f"Xatolik: {e}")
        return "Xatolik yuz berdi."

    finally:
        if cur:
            cur.close()
        if db:
            db.close()


async def get_user_orders(user_id, table_name="history"):
    db = None
    cur = None
    try:
        # Bazaga ulanish
        db = sq.connect("database.db")
        cur = db.cursor()

        # Ma'lumotlarni tanlash
        query = f"""
            SELECT item_name, item_price, item_count 
            FROM {table_name} 
            WHERE user_id=?
        """
        cur.execute(query, (user_id,))
        result = cur.fetchall()
        return result
    except Exception as e:
        print(f"Xatolik: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if db:
            db.close()
async def update_item_count(user_id, item_name, count_to_add, table_name="history"):
    try:
        db = sq.connect("database.db")
        cur = db.cursor()
        query_check = f"SELECT item_count FROM {table_name} WHERE user_id=? AND item_name=?"
        cur.execute(query_check, (user_id, item_name))
        result = cur.fetchone()
        if result:
            new_count =  count_to_add
            query_update = f"""
                UPDATE {table_name} 
                SET item_count=? 
                WHERE user_id=? AND item_name=?
            """
            cur.execute(query_update, (new_count, user_id, item_name))
        else:
            new_count = count_to_add
            query_insert = f"""
                INSERT INTO {table_name} 
                (user_id, item_name, item_count) 
                VALUES (?, ?, ?)
            """
            cur.execute(query_insert, (user_id, item_name, new_count))
        db.commit()
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        if cur:
            cur.close()
        if db:
            db.close()
