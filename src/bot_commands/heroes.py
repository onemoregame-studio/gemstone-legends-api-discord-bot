from discord.ext import commands
from utils import  GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote, validate_color
import discord


class Heroes(commands.Cog):
    @commands.command(name='color', help='List heroes of specified color')
    async def heroes_by_color(self, ctx, *, color: UserInputSanitizer):
        color_exists = validate_color(color)
        
        if color_exists == False:
            await send_message_to_channel(ctx, 'Color not found')
            return False

        heroes_by_color = await GemstoneStatsApi.get_api_response('heroes/by_color/' + quote(color))

        if not heroes_by_color:
            await send_message_to_channel(ctx, 'Heroes lists not awailable at the moment')
            return False

        embed = self._get_heroes_lists_embed(heroes_by_color, ctx)
        await send_message_to_channel(ctx, embed=embed)


    def _get_heroes_lists_embed(self, heroes_by_color, ctx):   
        data = {
            "RED": ["Walter", "Dobrinka"],
            "GREEN": ["Aya", "Bavric"]
        }
        
        for color, heroes in data:
            embed = discord.Embed(title=color)

            for hero in heroes:
                embed = discord.Embed(title=hero)

        return embed