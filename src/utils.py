import aiohttp
import urllib.parse
from aiocache import cached
from discord.ext import commands
from discord import Embed
import os
from dotenv import load_dotenv

load_dotenv()


class GemstoneStatsApi:
    """Group of staticmethods for querying game REST API"""

    @staticmethod
    @cached(ttl=int(os.getenv('CACHE_EXPIRE_SECONDS')))
    async def _get_response_from_url(url: str):
        api_response = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    api_response = await response.json()

        if isinstance(api_response, list):
            return api_response[:int(os.getenv('MAX_RETURN_RESULTS'))]

        return api_response

    async def get_api_response(command: str, params: dict = None):
        payload = urllib.parse.urlencode(params, quote_via=quote) if params else ''
        url = urllib.parse.urljoin(os.getenv('API_URL'), f'{command}?{payload}')
        return await GemstoneStatsApi._get_response_from_url(url)


class UserInputSanitizer(commands.Converter):
    """User input goes through here before being delivered as a command argument"""

    async def convert(self, ctx, argument):
        return str(argument[:int(os.getenv('MAX_COMMAND_ARGUMENT_LENGTH'))])


async def send_message_to_channel(ctx, message, embed=None):
    if _is_private_message(ctx):
        return

    embed = _get_embed(message, embed)
    greetings = f"{os.getenv('BOT_RESPONSE_PREFIX')}Hi <@{ctx.message.author.id}>, here is your result:"
    await ctx.send(greetings, embed=embed)


def validate_color(color):
    colors = [
        'red',
        'green',
        'blue',
        'yellow',
        'purple'
    ]

    if color in colors:
        return True
    
    return False


def get_color_from_string(color_name: str) -> int:
    color_name = color_name.lower()
    colors = {
        'red': 0xFF5733,
        'blue': 0x3498DB,
        'green': 0x27AE60,
        'yellow': 0xF4D03F,
        'purple': 0x8E44AD
    }

    if color_name in colors:
        return colors[color_name]
    else:
        return 0x17202A


def quote(data, *args, **kwargs):
    return urllib.parse.quote_plus(data, *args, **kwargs)


def _is_private_message(ctx):
    return False if ctx.message.guild else True


def _get_embed(message, embed):
    if embed:
        return embed

    return Embed(
        description=str(message) or 'Empty result'
    )
