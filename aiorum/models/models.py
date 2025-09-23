from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.manager import Manager

class NotAttachedToManager(Exception):
    pass

@dataclass
class Message:
    post_id: str
    message: str
    reply_id: Optional[str]
    user_id: Optional[str]
    username: Optional[str]
    _manager: Optional["Manager"] = None

    async def edit(self, content: str):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.edit_post(content, int(self.post_id))

    async def delete(self):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.delete_post(int(self.post_id))

    async def like(self):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.like_post(int(self.post_id))

    async def answer(self, content:str):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.create_post(content)

    async def reply(self, content: str):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.create_post(content, reply=True, reply_to=self)

    async def parse_user(self):
        if not self._manager:
            raise NotAttachedToManager("Message is not attached to a manager")
        return await self._manager.parse_user(int(self.user_id))


@dataclass
class User:
    username: str
    display_name: str
    slug: str
    joined_at: Optional[str]
    discussions_count: int
    comments_count: int
    last_seen_at: Optional[str]
    steam_id: str
    bio: str
    rank: str


@dataclass
class Discussion:
    id: str
    title: str
    slug: str
    comments_count: int
    participants_count: int
    created_at: Optional[str]
    updated_at: Optional[str]
    content: str
    tag: str
    first_post_id: str
    raw: dict
    _manager: Optional["Manager"] = None

    async def reply(self, content: str):
        if not self._manager:
            raise NotAttachedToManager("Discussion is not attached to a manager")
        old_discussion_id = self._manager.discussion_id
        self._manager.discussion_id = int(self.id)

        try:
            return await self._manager.create_post(content)
        finally:
            self._manager.discussion_id = old_discussion_id

    async def edit_first_post(self, content: str):
        if not self._manager:
            raise NotAttachedToManager("Discussion is not attached to a manager")
        return await self._manager.edit_post(content, int(self.first_post_id))

    async def delete(self):
        if not self._manager:
            raise NotAttachedToManager("Discussion is not attached to a manager")
        return await self._manager.delete_discussion(int(self.id))

