from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Oddiy foydalanuvchi uchun tugmalar
user_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Mahsulotlar")],
        [KeyboardButton(text="🛒 Savatcham")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="🧾 Profilim")],
        [KeyboardButton(text="ℹ️ Yordam")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Kerakli bo‘limni tanlang"
)


# Admin uchun menyu
admin_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Mahsulot qo‘shish")],
        [KeyboardButton(text="📦 Buyurtmalar ro‘yxati")],
        [KeyboardButton(text="🔙 Asosiy menyuga")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Admin paneli"
)



superadmin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Admin qo‘shish"), KeyboardButton(text="❌ Adminni o‘chirish")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Adminlar ro‘yxati")],
        # [KeyboardButton(text="🔙 Menyuga qaytish")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Superadmin panel"
)
