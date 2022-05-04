from discord.ext import commands
from utils import GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote


class Players(commands.Cog):
    """Methods for displaying players stats"""

    @commands.command(name='player', help='List player stats')
    async def player_stats(self, ctx, *, user_id: UserInputSanitizer):
        player = await GemstoneStatsApi.get_api_response('players/' + quote(str(user_id)))

        if not player:
            await send_message_to_channel(ctx, 'Player not found')
            return

        stats = ["team_power", "clan_id"]
        message = ['**' + player.get('nick', '') + '**']

        for stat in stats:
            param = stat.replace('_', ' ').title()
            value = str(player.get(stat, ''))
            message.append(f"`{param}`: {value}")

        await send_message_to_channel(ctx, '\n'.join(message))

    @commands.command(name='top_battles', help='Top wins yesterday')
    async def top_battles(self, ctx):
        top_players = await GemstoneStatsApi.get_api_response('stats/top_battles_won', {'days': 1})
        message = ['**Yesterday\'s top 10 players with the most battles:**\n']

        for player in top_players:
            message.append(f"{player.get('rankingPlace', '')}. **{player.get('nick', '')}** `BATTLES WON:{player.get('battles_won', 0):,}`\n")

        await send_message_to_channel(ctx, ''.join(message[:10]))
