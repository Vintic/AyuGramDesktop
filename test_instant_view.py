import asyncio
import os
from telethon import TelegramClient, functions, types

# Load secrets from .env file natively
env_vars = {}
try:
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()
except FileNotFoundError:
    print("Error: .env file not found. Please copy .env.example to .env and add your API keys.")
    exit(1)

api_id = int(env_vars.get("API_ID", 0))
api_hash = env_vars.get("API_HASH", "")

if not api_id or not api_hash:
    print("Error: API_ID or API_HASH missing from .env")
    exit(1)

client = TelegramClient('test_session', api_id, api_hash)

async def main():
    await client.start()
    print("Logged in!")

    target_chat = await client.get_input_entity('me')
    original_url = "https://999.md/ro/104861743"
    iv_url = f"https://t.me/iv?rhash=1b047efddd1e39&url={original_url}"
    import random

    # IDEA 1: Physical replacement
    print("Sending Idea 1 (Physical Replacement)...")
    text1 = f"Idea 1 (Physical): Here is a test link! {iv_url}"
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text1,
        random_id=random.randint(1000000, 9999999),
        no_webpage=False
    ))

    # IDEA 2: Markdown-style URL Entity over the original URL text
    print("Sending Idea 2 (Entity over original URL)...")
    text2 = f"Idea 2 (Markdown over URL): Here is a test link! {original_url}"
    offset2 = text2.find(original_url)
    entity2 = types.MessageEntityTextUrl(offset=offset2, length=len(original_url), url=iv_url)
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text2,
        random_id=random.randint(1000000, 9999999),
        entities=[entity2],
        no_webpage=False
    ))

    # IDEA 3: Markdown-style URL Entity over a visible label at the end
    print("Sending Idea 3 (Entity over a label at end)...")
    label = "[Instant View]"
    text3 = f"Idea 3 (Markdown over Label): Here is a test link! {original_url} {label}"
    offset3 = text3.find(label)
    entity3 = types.MessageEntityTextUrl(offset=offset3, length=len(label), url=iv_url)
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text3,
        random_id=random.randint(1000000, 9999999),
        entities=[entity3],
        no_webpage=False
    ))

    # IDEA 5: Zero-width space at the VERY BEGINNING of the message
    print("Sending Idea 5 (Zero-width space at beginning)...")
    text5 = f"\u200BHere is a test link! {original_url}"
    offset5 = 0
    entity5 = types.MessageEntityTextUrl(offset=offset5, length=1, url=iv_url)
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text5,
        random_id=random.randint(1000000, 9999999),
        entities=[entity5],
        no_webpage=False
    ))

    # IDEA 6: A tiny visible dot at the beginning
    print("Sending Idea 6 (Visible dot at beginning)...")
    text6 = f". Here is a test link! {original_url}"
    offset6 = 0
    entity6 = types.MessageEntityTextUrl(offset=offset6, length=1, url=iv_url)
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text6,
        random_id=random.randint(1000000, 9999999),
        entities=[entity6],
        no_webpage=False
    ))

    # IDEA 7: Zero-width space placed immediately BEFORE the original URL
    print("Sending Idea 7 (Zero-width space just before URL)...")
    text7 = f"Here is a test link! \u200B{original_url}"
    offset7 = text7.find("\u200B")
    entity7 = types.MessageEntityTextUrl(offset=offset7, length=1, url=iv_url)
    await client(functions.messages.SendMessageRequest(
        peer=target_chat,
        message=text7,
        random_id=random.randint(1000000, 9999999),
        entities=[entity7],
        no_webpage=False
    ))

    print("All tests sent! Please check your Saved Messages and click the links to see how they behave.")

with client:
    client.loop.run_until_complete(main())
