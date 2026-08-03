import io
import random
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord

import config
from image import Image


def get_channels(client):
    channel_ids = [int(channel_id.strip()) for channel_id in config.CHANNEL_IDS.split(",")]
    return [client.get_channel(channel_id) for channel_id in channel_ids]


async def handle_message(client, message):
    if (
        str(message.guild.id) == config.MAIN_SERVER_ID
        and str(message.channel.id) == config.MAIN_CHANNEL_ID
        and str(message.author.id) == config.MAIN_USER_ID
    ):
        if message.attachments:
            image_content = message.content
            image_name = message.attachments[0].filename
            image_url = message.attachments[0].url
            image = Image(image_content, image_name, image_url)

            for channel in client.target_channels:
                await _send_image(channel, image)

        if message.content == "!pic":
            await send_random_image(client)

        if message.content == "!ping":
            channel = client.get_channel(int(config.MAIN_CHANNEL_ID))
            await channel.send(content=f"pong! ({datetime.now(tz=ZoneInfo('America/New_York'))})")

        if message.content == "!count":
            channel = client.get_channel(int(config.MAIN_CHANNEL_ID))
            count = _get_pending_image_count()
            await channel.send(f"{count} images remaining.")


async def send_random_image(client):
    image_path, file_count = _get_random_pending_image()
    main_channel = client.get_channel(int(config.MAIN_CHANNEL_ID))

    if image_path is None:
        await main_channel.send("No images found!")
        return

    for channel in client.target_channels:
        await channel.send(file=discord.File(image_path))

    _move_image_to_sent(image_path)

    if file_count <= 1:
        await main_channel.send("No more images left to send!")


def _get_random_pending_image():
    files = [f for f in config.PENDING_DIR.iterdir() if f.is_file()]
    if not files:
        return None, 0
    return random.choice(files), len(files)


def _move_image_to_sent(image_path):
    config.SENT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(image_path), config.SENT_DIR / image_path.name)


def _get_pending_image_count():
    return sum(1 for f in config.PENDING_DIR.iterdir() if f.is_file())


async def _send_image(channel, image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(content=image.content, file=discord.File(data, image.filename))
