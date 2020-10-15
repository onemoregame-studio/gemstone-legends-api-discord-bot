from discord.ext import commands
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


    @commands.command(name='top_wins', help='Top wins yesterday')
    async def top_wins(self, ctx):
        top_players = await GemstoneStatsApi.get_api_response('stats/top_battles_won', {'days': 1})
        message = []

        for player in top_players:
            message.append(f"{player.get('rankingPlace', '')}. **{player.get('nick', '')}** ``BATTLES WON:{player.get('battles_won', 0):,}``")

        await send_message_to_channel(ctx, '\n'.join(message[:10]))

    @commands.command(name='hero', help='List hero stats')
    async def hero_stats(self, ctx, *, hero_name: UserInputSanitizer):
        if not hero_name:
            return

        all_creature_stats = await GemstoneStatsApi.get_api_response('stats/creature/' + quote(hero_name))
        visible_stats = ["Health", "Attack", "Defense", "CriticalDamageFactor", "CriticalChanceFactor", "SpeedGainFactor",
                 "ManaGainFactor", "Resistance", "Accuracy", "Rarity", "Color", "Class", "Name", "Power", "Skill"]
        message = ['**' + hero_name + '**']

        for stat in visible_stats:
            param = re.findall('[A-Z][^A-Z]*', stat)
            param = ' '.join(param).title()
            value = str(all_creature_stats.get(stat, ''))

            if value.replace('.','',1).isdigit() and 0 < float(value) < 1:
                value = f"{float(value):.0%}"

            message.append(f"``{param}``: {value}")

        await send_message_to_channel(ctx, '\n'.join(message))
