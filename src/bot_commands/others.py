import discord
from discord.ext import commands
from utils import GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote


class Others(commands.Cog):
    @commands.command(name='help', help='Help')
    async def help(self, ctx):
        message = f"""
        # **GUILDS**
        `!find GUILD_NAME` - Use it to find guild_id using guild name, e.g. `!find Crazy Beasts`
        `!guild GUILD_ID` - Use it to check guild stats, e.g. `!guild clan_4251#1`
        `!members GUILD_ID` - Use it to check the guild members and their power, e.g. `!members clan_4251#1`
        `!place GUILD_ID` - Use it to check the guild place in the ranking, e.g. `!place clan_4251#1`
    
        # **HEROES**
        `!hero HERO_NAME` - Use it to find detailed information about each Hero in the game, e.g. `!hero Wanda`
        `!color COLOR` - Use it to list heroes od specified color (possible options are: red, green, blue, yellow, purple), e.g. `!color red`
    
        # **RANKINGS**
        `!top_battles` - Use it to check yesterday's top 10 players with the most battles
        `!top_guilds` - Use it to list the top 10 Guilds in the game 
                
        # **STATUSES**
        `!statuses` - Use it to list possible statuses (in alphabetical order)
        `!status STATUS_NAME` - Get status name, description and creatures that use it, e.g. `!status stun`
        """

        await send_message_to_channel(ctx, message)

    @commands.command(name='status', help='Get status details')
    async def status_details(self, ctx, *, status_id: str):
        status_details = await GemstoneStatsApi.get_api_response('statuses/status/' + quote(status_id))

        heroes = ""
        for hero_details in status_details['UsedByCreatures']:
            separated_details = hero_details.split(" | ")
            heroes += f"> **{separated_details[0]}** - {separated_details[1].lower()} | {separated_details[2].lower()},\n"

        embed = discord.Embed(title=status_details['Name'], description=status_details['Desc'])\
            .add_field(name='Used by:', value=heroes)

        await send_message_to_channel(ctx, '', embed)

    @commands.command(name='statuses', help='Get all possible statuses list')
    async def list_all_statuses(self, ctx):
        statuses = await GemstoneStatsApi.get_api_response('statuses/statuses')
        grouped_by_name = {}

        for status in statuses:
            first_char = status[0]
            if first_char not in grouped_by_name:
                grouped_by_name[first_char] = []

            grouped_by_name[first_char].append(status)

        embed = discord.Embed(title='Available statuses:')
        for first_char in grouped_by_name:
            statuses_names = ''
            for status in grouped_by_name[first_char]:
                statuses_names += f'\n{status},'

            embed.add_field(name=f'{first_char.upper()}:', value=statuses_names)

        await send_message_to_channel(ctx, '', embed)
