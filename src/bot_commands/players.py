from discord.ext import commands
from discord.utils import get
from utils import  GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote
import re
import discord


class Players(commands.Cog):
    """Methods for displaying players stats"""

    @commands.command(name='player', help='List player stats')
    async def player_stats(self, ctx, *, user_id: UserInputSanitizer):
        player = await GemstoneStatsApi.get_api_response('players/' +  quote(str(user_id)))

        if not player:
            await send_message_to_channel(ctx, 'Player not found')
            return

        stats = ["team_power", "clan_id"]
        message = ['**' + player.get('nick', '') + '**']

        for stat in stats:
            param = stat.replace('_', ' ').title()
            value = str(player.get(stat, ''))
            message.append(f"``{param}``: {value}")

        await send_message_to_channel(ctx, '\n'.join(message))


    @commands.command(name='top_battles', help='Top wins yesterday')
    async def top_battles(self, ctx):
        top_players = await GemstoneStatsApi.get_api_response('stats/top_battles_won', {'days': 1})
        message = []

        for player in top_players:
            message.append(f"{player.get('rankingPlace', '')}. **{player.get('nick', '')}** ``BATTLES WON:{player.get('battles_won', 0):,}``")

        await send_message_to_channel(ctx, '\n'.join(message[:10]))

    @commands.command(name='hero', help='List hero stats')
    async def hero_stats(self, ctx, *, hero_name: UserInputSanitizer):
        if not ctx.message.guild:
            await send_message_to_channel(ctx, 'Command !hero not supported in private messages due to custom guild emojis required to display hero card')
            return False

        if not hero_name:
            await send_message_to_channel(ctx, 'Hero not found')
            return False

        creature_stats = await GemstoneStatsApi.get_api_response('stats/creature/' + quote(hero_name))

        if not creature_stats:
            await send_message_to_channel(ctx, 'Hero stats not available')
            return False

        class_name = creature_stats.get('Class_abilities', {}).get('name', '').title()
        class_type = creature_stats.get('Class_abilities', {}).get('type', '').title()

        visible_stats = {
            f'{get(ctx.message.guild.emojis, name="hp_icon")} HP': 'Health',
            f'{get(ctx.message.guild.emojis, name="spd_icon")} SPD': 'SpeedGainFactor',
            f'{get(ctx.message.guild.emojis, name="cr_icon")} CR': 'CriticalChanceFactor',

            f'{get(ctx.message.guild.emojis, name="atk_icon")} ATK': 'Attack',
            f'{get(ctx.message.guild.emojis, name="res_icon")} RES': 'Resistance',
            f'{get(ctx.message.guild.emojis, name="cd_icon")} CD': 'CriticalDamageFactor',

            f'{get(ctx.message.guild.emojis, name="def_icon")} DEF': 'Defense',
            f'{get(ctx.message.guild.emojis, name="acc_icon")} ACC': 'Accuracy',
            f'{get(ctx.message.guild.emojis, name="mg_icon")} MG': 'ManaGainFactor',
        }

        embed = discord.Embed(
            title=creature_stats.get('Name', ''),
            description=f'{class_name}, {class_type}',
        )

        if creature_stats.get('creature_avatar'):
            embed.set_thumbnail(url=creature_stats.get('creature_avatar'))

        for stat_name, stat_key in visible_stats.items():
            value = str(creature_stats.get(stat_key, '-'))

            if (value.replace('.','',1).isdigit() and 0 < float(value) < 1) or value == '0':
                value = f"{float(value):.0%}"

            embed.add_field(name=stat_name, value=value, inline=True)

        if creature_stats.get('Active_ability', {}).get('name'):
            embed.add_field(name=creature_stats.get('Active_ability', {}).get('name', '-'), value=creature_stats.get('Active_ability', {}).get('description', '-'), inline=False)

        for passive_ability in creature_stats.get('Passive_abilities', []):
            if passive_ability.get('name'):
                embed.add_field(name=passive_ability.get('name', '-'), value=passive_ability.get('description', '-'), inline=False)

        if creature_stats.get('Leader_ability', {}).get('name'):
            embed.add_field(name=creature_stats.get('Leader_ability', {}).get('name', '-'), value=creature_stats.get('Leader_ability', {}).get('description', '-'), inline=False)

        await send_message_to_channel(ctx, '', embed=embed)

    @commands.command(name='help', help='Help')
    async def help(self, ctx):
        message = """**GUILDS**
``!find GUILD_NAME`` - Use it to find guild_id using guild name, e.g. ``!find Crazy Beasts``
``!guild GUILD_ID`` - Use it to check guild stats, e.g. ``!guild clan_4251#1``
``!members GUILD_ID`` - Use it to check the guild members and their power, e.g. ``!members clan_4251#1``
``!place GUILD_ID`` - Use it to check the guild place in the ranking, e.g. ``!place clan_4251#1``

**HEROES**
``!hero HERO_NAME`` - Use it to find detailed information about each Hero in the game, e.g. ``!hero Wanda``

**RANKINGS**
``!top_battles`` - Use it to check yesterday's top 10 players with the most battles
``!top_guilds`` - Use it to list the top 10 Guilds in the game"""

        await send_message_to_channel(ctx, message)
