import asyncio
import logging

from aiorum import Bot
from aiorum.api.api_references import ApiReference
from aiorum.models.models import Discussion

from dotenv import load_dotenv
from os import getenv


load_dotenv()

bot = Bot(
    token=getenv("TOKEN"),
    bot_id=8033,
    discussion_id=18508,
    api_reference=ApiReference("https://forum.wayzer.ru/api/")
)

@bot.on_new_discussion
async def hider(discussion: Discussion):
    await discussion.edit_first_post("Oopsie!")


async def main() -> None:
    try:
        await bot.start()
    finally:
        await bot.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
    asyncio.run(main())
