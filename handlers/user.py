from aiogram import Router, F
from aiogram.types import Message
from database.db import add_user, get_user_role
from config import SUPERADMIN_ID
from keyboards.reply import user_main_menu,superadmin_menu,admin_main_menu
from utils.product_utils import get_all_products
from keyboards.inline import product_inline_buttons
import sqlite3
from config import DB_PATH

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    tg_id = message.from_user.id
    full_name = message.from_user.full_name

    # Foydalanuvchini bazaga qo‘shamiz
    add_user(tg_id=tg_id, full_name=full_name)

    # Agar bu superadmin bo‘lsa, uni roli yangilanadi
    if tg_id == SUPERADMIN_ID:
        from sqlite3 import connect
        conn = connect("data/shop.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = 'superadmin' WHERE tg_id = ?", (tg_id,))
        conn.commit()
        conn.close()

    # Uning rolini aniqlaymiz
    role = get_user_role(tg_id)

    # Javob yuboramiz
    if role == "superadmin":
        await message.answer("👑 Xush kelibsiz, Superadmin!",reply_markup=superadmin_menu)
    elif role == "admin":
        await message.answer("🛠 Salom, admin! Panelga xush kelibsiz.",reply_markup=admin_main_menu)
    else:
        await message.answer(
        "🛍 Xush kelibsiz! Siz mahsulotlar bilan tanishishingiz mumkin.",
        reply_markup=user_main_menu
    )




@router.message(F.text == "🛍 Mahsulotlar")
async def show_products(message: Message):
    products = get_all_products()

    if not products:
        await message.answer("Hozircha mahsulotlar mavjud emas.")
        return

    for product in products:
        product_id, name, desc, price, image = product
        text = f"<b>{name}</b>\n\n{desc}\n\n💰 Narxi: {price} so'm"

        if image:
            await message.answer_photo(photo=image, caption=text, reply_markup=product_inline_buttons(product_id))
        else:
            await message.answer(text, reply_markup=product_inline_buttons(product_id))



@router.message(F.text == "🛒 Savatcham")
async def show_cart(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON p.id = c.product_id
        WHERE c.user_id = ?
    """, (user_id,))
    items = cursor.fetchall()
    conn.close()

    if not items:
        await message.answer("🛒 Sizning savatchangiz bo‘sh.")
        return

    total = 0
    text = "<b>🛍 Sizning savatchangiz:</b>\n\n"
    for name, price, qty in items:
        total += price * qty
        text += f"{name} — {qty} x {price} = {qty * price} so‘m\n"

    text += f"\n<b>Umumiy:</b> {total} so‘m\n\n✅ Buyurtma berish uchun /order ni bosing."
    await message.answer(text)



@router.message(F.text == "/order")
async def make_order(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Savatdagi mahsulotlar
    cursor.execute("""
        SELECT product_id, quantity FROM cart WHERE user_id = ?
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        await message.answer("❗️Savatchangiz bo‘sh.")
        return

    # Umumiy narx va mahsulotlar ro‘yxatini to‘plab olamiz
    total = 0
    product_list_text = ""
    for product_id, qty in cart_items:
        cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
        name, price = cursor.fetchone()
        total += price * qty
        product_list_text += f"{name} x{qty}, "

    # Order qo‘shamiz
    cursor.execute("""
        INSERT INTO orders (user_id, product_list, total_price)
        VALUES (?, ?, ?)
    """, (user_id, product_list_text.strip(', '), total))

    # Savatni tozalaymiz
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Buyurtmangiz qabul qilindi!\n\n<b>Umumiy narx:</b> {total} so‘m")

    # Adminlarga xabar yuborish (ixtiyoriy)
    # for admin_id in [list of admin IDs]:
    #     await bot.send_message(admin_id, f"Yangi buyurtma:\n{product_list_text} - {total} so‘m")
