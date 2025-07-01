from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def product_inline_buttons(product_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Savatchaga", callback_data=f"add_to_cart:{product_id}")]
        ]
    )



def order_action_buttons(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"order_confirm:{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"order_reject:{order_id}")
            ],
            [
                InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"order_delete:{order_id}")
            ]
        ]
    )