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
        image_url = message.attachments[0].url
        image_name = message.attachments[0].filename
        image = Image(image_name, image_url)

        channels = await get_channels()

        for channel in channels:
            await send_image(channel, image)


async def get_channels():
    return [channel for channel in client.get_all_channels() if "cute-animals" in channel.name]


async def send_image(channel, image: Image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(file=discord.File(data, image.filename))


client.run(TOKEN)
