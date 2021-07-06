import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('conf/app.env')
logging.basicConfig(level=logging.INFO)
DB_SCHEMA = os.getenv('DB_SCHEMA')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_DIALECT = os.getenv('DB_DIALECT')
DB_DRIVER = os.getenv('DB_DRIVER')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DB = os.getenv('DB_DB')
BOT_PREFIX = os.getenv('BOT_PREFIX')

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
bot.remove_command('help')
