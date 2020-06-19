from discord.ext import commands
from utils import GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote


class Guilds(commands.Cog):
    """Methods for displaying guilds stats"""

    @commands.command(name='find', help='Find guild_id using guild name')
    async def find_clan(self, ctx, *, guild_name: UserInputSanitizer):
        clans = await GemstoneStatsApi.get_api_response('clans', {'name': guild_name})
        message = []

        for clan in clans:
            message.append(f"**{clan.get('name', '')}**: ``{clan.get('id', '')}``")

        await send_message_to_channel(ctx, '\n'.join(message))


    @commands.command(name='top', help='List guilds ranking')
    async def top_clans(self, ctx):
        clans = await GemstoneStatsApi.get_api_response('clans/ranking')
        message = []
        for clan in clans:
            message.append(f"{clan.get('rankingPlace', '')}. **{clan.get('name', '')}** ``POWER:{clan.get('guildPower', 0):,}``")

        await send_message_to_channel(ctx, '\n'.join(message[:10]))


    @commands.command(name='members', help='List guild members ordered by Team Power')
    async def clan_members_ranking(self, ctx, *, guild_name: UserInputSanitizer):
        guild_id = await self.find_clan_id_by_name(ctx, guild_name)
        if not guild_id:
            return

        members = await GemstoneStatsApi.get_api_response('clans/' + quote(guild_id) + '/members')
        members.sort(key=lambda x: x.get('TeamPower', 0), reverse=True)
        message = []

        for place, member in enumerate(members, 1):
            name = member.get('username', '')
            team_power = member.get('TeamPower', 0)
            user_id = member.get('userId', 0)
            message.append(f"{place}. **{name}** ``POWER:{team_power:,}`` ``ID:{user_id}``")

        await send_message_to_channel(ctx, '\n'.join(message))


    @commands.command(name='guild', help='List guild stats')
    async def clan_stats(self, ctx, *, guild_name: UserInputSanitizer):
        guild_id = await self.find_clan_id_by_name(ctx, guild_name)
        if not guild_id:
            return

        clan = await GemstoneStatsApi.get_api_response('clans/' + quote(guild_id) + '/stats')
        stats = ["description", "members", "team_power", "created"]
        message = ['**' + clan.get('name', '') + '**']

        for stat in stats:
            param = stat.replace('_', ' ').title()
            value = str(clan.get(stat, ''))
            message.append(f"``{param}``: {value}")

        await send_message_to_channel(ctx, '\n'.join(message))


    async def find_clan_id_by_name(self, ctx, guild_name):
        guild_name = guild_name.lower()
        if guild_name.startswith('clan_'):
            return guild_name

        clans = await GemstoneStatsApi.get_api_response('clans', {'name': guild_name})

        result = []
        for clan in clans:
            if guild_name == clan.get('name', '').lower():
                result.append(clan)

        if not result:
            await send_message_to_channel(ctx, 'name not found')
            return False

        if len(result) > 1:
            found = []
            for clan in result:
                guild_name = clan.get('name', '')
                guild_id = clan.get('id', '')
                found.append(f"**{guild_name}** ``{guild_id}``")

            message = 'there are several guilds with this name, use guild_id instead of name\n' + '\n'.join(found)
            await send_message_to_channel(ctx, message)
            return False

        return result[0].get('id', '')


    @commands.command(name='place', help='Show guild ranking place')
    async def clan_place(self, ctx, *, guild_name: UserInputSanitizer):
        guild_id = await self.find_clan_id_by_name(ctx, guild_name)
        if not guild_id:
            return

        clan = await GemstoneStatsApi.get_api_response('clans/' + quote(guild_id) + '/place')
        place = clan.get('rankingPlace', '')
        name = clan.get('name', '')
        message = f"**{name}** - Ranking Place: #{place} :trophy:"

        await send_message_to_channel(ctx, message)
