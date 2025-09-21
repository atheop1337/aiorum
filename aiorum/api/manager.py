import asyncio
import json
import logging
from typing import Optional

from ..utils.html_stripper import HTMLStripper

from ..models.models import Message, User, Discussion

from .api_references import ApiReference

HTMLStripper = HTMLStripper()
KNOWN_POSTS_FILE = "known_posts.json"
KNOWN_DISCUSSIONS_FILE = "known_discussions.json"


class Manager:
    def __init__(self, api_client, discussion_id: int, bot_id: int, api_reference: ApiReference):
        self.api_client = api_client
        self.discussion_id = discussion_id
        self.bot_id = bot_id
        self.api_reference = api_reference
        self.known_posts: set = self._load_known_posts()
        self.known_discussions: set = self._load_known_discussions()

    def _load_known_posts(self) -> set:
        try:
            with open(KNOWN_POSTS_FILE, "r") as file:
                data = json.load(file)
                return set(data)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("No known posts file found, starting fresh.")
            empty = set()
            with open(KNOWN_POSTS_FILE, "w") as file:
                json.dump([], file)
            return empty

    def _save_known_posts(self):
        with open(KNOWN_POSTS_FILE, "w") as file:
            json.dump(list(self.known_posts), file)

    def _load_known_discussions(self) -> set:
        try:
            with open(KNOWN_DISCUSSIONS_FILE, "r") as file:
                data = json.load(file)
                return set(data)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("No known discussions file found, starting fresh.")
            empty = set()
            with open(KNOWN_DISCUSSIONS_FILE, "w") as file:
                json.dump([], file)
            return empty

    def _save_known_discussions(self):
        with open(KNOWN_DISCUSSIONS_FILE, "w") as file:
            json.dump(list(self.known_discussions), file)

    async def create_post(self, content: str, reply: bool = False, reply_to: Optional[Message] = None, discussion_id: int = None) -> Message:
        if reply and reply_to:
            username = reply_to.username
            post_id = reply_to.post_id
            content = f'@"{username}"#p{post_id} {content}'

        url = self.api_reference.posts
        data = {
            "data": {
                "type": "posts",
                "attributes": {"content": content},
                "relationships": {
                    "discussion": {
                        "data": {"type": "discussions", "id": discussion_id or self.discussion_id}
                    }
                },
            }
        }

        result = await self.api_client.request("POST", url, data=data)

        if result.get("status") != 201:
            return result

        logging.info("Successfully created a new post.")

        raw = result["json"]
        post_data = raw.get("data", {})
        included = raw.get("included", [])

        content_html = post_data.get("attributes", {}).get("contentHtml", "")
        message, reply_id = HTMLStripper.strip_html_and_extract_reply_id(content_html)

        user_id = post_data.get("relationships", {}).get("user", {}).get("data", {}).get("id")
        username = None
        for item in included:
            if item.get("type") == "users" and item.get("id") == user_id:
                username = item.get("attributes", {}).get("username")
                break

        return Message(
            post_id=post_data.get("id"),
            message=message,
            reply_id=reply_id,
            user_id=user_id,
            username=username,
            _manager=self
        )

    async def edit_post(self, content: str, post_id: int) -> dict:
        url = self.api_reference.post(post_id)
        data = {
            "data": {
                "type": "posts",
                "id": post_id,
                "attributes": {
                    "content": content
                }
            }
        }
        return await self.api_client.request("PATCH", url, data=data)

    async def edit_bio(self, content: str) -> dict:
        url = self.api_reference.user(self.bot_id)
        data = {
            "data": {
                "type": "users",
                "id": self.bot_id,
                "attributes": {"bio": content}
            }
        }
        return await self.api_client.request("PATCH", url, data=data)

    async def like_post(self, post_id: int) -> dict:
        url = self.api_reference.post(post_id)
        data = {
            "data": {
                "type": "posts",
                "attributes": {
                    "isLiked": True
                },
                "id": post_id
            }
        }
        return await self.api_client.request("PATCH", url, data=data)

    async def delete_post(self, post_id: int) -> dict:
        url = self.api_reference.post(post_id)
        data = {
            "data": {
                "type": "posts",
                "id": str(post_id),
                "attributes": {
                    "isHidden": True
                }
            }
        }
        return await self.api_client.request("PATCH", url, data=data)

    async def fetch_new_posts(self, max_retries: int = 3) -> list[str]:
        url = self.api_reference.discussion(self.discussion_id)

        for attempt in range(1, max_retries + 1):
            result = await self.api_client.request("GET", url)

            if result.get("status") != 200:
                logging.warning(f"Attempt {attempt}: Failed to fetch discussion")
                await asyncio.sleep(2)
                continue

            posts = (
                result.get("json", {})
                .get("data", {})
                .get("relationships", {})
                .get("posts", {})
                .get("data", [])
            )
            new_posts = [p["id"] for p in posts if p["id"] not in self.known_posts]

            if new_posts:
                self.known_posts.update(new_posts)
                self._save_known_posts()
                return new_posts

            return []

        return []

    async def parse_post(self, post_id: str) -> Optional[Message]:
        url = self.api_reference.post(int(post_id))
        result = await self.api_client.request("GET", url)
        data = result.get("json", {})
        post_data = data.get("data", {})

        message, reply_id = HTMLStripper.strip_html_and_extract_reply_id(post_data.get("attributes", {}).get("contentHtml", ""))

        username = None
        for item in data.get("included", []):
            if item.get("type") == "users":
                username = item.get("attributes", {}).get("username")
                break

        return Message(
            post_id=post_id,
            message=message,
            reply_id=reply_id,
            user_id=post_data.get("relationships", {}).get("user", {}).get("data", {}).get("id"),
            username=username,
            _manager=self
        )

    async def parse_user(self, user_id: int) -> Optional[User]:
        url = self.api_reference.user(user_id)
        result = await self.api_client.request("GET", url)

        data = result.get("json", {})
        attributes = data.get("data", {}).get("attributes", {})

        return User(
            username=attributes.get("username"),
            display_name=attributes.get("displayName"),
            slug=attributes.get("slug"),
            joined_at=attributes.get("joinTime"),
            discussions_count=attributes.get("discussionCount"),
            comments_count=attributes.get("commentCount"),
            last_seen_at=attributes.get("lastSeenAt") or "Последний заход приватный",
            steam_id=attributes.get("SteamAuth", {}).get("identifier"),
            bio=attributes.get("bio"),
            rank = (data.get("included") or [{}])[0].get("attributes", {}).get("nameSingular", "Ранга нет")
        )

    async def parse_discussion(self, discussion_id: int) -> Optional[Discussion]:
        url = self.api_reference.discussion(discussion_id)
        result = await self.api_client.request("GET", url)

        data = result.get("json", {})
        discussion = data.get("data", {})
        attributes = discussion.get("attributes", {})
        relationships = discussion.get("relationships", {})
        included = data.get("included", [])

        content, reply_id = None, None
        if included:
            first_post = next((i for i in included if i.get("type") == "posts"), None)
            if first_post:
                raw_html = first_post.get("attributes", {}).get("contentHtml", "")
                content, reply_id = HTMLStripper.strip_html_and_extract_reply_id(raw_html)

        return Discussion(
            id=discussion.get("id"),
            title=attributes.get("title"),
            slug=attributes.get("slug"),
            comments_count=attributes.get("commentCount"),
            participants_count=attributes.get("participantCount"),
            created_at=attributes.get("createdAt"),
            updated_at=attributes.get("lastPostedAt"),
            content=content,
            tag=relationships["tags"]["data"][0]["id"],
            first_post_id=included[0]["id"],
            raw=data,
            _manager=self
        )

    async def get_last_discussion(self) -> Optional[Discussion]:
        url = self.api_reference.discussions_last
        result = await self.api_client.request("GET", url)
        data = result.get("json", {})
        discussion = data["data"][0]

        return await self.parse_discussion(discussion["id"])

    async def fetch_new_discussion(self) -> Optional[Discussion]:
        discussion = await self.get_last_discussion()
        if not discussion:
            return None

        if discussion.id in self.known_discussions:
            return None

        self.known_discussions.add(discussion.id)
        self._save_known_discussions()
        return discussion

