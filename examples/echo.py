import asyncio
import logging

from aiorum import Bot
from aiorum.api.api_references import ApiReference
from aiorum.models.models import Message

from dotenv import load_dotenv
from os import getenv


load_dotenv()

bot = Bot(
    token=getenv("TOKEN"),
    bot_id=8033,
    discussion_id=18508,
    api_reference=ApiReference("https://forum.wayzer.ru/api/")
)

@bot.on_new_message
async def echo(message: Message):
    await message.like()
    await message.reply(content=f"{message.message}!")


async def main():
    try:
        await bot.start()
    finally:
        await bot.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
    asyncio.run(main())