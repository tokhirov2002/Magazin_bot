from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging
from handlers import user,admin,superadmin,cart  # yangi import

from config import BOT_TOKEN
from database.db import create_tables

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Bot ishga tushganida bazani yaratish
async def on_startup():
    create_tables()
    print("✅ Baza tayyor!")


async def main():
    await on_startup()
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(superadmin.router)
    dp.include_router(cart.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
