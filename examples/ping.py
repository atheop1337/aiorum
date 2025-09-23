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

@bot.command("/ping")
async def ping(message: Message):
    await message.reply(content="🙄 Pong!")


async def main() -> None:
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