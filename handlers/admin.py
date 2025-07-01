from aiogram import Router, F
from aiogram.types import Message
from database.db import get_user_role
from keyboards.reply import admin_main_menu
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from keyboards.inline import order_action_buttons
from aiogram.types import CallbackQuery
import sqlite3
from datetime import datetime
from config import DB_PATH


router = Router()

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    tg_id = message.from_user.id
    role = get_user_role(tg_id)

    if role != "admin" and role != "superadmin":
        await message.answer("❌ Sizda ruxsat yo'q.")
        return

    await message.answer("🔧 Admin paneliga xush kelibsiz!", reply_markup=admin_main_menu)


def add_timestamp_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN timestamp TEXT DEFAULT (datetime('now', 'localtime'))")
        conn.commit()
        print("timestamp ustuni qo‘shildi.")
    except sqlite3.OperationalError:
        print("timestamp ustuni allaqachon mavjud yoki qo‘shib bo‘lindi.")
    conn.close()

add_timestamp_column()

# Mahsulot qo‘shish holatlari
class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()
    image = State()

# Tugmani bosganda boshlaymiz
@router.message(F.text == "➕ Mahsulot qo‘shish")
async def start_adding_product(message: Message, state: FSMContext):
    await message.answer("📝 Mahsulot nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)

@router.message(AddProduct.name)
async def product_name_step(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("✏️ Tavsifini kiriting:")
    await state.set_state(AddProduct.description)

@router.message(AddProduct.description)
async def product_description_step(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Narxini kiriting (faqat raqam):")
    await state.set_state(AddProduct.price)

@router.message(AddProduct.price)
async def product_price_step(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗️Faqat raqam kiriting.")
        return
    await state.update_data(price=int(message.text))
    await message.answer("🏷 Kategoriyasini kiriting:")
    await state.set_state(AddProduct.category)

@router.message(AddProduct.category)
async def product_category_step(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("📷 Mahsulot rasmini yuboring (yoki rasm joylamasangiz, 'yo'q' deb yozing):")
    await state.set_state(AddProduct.image)



@router.message(AddProduct.image)
async def product_image_step(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
    elif message.text.lower() in ["yo'q", "yoq", "yoqmas"]:
        file_id = None
    else:
        await message.answer("❗️Rasm yuboring yoki 'yo'q' deb yozing.")
        return

    # Bazaga yozish
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, description, price, category, image)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["description"],
        data["price"],
        data["category"],
        file_id
    ))
    conn.commit()
    conn.close()

    await message.answer("✅ Mahsulot rasmi bilan qo‘shildi!", reply_markup=admin_main_menu)
    await state.clear()



@router.message(F.text == "📦 Buyurtmalar ro‘yxati")
async def view_orders(message: Message):
    tg_id = message.from_user.id
    role = get_user_role(tg_id)

    if role not in ["admin", "superadmin"]:
        await message.answer("⛔ Sizda bu amal uchun ruxsat yo‘q.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, u.full_name, o.product_list, o.total_price, o.status
        FROM orders o
        JOIN users u ON u.tg_id = o.user_id
        ORDER BY o.id DESC
        LIMIT 10
    """)
    orders = cursor.fetchall()
    conn.close()

    if not orders:
        await message.answer("📭 Buyurtmalar mavjud emas.")
        return

    for order in orders:
        order_id, full_name, product_list, total_price, status = order
        text = (
            f"🆔 Buyurtma ID: {order_id}\n"
            f"👤 Foydalanuvchi: {full_name}\n"
            f"📋 Mahsulotlar: {product_list}\n"
            f"💵 Narxi: {total_price} so‘m\n"
            f"🕒 Sana: {timestamp}\n"
            f"📦 Holat: {status}\n"
        )
        await message.answer(text, reply_markup=order_action_buttons(order_id))





@router.callback_query(F.data.startswith("order_confirm"))
async def order_confirm(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id
    role = get_user_role(tg_id)

    if role not in ["admin", "superadmin"]:
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'Tasdiqlangan' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    await callback.answer("✅ Buyurtma tasdiqlandi.", show_alert=True)
    await callback.message.edit_reply_markup()  # Inline tugmalarni olib tashlash

@router.callback_query(F.data.startswith("order_reject"))
async def order_reject(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id
    role = get_user_role(tg_id)

    if role not in ["admin", "superadmin"]:
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'Rad etilgan' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    await callback.answer("❌ Buyurtma rad etildi.", show_alert=True)
    await callback.message.edit_reply_markup()

@router.callback_query(F.data.startswith("order_delete"))
async def order_delete(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id
    role = get_user_role(tg_id)

    if role not in ["admin", "superadmin"]:
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    await callback.answer("🗑 Buyurtma o‘chirildi.", show_alert=True)
    await callback.message.delete()