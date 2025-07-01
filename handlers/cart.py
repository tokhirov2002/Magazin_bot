from aiogram import Router, F
from aiogram.types import CallbackQuery
import sqlite3
from config import DB_PATH

router = Router()

@router.callback_query(F.data.startswith("add_to_cart"))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Agar savatchada bo‘lsa, quantity +1
    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE cart SET quantity = quantity + 1
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (?, ?, 1)
        """, (user_id, product_id))

    conn.commit()
    conn.close()

    await callback.answer("🛒 Savatchaga qo‘shildi!", show_alert=False)
