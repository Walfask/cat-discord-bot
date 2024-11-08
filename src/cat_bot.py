import datetime
import io
import os

import aiohttp
import discord
from dateutil import tz
from discord.ext import commands, tasks
from dotenv import load_dotenv

from database import Database
from image import Image

load_dotenv()
TOKEN = os.getenv("TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USER_ID = os.getenv("USER_ID")
DIR_PATH = os.path.abspath('.')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
time = datetime.time(hour=9, tzinfo=tz.gettz("US/Eastern"))

@client.event
async def on_ready():
    print(f"Logged on as {client.user}")
    client.channels = await get_channels()
    client.database = Database(f"{DIR_PATH}/db/cat.db")
    client.daily_pic = DailyPic()


@client.event
async def on_message(message):
    if (
        str(message.guild.id) == SERVER_ID
        and str(message.channel.id) == CHANNEL_ID
        and str(message.author.id) == USER_ID
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
            await message.channel.send(content=f"pong! ({datetime.datetime.now(tz=tz.gettz('US/Eastern'))})")



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


async def send_image_from_db():
    id = client.database.get_counter()
    file_name = client.database.get_picture_file(id)

    for channel in client.channels:
        await channel.send(file=discord.File(f"{DIR_PATH}/images/{file_name}"))


class DailyPic(commands.Cog):
    def __init__(self):
        self.cron_send_pic.start()

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(time=time)
    async def cron_send_pic(self):
        await send_image_from_db()


client.run(TOKEN)
