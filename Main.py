import json

import discord
from sqlalchemy import create_engine, DATETIME
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from Business.Models.AuthorizedRole import AuthorizedRole
from Business.Models.Event import Event
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import mysql

load_dotenv("conf/app.env")
logging.basicConfig(level=logging.DEBUG)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MYSQL_DIALECT = os.getenv("MYSQL_DIALECT")
MYSQL_DRIVER = os.getenv("MYSQL_DRIVER")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PWD = os.getenv("MYSQL_PWD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")
BOT_PREFIX = os.getenv("BOT_PREFIX")

engine = create_engine(
    f"{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT.__str__()}/{MYSQL_DB}",
    echo=True)
Session = sessionmaker(bind=engine)
session = Session()

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, description="desc")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def is_admin(user):
    return user.guild_permissions.administrator


def is_animator(user):
    authorizedroles = session.query(AuthorizedRole).all()
    for role in authorizedroles:
        if discord.utils.get(user.roles, name=role.name) is not None:
            return True
    return False


async def create_embed_inscr(event):
    user_list = ""
    for id in event.users.split(','):
        user_list += f'• <@{id}>\r'
    embed = discord.Embed(title="Liste d'inscription",
                          description=f"Partie de {event.type} du {event.date_closure.strftime('%d/%m/%Y')}\r "
                                      f"Pour s'inscrire:\r** {BOT_PREFIX}register {event.id}**",
                          color=0x16b826)
    embed.add_field(name="Liste des participant", value=user_list, inline=False)
    if not event.open:
        embed.add_field(name="Status", value="Inscription fermée", inline=False)
        return embed
    if len(event.users.split(',')) < event.max_user:
        embed.add_field(name="Status", value="Inscription ouverte", inline=False)
    else:
        embed.add_field(name="Status", value="Inscription pleine", inline=False)
    return embed


@bot.command()
async def test(ctx, msg):
    await ctx.send(msg)


@bot.command(descritption="ajouter un role authorisé a utiliser les commandes d'animation")
async def addRole(ctx, *, role: discord.Role):
    if is_admin(ctx.author):
        role = AuthorizedRole(id=role.id, name=role.name)
        if session.query(AuthorizedRole).get(role.id) is None:
            role = AuthorizedRole(id=role.id, name=role.name)
            session.add(role)
            session.commit()
            await ctx.channel.send('Role <@&' + str(session.query(AuthorizedRole.id)[0].id) + '> registered!')
        else:
            await ctx.channel.send('Role <@&'
                                   + str(session.query(AuthorizedRole).get(role.id).id) +
                                   '> has already been registered!')
    else:
        await ctx.channel.send('You don\'t have permission to use this command')


@bot.command(descritption="Créer une liste d'inscritpion pour un evenement")
async def createEvent(ctx, game, count, hour, date):
    if is_animator(ctx.author):
        date = date.split("/")
        hour = hour.split("h")
        date_end = datetime(int(date[2]), int(date[1]), int(date[0]), int(hour[0]), int(hour[1]))
        event = Event(date_closure=date_end, users=f'{ctx.author.id}', max_user=count, type=game)
        session.add(event)
        session.commit()

        id_message = await ctx.channel.send(embed=await create_embed_inscr(event))
        event.id_message = id_message.id
        session.add(event)
        session.commit()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')


@bot.command(descritption="fermer une liste d'inscritpion pour un evenement")
async def closeEventRegister(ctx, event_id):
    if is_animator(ctx.author):
        event = session.query(Event).get(event_id)
        event.open = False
        msg = await ctx.channel.fetch_message(event.id_message)
        await msg.edit(embed=await create_embed_inscr(event))
        await ctx.message.delete()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')


@bot.command(descritption="s'inscrire a un event")
async def register(ctx, event_id):
    event = session.query(Event).get(event_id)
    registered_users = event.users.split(',')
    if event.open and len(registered_users) < event.max_user:
        if str(ctx.author.id) in registered_users:
            await (await ctx.channel.send("Vous etes deja inscrit a cet evenement")).delete(delay=30)
            await ctx.message.delete(delay=30)
            return
        event.users += f',{ctx.author.id}'
        session.add(event)
        session.commit()
        msg = await ctx.channel.fetch_message(event.id_message)
        await msg.edit(embed=await create_embed_inscr(event))
        await ctx.message.delete()
    else:
        await ctx.channel.send("les inscritpion a cet evenement sont deja terminée ou la liste est pleine")


@bot.command(descritption="se désinscrire d'un event")
async def unregister(ctx, event_id):
    event = session.query(Event).get(event_id)
    event.users = event.users.replace(f'{ctx.author.id},', '')
    session.add(event)
    session.commit()
    msg = await ctx.channel.fetch_message(event.id_message)
    await msg.edit(embed=await create_embed_inscr(event))
    await ctx.message.delete()


bot.run(DISCORD_TOKEN)
