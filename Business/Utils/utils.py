import json
import re

from Business.Models.models import User, AuthorizedRole, Event, Report
from Const import *

MENTION = re.compile("<@!?(\d+)>\s*([^<]+)")


async def user_exist(id_user, session):
    player = session.query(User).get(id_user)
    if player is None:
        return await register_user(id_user, session)
    return player


async def register_user(id_user, session):
    usr = await bot.fetch_user(id_user)
    user = User(id=id_user, name=usr.name)
    session.add(user)
    session.commit()
    session.flush()
    return session.query(User).get(id_user)


def is_admin(user):
    return user.guild_permissions.administrator


def is_animator(user, session):
    authorizedroles = session.query(AuthorizedRole).all()
    for role in authorizedroles:
        if discord.utils.get(user.roles, name=role.name) is not None:
            session.close()
            return True
    session.close()
    return False


async def parseReport(msg, session):
    if '\n' in msg:
        event_id, corps = msg.split('\n', 1)
        event = session.query(Event).get(event_id)
        if event is not None:
            report = Report(event=event)
            report.result = await parseReportData(corps)
            for userId in report.result:
                report.users.append(await user_exist(userId, session))
            return report
    return None


async def parseReportData(txt):
    result = []
    for line in txt.split('\n'):
        result.append(line.replace('<@!', '').replace('>', ''))
    return result


async def create_embed_inscr(event, color):
    user_list = ''
    for user in event.users:
        user_list += f'• <@{user.id}>\r'
    user_list += '\u200b'

    embed = discord.Embed(title='**Liste d\'inscription**',
                          description=f'Partie de {event.type} du {event.date_closure.strftime("%d/%m/%Y à %H:%M")}\n\n'
                                      f'__Pour s\'inscrire__**:** `{BOT_PREFIX}register {event.id}`\n'
                                      f'__Pour se désinscrire__**:** ``{BOT_PREFIX}unregister {event.id}\r``\u200b',
                          color=color)
    embed.add_field(name='**Participants inscrits:**', value=f'{len(event.users)}/{event.max_user}')
    embed.add_field(name='**Liste des participants**', value=user_list, inline=False)
    if not event.open:
        embed.add_field(name='**Statut**', value='Inscription fermée', inline=False)
        return embed
    if len(event.users) - 1 < event.max_user:
        embed.add_field(name='**Statut**', value='Inscription ouverte', inline=False)
    else:
        embed.add_field(name='**Statut**', value='Inscription pleine', inline=False)
    return embed


async def create_embed_report(report):
    user_list = ''
    i = 0
    users = report.result.replace('{', '').replace('}', '').split(',')
    for user in users:
        user_list += f'{i} • <@{user}>\r'
        i += 1
    user_list += '\u200b'

    embed = discord.Embed(title='**RESULTAT**',
                          description=f'Résultat de l\'evenement {report.event.type} du {report.event.date_closure.strftime("%d/%m/%Y à %H:%M")}\n',
                          color=0x16b826)
    embed.add_field(name='**Classement des participants**', value=user_list, inline=False)
    return embed
