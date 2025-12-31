import io
import random
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord

import config
from image import Image


async def get_channels(client):
    channel_ids = [int(id.strip()) for id in config.CHANNEL_IDS.split(',')]
    return [client.get_channel(int(id)) for id in channel_ids]


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

            for channel in client.channels:
                await _send_image(channel, image)

        if message.content == "!pic":
            await send_random_image(client)

        if message.content == "!ping":
            channel = client.get_channel(int(config.MAIN_CHANNEL_ID))
            await channel.send(content=f"pong! ({datetime.now(tz=ZoneInfo('America/New_York'))})")


async def send_random_image(client):
    image_path = _get_random_pending_image()

    if image_path is None:
        channel = client.get_channel(int(config.MAIN_CHANNEL_ID))
        await channel.send(content="No more images left to send!")
        return

    for channel in client.channels:
        await channel.send(file=discord.File(image_path))

    _move_image_to_sent(image_path)


def _get_random_pending_image():
    files = [f for f in config.PENDING_DIR.iterdir() if f.is_file()]
    if not files:
        return None
    return random.choice(files)


def _move_image_to_sent(image_path):
    config.SENT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(image_path), config.SENT_DIR / image_path.name)


async def _send_image(channel, image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(content=image.content, file=discord.File(data, image.filename))
