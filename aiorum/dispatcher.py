from __future__ import annotations

import logging
import inspect
from typing import Callable, Awaitable, Any

class Dispatcher:
    def __init__(self):
        self._commands: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._new_discussion_handlers: list[Callable[..., Awaitable[Any]]] = []
        self._new_message_handlers: list[Callable[..., Awaitable[Any]]] = []

    def command(self, name: str):
        def decorator(func: Callable[..., Awaitable[Any]]):
            self._commands[name] = func
            return func
        return decorator

    def on_new_discussion(self, func: Callable[..., Awaitable[Any]]):
        self._new_discussion_handlers.append(func)
        return func

    def on_new_message(self, func: Callable[..., Awaitable[Any]]):
        self._new_message_handlers.append(func)
        return func

    async def _call_handler(self, handler: Callable[..., Any], msg, bot):
        try:
            sig = inspect.signature(handler)
            params_count = len(sig.parameters)
        except Exception:
            params_count = 1

        if params_count <= 1:
            call_args = (msg,)
        else:
            call_args = (msg, bot)

        try:
            result = handler(*call_args)
            if inspect.isawaitable(result):
                await result
        except Exception:
            logging.exception("Error while running handler %s", getattr(handler, "__name__", repr(handler)))

    async def handle_message(self, msg, bot):
        if int(msg.user_id) == int(bot.bot_id):
            logging.info("Skipping my own message..")
            return

        logging.info("Handling message")

        parts = (msg.message or "").split()
        if not parts:
            return
        cmd = parts[0]
        if cmd in self._commands:
            await self._call_handler(self._commands[cmd], msg, bot)
            return

        for handler in list(self._new_message_handlers):
            await self._call_handler(handler, msg, bot)

    async def handle_new_discussion(self, discussion):
        logging.info(f"Handling new discussion: {getattr(discussion, 'id', '?')}")
        for handler in list(self._new_discussion_handlers):
            await self._call_handler(handler, discussion, None)
