import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    print(message.author, client.user)
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('MTM0NDk3MTM2ODgyMjczODk0NA.GZqbWk.NsPci512kJWQrVtndK6_e-aTSOSsfsYybUZALY')

