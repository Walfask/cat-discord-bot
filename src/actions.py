import io
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
            await send_image_from_db(client)

        if message.content == "!ping":
            channel = client.get_channel(int(config.MAIN_CHANNEL_ID))
            await _send_ping_response(channel)


async def send_image_from_db(client):
    id = client.database.get_counter()
    file_name = client.database.get_picture_file(id)

    for channel in client.channels:
        await channel.send(file=discord.File(f"{config.DIR_PATH}/images/{file_name}"))


async def _send_ping_response(channel):
    await channel.send(content=f"pong! ({datetime.now(tz=ZoneInfo('America/New_York'))})")


async def _send_image(channel, image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(content=image.content, file=discord.File(data, image.filename))
