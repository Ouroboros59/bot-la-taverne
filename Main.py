import discord
from sqlalchemy import create_engine, DATETIME
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from Business.Models.AuthorizedRole import AuthorizedRole
from Business.Models.Event import Event

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
BOT_COMMAND_EVENT_REGISTER = "createEvent"

client = discord.Client()
engine = create_engine(
    f"{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}", echo=True)
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
            if session.query(AuthorizedRole).get(role.id) is None:
                role = AuthorizedRole(id=role.id, name=role.name)
                session.add(role)
                session.commit()
                await message.channel.send('Role <@&' + str(session.query(AuthorizedRole.id)[0].id) + '> registered!')
            else:
                await message.channel.send('Role <@&'
                                           + str(session.query(AuthorizedRole).get(role.id).id) +
                                           '> has already been registered!')

    # param: 1=gameType 2=maxPlayer 3=end hour 4=end date
    if message.content.startswith(BOT_PREFIX + BOT_COMMAND_EVENT_REGISTER):
        param = message.content.split(' ')[1:]
        date = param[3].split("/")
        hour = param[2].split("h")
        date_end = datetime(int(date[2]), int(date[1]), int(date[0]), int(hour[0]), int(hour[1]))
        event = Event(date_closure=date_end, users="{}", max_user=param[1])
        session.add(event)
        session.commit()

        #await message.delete()
        embed = discord.Embed(title="Liste d'inscription",
                              description=f"Partie de {param[0]} du {event.date_closure.strftime('%d/%m/%Y')}",
                              color=0x16b826)
        embed.add_field(name="Liste des participant", value="-", inline=False)
        embed.add_field(name="Status", value="Inscription ouverte", inline=False)

        id_message = await message.channel.send(embed=embed)
        event.id_message = id_message.id
        session.add(event)
        session.commit()


client.run(DISCORD_TOKEN)
