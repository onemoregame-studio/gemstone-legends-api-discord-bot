import aiohttp
import urllib.parse
from aiocache import cached
from discord.ext import commands
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
    message = str(message) or 'Empty result'

    if embed:
        message = ''

    discord_user_id = ctx.message.author.id
    message = f"Hi <@{discord_user_id}>, here is your result:\n{message}"
    await ctx.send(os.getenv('BOT_RESPONSE_PREFIX') + message, embed=embed)


def quote(data, *args, **kwargs):
    return urllib.parse.quote_plus(data, *args, **kwargs)
