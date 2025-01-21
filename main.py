import asyncio
import logging
import sys
import aiosqlite
import datetime

from os import getenv


from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from just_token import The_token

TOKEN = The_token

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

async def add_to_database(telegram_id, username):    
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, username TEXT, date TEXT)')
        cursor = await db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        data = await cursor.fetchone()
        if data is not None:
            return
    date = f'{datetime.date.today()}'
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute("INSERT INTO users (telegram_id, username, date) VALUES(?, ?, ?)", (telegram_id, username, date))

        await db.commit()

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Hello!")
    telegram_id = message.from_user.id
    username = message.from_user.username
    if username is None:
        username = 'None'
    await add_to_database(telegram_id, username)


@dp.message()
async def echo_handler(message: Message):
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')