import asyncio
import logging

from aiorum import Bot
from aiorum.api.api_references import ApiReference
from aiorum.models.models import Discussion, Message

from dotenv import load_dotenv
from os import getenv

load_dotenv()

bot = Bot(
    token=getenv("TOKEN") or "YOUR_TOKEN", # str: Your token (flarum_remember cookie)
    bot_id=1337, # int: Your account ID
    discussion_id=1337, # int: Discussion id where the bot will work
    api_reference=ApiReference("https://forum.example.com/api/")
    # str: API base URL (your forum link + "/api/")
)


# New command
@bot.command("/example")
async def example(message: Message):
    # Dataclass Message contains the following fields:
    print(
        message.post_id,
        message.message,
        message.reply_id, # None if there is no reply
        message.user_id,
        message.username
    )
    # Basic methods
    await message.answer("Answer")
    await message.reply("Reply")
    await message.like() # Toggle like/unlike

    user_data = await message.parse_user()
    print(
        user_data.username,
        user_data.display_name,
        user_data.slug,
        user_data.joined_at,
        user_data.discussions_count,
        user_data.last_seen_at, # None if hide
        user_data.steam_id, # None if not linked
        user_data.bio,
        user_data.rank # "No rank" if no rank
    )

    # Admin only methods
    await message.edit("Edited")
    await message.delete()

    # Also you can store created message and call methods on it
    # For messages you created yourself, edit/delete/like do not require admin rights
    msg = await message.answer("New message")
    await msg.edit("Updated message")
    await msg.answer("Answer to self")
    await msg.reply("reply to self")
    await msg.delete()
    await msg.like() # Toggle like/unlike

    # NOTE: calling like() on a liked post will remove the like


# EVENT: On new message
@bot.on_new_message
async def greetings(message: Message):
    await message.reply(f"Hello, {message.username}! Do you know that your ID is {message.user_id}?")
    # Works the same as above, but triggers automatically
    # when a new message is posted in the followed discussion


# EVENT: On new discussion
@bot.on_new_discussion
async def notify(discussion: Discussion):
    print(
        discussion.id,
        discussion.title,
        discussion.slug,
        discussion.comments_count,
        discussion.participants_count,
        discussion.created_at,
        discussion.updated_at,
        discussion.content, # Content of first post (TS)
        discussion.tag, # e.g. 7 for Off-topic
        discussion.first_post_id,
        discussion.raw # Raw json
    )

    await discussion.reply("Hi there!")                 # Reply to the new discussion
    await discussion.edit_first_post("Edited TS post!") # Edit the first post


async def worker():
    """
    Example usage of Manager outside decorators.
    Demonstrates:
    - Creating, editing, deleting, and liking posts
    - Fetching and parsing users
    - Fetching and parsing discussions
    - Detecting new posts and discussions
    """
    # ======== POSTS ========

    # Fetch an existing post by ID
    post_id = 1337
    post_data = await bot.manager.parse_post(post_id)
    print("Post:", post_data.post_id, post_data.message, post_data.username) # post_data.etc..

    # Create a reply to an existing post
    await bot.manager.create_post(
        content="This is a reply to your post!",
        reply=True,
        reply_to=post_data,
        discussion_id=1337
    )

    # Create a new post without reply
    await bot.manager.create_post(
        content="This is a standalone post",
        discussion_id=1337
    )

    # Edit a post
    await bot.manager.edit_post("Edited content of the post", post_id=1337)

    # Delete a post
    await bot.manager.delete_post(post_id=1337)

    # Like a post
    await bot.manager.like_post(post_id=1337)

    # ======== USERS ========

    # Fetch user data
    user = await bot.manager.parse_user(user_id=8033)
    print("User:", user.username, user.display_name, user.bio, user.rank) # user.etc..

    # Edit bot profile bio
    await bot.manager.edit_bio("Updated profile bio!")

    # ======== DISCUSSIONS ========

    # Fetch the latest discussion
    last_discussion = await bot.manager.get_last_discussion()
    print("Latest discussion:", last_discussion.id, last_discussion.title)

    # Fetch a new discussion if available
    new_discussion = await bot.manager.fetch_new_discussion()
    if new_discussion:
        print("New discussion detected:", new_discussion.id, new_discussion.title)

    # Parse a specific discussion
    discussion = await bot.manager.parse_discussion(discussion_id=18448)
    print("Discussion:", discussion.title, discussion.comments_count, discussion.participants_count)

    # ======== NEW POSTS ========

    # Detect new posts
    new_posts = await bot.manager.fetch_new_posts()
    if new_posts:
        print("New posts detected:", new_posts)


# Entry point
async def main():
    try:
        await bot.start()
    finally:
        await bot.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, # INFO or DEBUG. (DEBUG for framework analysis)
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
    asyncio.run(main())
