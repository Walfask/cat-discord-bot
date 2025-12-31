import discord

import config
from actions import get_channels, handle_message
from cron import setup_cron

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged on as {client.user}")
    client.channels = await get_channels(client)

    setup_cron(client)


@client.event
async def on_message(message):
    await handle_message(client, message)


client.run(config.TOKEN)
