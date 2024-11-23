import datetime
import io
import os

import aiocron
import aiohttp
import discord
from dateutil import tz
from dotenv import load_dotenv

from database import Database
from image import Image

load_dotenv()
DEBUG = os.getenv("DEBUG", "False") == "True"
TOKEN = os.getenv("TOKEN")
MAIN_SERVER_ID = os.getenv("MAIN_SERVER_ID")
MAIN_CHANNEL_ID = os.getenv("MAIN_CHANNEL_ID")
MAIN_USER_ID = os.getenv("MAIN_USER_ID")
CHANNEL_IDS = os.getenv("CHANNEL_IDS")
DIR_PATH = os.path.abspath('.')

client = discord.Client()

@client.event
async def on_ready():
    print(f"Logged on as {client.user}")
    client.channels = await get_channels()
    client.database = Database(f"{DIR_PATH}/db/cat.db")


@client.event
async def on_message(message):
    if (
        str(message.guild.id) == MAIN_SERVER_ID
        and str(message.channel.id) == MAIN_CHANNEL_ID
        and str(message.author.id) == MAIN_USER_ID
    ):
        if message.attachments:
            image_content = message.content
            image_name = message.attachments[0].filename
            image_url = message.attachments[0].url
            image = Image(image_content, image_name, image_url)

            for channel in client.channels:
                await send_image(channel, image)

        if message.content == "!pic":
            await send_image_from_db()

        if message.content == "!ping":
            channel = client.get_channel(int(MAIN_CHANNEL_ID))
            await send_ping_response(channel)


async def get_channels():
    channel_ids = [int(id.strip()) for id in CHANNEL_IDS.split(',')]
    return [client.get_channel(int(id)) for id in channel_ids]


async def send_ping_response(channel):
    await channel.send(content=f"pong! ({datetime.datetime.now(tz=tz.gettz('US/Eastern'))})")


async def send_image(channel, image):
    async with aiohttp.ClientSession() as session:
        async with session.get(image.url) as response:
            data = io.BytesIO(await response.read())
            await channel.send(content=image.content, file=discord.File(data, image.filename))


async def send_image_from_db():
    id = client.database.get_counter()
    file_name = client.database.get_picture_file(id)

    for channel in client.channels:
        await channel.send(file=discord.File(f"{DIR_PATH}/images/{file_name}"))

@aiocron.crontab("0 9 * * *")
async def cron_send_pic():
    await send_image_from_db()

    if DEBUG:
        channel = client.get_channel(int(MAIN_CHANNEL_ID))
        await send_ping_response(channel)

client.run(TOKEN)
