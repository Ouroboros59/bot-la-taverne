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

engine = create_engine(
    f'{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT.__str__()}/{MYSQL_DB}',
    echo=True)
Session = sessionmaker(bind=engine)
session = Session()

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'Boire l\'apéro avec {BOT_PREFIX}help'))
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


async def create_embed_inscr(event, color):
    user_list = ''
    for id_user in event.users.split(','):
        user_list += f'• <@{id_user}>\r'
    user_list += '\u200b'

    embed = discord.Embed(title='**Liste d\'inscription**',
                          description=f'Partie de {event.type} du {event.date_closure.strftime("%d/%m/%Y")}\n\n '
                                      f'__Pour s\'inscrire__**:** `{BOT_PREFIX}register {event.id}`\n'
                                      f'__Pour se désinscrire__**:** ``{BOT_PREFIX}unregister {event.id}\r``\u200b',
                          color=color)
    embed.add_field(name='**Liste des participants**', value=user_list, inline=False)
    if not event.open:
        embed.add_field(name='**Statut**', value='Inscription fermée', inline=False)
        return embed
    if len(event.users.split(',')) < event.max_user:
        embed.add_field(name='**Statut**', value='Inscription ouverte', inline=False)
    else:
        embed.add_field(name='**Statut**', value='Inscription pleine', inline=False)
    return embed


@bot.command()
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


@bot.command()
async def createEvent(ctx, game, count, hour, date):
    if is_animator(ctx.author):
        date = date.split('/')
        hour = hour.split('h')
        date_end = datetime(int(date[2]), int(date[1]), int(date[0]), int(hour[0]), int(hour[1]))
        event = Event(date_closure=date_end, users=f'{ctx.author.id}', max_user=count, type=game)
        session.add(event)
        session.commit()

        id_message = await ctx.channel.send(embed=await create_embed_inscr(event, 0x16b826))
        event.id_message = id_message.id
        session.add(event)
        session.commit()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')


@bot.command()
async def closeEventRegister(ctx, event_id):
    if is_animator(ctx.author):
        event = session.query(Event).get(event_id)
        event.open = False
        msg = await ctx.channel.fetch_message(event.id_message)
        await msg.edit(embed=await create_embed_inscr(event, 0xec2013))
        await ctx.message.delete()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')


@bot.command()
async def register(ctx, event_id):
    event = session.query(Event).get(event_id)
    registered_users = event.users.split(',')
    if event.open and len(registered_users) < event.max_user:
        if str(ctx.author.id) in registered_users:
            await (await ctx.channel.send('Tu es déjà inscrit.e à cet événement')).delete(delay=30)
            await ctx.message.delete(delay=30)
            return
        event.users += f',{ctx.author.id}'
        session.add(event)
        session.commit()
        msg = await ctx.channel.fetch_message(event.id_message)
        if len(event.users.split(',')) < event.max_user:
            color = 0x16b826
        else:
            color = 0xf57c17
        await msg.edit(embed=await create_embed_inscr(event, color))
        await ctx.message.delete()
    else:
        await ctx.channel.send('Pour cet événement soit la liste est pleine, soit les inscriptions sont terminées')


@bot.command()
async def unregister(ctx, event_id):
    event = session.query(Event).get(event_id)
    event.users = event.users.replace(f'{ctx.author.id},', '')
    session.add(event)
    session.commit()
    if len(event.users.split(',')) < event.max_user:
        color = 0x16b826
    else:
        color = 0xf57c17
    msg = await ctx.channel.fetch_message(event.id_message, color)
    await msg.edit(embed=await create_embed_inscr(event))
    await ctx.message.delete()


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Voici la liste des commandes disponibles',
                          description=open('conf/help', 'r', encoding='utf8').read()+'\r\u200b',
                          color=0xAD33E9
                          )

    embed.add_field(name='**__Préfixe du bot__**', value=f'• `{BOT_PREFIX}`', inline=False)
    embed.set_author(name='Le Tavernier', url='https://mrdoob.com/projects/chromeexperiments/google-gravity/',
                     icon_url='https://cdn.discordapp.com/avatars/780489320582610994/1b1613457d8bde8de158baf95ad42ecd'
                              '.png?size=4096')

    embed.set_footer(text=f'À la prochaine {ctx.author.display_name} pour boire un verre avec moi 🍻')
    await ctx.channel.send(embed=embed)
    await ctx.message.delete()


bot.run(DISCORD_TOKEN)
