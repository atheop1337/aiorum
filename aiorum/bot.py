from __future__ import annotations

import asyncio
import aiohttp
import logging

from .utils.token import validate_token

from .api.api_client import ApiClient
from .api.manager import Manager
from .dispatcher import Dispatcher

from .api.api_references import ApiReference

from .models.models import Discussion

class Bot:
    def __init__(self, token: str, bot_id: int, discussion_id: int, api_reference: ApiReference, session: aiohttp.ClientSession | None = None) -> None:
        validate_token(token)

        self._token = token
        self._bot_id = bot_id
        self._discussion_id = discussion_id

        self.api_reference = api_reference

        self.api_client = ApiClient(token, session=session)
        self.manager = Manager(self.api_client, discussion_id=discussion_id, bot_id=self._bot_id, api_reference=self.api_reference)

        self.dispatcher = Dispatcher()
        self._last_discussion_id: str | None = None

    def command(self, name: str):
        return self.dispatcher.command(name)

    def on_new_discussion(self, func):
        return self.dispatcher.on_new_discussion(func)

    def on_new_message(self, func):
        return self.dispatcher.on_new_message(func)

    async def start(self):
        logging.info("Starting bot...")
        async with ApiClient(self.token) as client:
            self.api_client = client
            self.manager = Manager(client, self.discussion_id, self.bot_id, self.api_reference)

            await self._listen_loop()

    async def _listen_loop(self):
        logging.info("Listening for new posts and discussions...")
        while True:
            try:
                new_posts = await self.manager.fetch_new_posts()
                for post_id in new_posts:
                    msg = await self.manager.parse_post(post_id)
                    if not msg or not msg.message:
                        continue
                    logging.info(f"New message: {msg.message}")
                    await self.dispatcher.handle_message(msg, self)

                discussion: Discussion | None = await self.manager.fetch_new_discussion()
                if discussion:
                    logging.info(f"New discussion detected: {discussion.title}")
                    await self.dispatcher.handle_new_discussion(discussion)

                await asyncio.sleep(5)

            except asyncio.TimeoutError:
                logging.warning("Timeout in listen loop (network issue?)")
            except Exception as e:
                logging.exception(f"Error in listen loop: {e}")

    def run(self):
        asyncio.run(self.start())

    @property
    def token(self) -> str:
        return self._token

    @property
    def bot_id(self) -> int:
        return self._bot_id

    @property
    def discussion_id(self) -> int:
        return self._discussion_id

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.session

    async def close(self) -> None:
        if self.api_client and self.api_client.session and not self.api_client.session.closed:
            await self.api_client.session.close()