import io
import os

import aiohttp
import discord
from dotenv import load_dotenv

from image import Image

load_dotenv()
TOKEN = os.getenv("TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USER_ID = os.getenv("USER_ID")

client = discord.Client()


@client.event
async def on_ready():
    print(f"Logged on as {client.user}")


@client.event
async def on_message(message):
    if (
        str(message.guild.id) == SERVER_ID
        and str(message.channel.id) == CHANNEL_ID
        and str(message.author.id) == USER_ID
        and message.attachments
    ):
        image_content = message.content
        image_name = message.attachments[0].filename
        image_url = message.attachments[0].url
        image = Image(image_content, image_name, image_url)

        channels = await get_channels()

        for channel in channels:
            await send_image(channel, image)


async def get_channels():
    channel_names = ["cute-animals", "pics-and-stuff"]
    return [
        channel
        for channel in client.get_all_channels()
        if any(channel_name in channel.name for channel_name in channel_names)
    ]


async def send_image(channel, image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(content=image.content, file=discord.File(data, image.filename))


client.run(TOKEN)
