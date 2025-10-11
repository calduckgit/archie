import discord
from discord.ext import commands
import os
import json

def load_prefix_from_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", ".config")
    try:
        with open(config_path, "r") as file:
            for line in file.readlines():
                line = line.strip().replace(" ", "")
                if line.startswith("BOT_PREFIX="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        print("No .config file found. Using default prefix.")
    return ">" 

def load_token_from_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    try:
        with open(env_path, "r") as file:
            for line in file.readlines():
                line = line.strip().replace(" ", "")  # BOT_TOKEN="..."
                if line.startswith("BOT_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        raise RuntimeError("No .env file found. BOT_TOKEN is required!")
    raise RuntimeError("BOT_TOKEN not found in .env!")

DEFAULT_PREFIX = load_prefix_from_config()
TOKEN = load_token_from_env()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

async def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX

    prefix_cog = bot.get_cog('SetPrefix')
    if prefix_cog:
        return prefix_cog.get_prefix(message.guild.id)

    return DEFAULT_PREFIX

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

async def load_cogs_from_json(json_file):
    json_path = os.path.join(os.path.dirname(__file__), json_file)
    with open(json_path, "r") as file:
        data = json.load(file)
        for cog in data["cogs"]:
            await bot.load_extension(cog)

async def load_extensions():
    try:
        await load_cogs_from_json("cogs.json")
        print("Successfully loaded cogs.")
    except Exception as e:
        print(f"One or more cogs failed to load: {e}")

@bot.event
async def on_ready():
    total_users = sum(guild.member_count for guild in bot.guilds)
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{total_users} users"
        )
    )
    try:
        await bot.tree.sync()
        print("Slash commands have been synced.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    print(f"Bot is online as user: {bot.user}")

async def main():
    await load_extensions()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
