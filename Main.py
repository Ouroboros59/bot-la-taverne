import discord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql
from Business.Models.AuthorizedRole import AuthorizedRole

DISCORD_TOKEN = "NzgwNDg5MzIwNTgyNjEwOTk0.X7v1Ug.vupp97razj8HRDXVeMhwtGZEgoc"
MYSQL_DIALECT = "mysql"
MYSQL_DRIVER = "mysqlconnector"
MYSQL_USER = "admin"
MYSQL_PWD = "IKhVvZVl0yZLgD3"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "bot_database"
BOT_PREFIX = "!"
BOT_COMMAND_ADD_ROLE = "addRole"

client = discord.Client()
engine = create_engine(f"{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def is_admin(user):
    return user.guild_permissions.administrator


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(BOT_PREFIX + BOT_COMMAND_ADD_ROLE):
        if is_admin(message.author):
            role = message.role_mentions[0]
            role = AuthorizedRole(id=role.id, name=role.name)

            session.add(role)
            session.commit()
            await message.channel.send('Role <@&' + str(session.query(AuthorizedRole.id)[0].id) + '> registered!')


client.run(DISCORD_TOKEN)
