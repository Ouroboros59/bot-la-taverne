import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv('conf/app.env')
logging.basicConfig(level=logging.INFO)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MYSQL_DIALECT = os.getenv('MYSQL_DIALECT')
MYSQL_DRIVER = os.getenv('MYSQL_DRIVER')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PWD = os.getenv('MYSQL_PWD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DB = os.getenv('MYSQL_DB')
BOT_PREFIX = os.getenv('BOT_PREFIX')
Base = declarative_base()
engine = create_engine(
    f'{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT.__str__()}/{MYSQL_DB}',
    echo=True)

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
intents = discord.Intents.default()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
bot.remove_command('help')
