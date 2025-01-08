import asyncio
import logging
import sys

from aiogram import Dispatcher, types, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import handle_document, handle_other, handle_text
from settings import BOT_TOKEN

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    await message.reply("Отправьте документ, чтобы обработать его.")


@dp.message(F.document)
async def document_handler(message: types.Message):
    await handle_document(message)

@dp.message(F.text)
async def text_handler(message: types.Message):
    await handle_text(message)

@dp.message()
async def other_handler(message: types.Message):
    await handle_other(message)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
