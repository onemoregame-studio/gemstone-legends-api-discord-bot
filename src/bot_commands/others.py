from discord.ext import commands
from utils import  GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote, get_statuses, build_statuses_string


class Others(commands.Cog):
    @commands.command(name='help', help='Help')
    async def help(self, ctx):
        # statuses_list = build_statuses_string()
        message = f"""
        **GUILDS**
        `!find GUILD_NAME` - Use it to find guild_id using guild name, e.g. `!find Crazy Beasts`
        `!guild GUILD_ID` - Use it to check guild stats, e.g. `!guild clan_4251#1`
        `!members GUILD_ID` - Use it to check the guild members and their power, e.g. `!members clan_4251#1`
        `!place GUILD_ID` - Use it to check the guild place in the ranking, e.g. `!place clan_4251#1`
    
        **HEROES**
        `!hero HERO_NAME` - Use it to find detailed information about each Hero in the game, e.g. `!hero Wanda`
    
        **RANKINGS**
        `!top_battles` - Use it to check yesterday's top 10 players with the most battles
        `!top_guilds` - Use it to list the top 10 Guilds in the game 
        """
    
        await send_message_to_channel(ctx, message)


    # **HEROES**
    # `!color COLOR` - Use it to list heroes od specified color (possible options are red, green, blue, yellow, purple), e.g. '!color red'

    # **STATUSES**
    # `!status` - get status description, e.g. `!status stun. Possible options are {statuses_list}.`


    @commands.command(name='status', help='Get description of a status')
    async def status_description(self, ctx, *, status_id: UserInputSanitizer):
        if status_id not in get_statuses():
            message = f'Status not found. Possible options are: {build_statuses_string()}.'
            await send_message_to_channel(ctx, message=message)
            return False

        status_description = await GemstoneStatsApi.get_api_response('others/status_description/' + quote(status_id))
        await send_message_to_channel(ctx, status_description)