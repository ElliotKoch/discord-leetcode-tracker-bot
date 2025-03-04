import discord
import json
import requests
from dotenv import load_dotenv
import os
import logging

# Keys are stored locally in the '.env' file for security reasons.
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

github_data = json.load(open("data.json"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


# Creates a handler for the logs
#handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
client.run(BOT_TOKEN)#, log_handler=handler, log_level=logging.DEBUG)