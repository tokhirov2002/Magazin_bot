from aiogram import Router, F
from aiogram.types import Message
from config import SUPERADMIN_ID
from keyboards.reply import superadmin_menu
import sqlite3
from config import DB_PATH

router = Router()

@router.message(F.text == "/superadmin")
async def open_superadmin_panel(message: Message):
    if message.from_user.id != SUPERADMIN_ID:
        await message.answer("⛔ Siz Superadmin emassiz.")
        return
    await message.answer("👑 Superadmin paneliga xush kelibsiz!", reply_markup=superadmin_menu)


@router.message(F.text == "➕ Admin qo‘shish")
async def add_admin(message: Message):
    await message.answer("Yangi adminning Telegram ID raqamini kiriting:")

    @router.message()
    async def catch_admin_id(msg: Message):
        if not msg.text.isdigit():
            await msg.answer("❗️Faqat raqam kiriting.")
            return

        new_admin_id = int(msg.text)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = 'admin' WHERE tg_id = ?", (new_admin_id,))
        conn.commit()
        conn.close()
        await msg.answer(f"✅ <code>{new_admin_id}</code> admin sifatida belgilandi.", reply_markup=superadmin_menu)
        router.message.handlers.pop()  # faqat 1 marta ishlashi uchun

@router.message(F.text == "❌ Adminni o‘chirish")
async def remove_admin(message: Message):
    await message.answer("O‘chiriladigan adminning Telegram ID raqamini kiriting:")

    @router.message()
    async def catch_remove_id(msg: Message):
        if not msg.text.isdigit():
            await msg.answer("❗️Faqat raqam kiriting.")
            return

        remove_id = int(msg.text)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = 'user' WHERE tg_id = ?", (remove_id,))
        conn.commit()
        conn.close()
        await msg.answer(f"✅ <code>{remove_id}</code> endi oddiy foydalanuvchi.", reply_markup=superadmin_menu)
        router.message.handlers.pop()



@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    total_admins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    conn.close()

    await message.answer(
        f"📊 Statistika:\n\n👥 Foydalanuvchilar: {total_users}\n🛠 Adminlar: {total_admins}\n📦 Mahsulotlar: {total_products}"
    )

@router.message(F.text == "👥 Adminlar ro‘yxati")
async def show_admin_list(message: Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, full_name FROM users WHERE role = 'admin'")
    admins = cursor.fetchall()
    conn.close()

    if not admins:
        await message.answer("⛔ Hozirda hech qanday admin yo‘q.")
        return

    text = "🛠 Adminlar ro‘yxati:\n\n"
    for admin in admins:
        text += f"🆔 {admin[0]} — {admin[1]}\n"

    await message.answer(text)
