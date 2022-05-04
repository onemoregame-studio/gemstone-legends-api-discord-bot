from collections import namedtuple
from discord.ext import commands
from discord.utils import get
from utils import GemstoneStatsApi, UserInputSanitizer, send_message_to_channel, quote, validate_color, get_color_from_string
import discord


class Heroes(commands.Cog):
    @commands.command(name='color', help='List heroes of specified color')
    async def heroes_by_color(self, ctx, *, color: UserInputSanitizer):
        color_exists = validate_color(color)

        if not color_exists:
            await send_message_to_channel(ctx, 'Color not found')
            return False

        heroes_by_color = await GemstoneStatsApi.get_api_response('stats/creatures/' + quote(color))

        if not heroes_by_color:
            await send_message_to_channel(ctx, 'Heroes lists not available at the moment')
            return False

        grouped_by_rarity = {}

        for hero in heroes_by_color:
            rarity = hero['Rarity']
            if rarity not in grouped_by_rarity:
                grouped_by_rarity[rarity] = []

            grouped_by_rarity[rarity].append(hero)

        embed = discord.Embed(title=f'{color.upper()} Heroes by rarity:', colour=get_color_from_string(color))
        for rarity in grouped_by_rarity:
            heroes_names: str = ''
            for hero in grouped_by_rarity[rarity]:
                heroes_names += hero['Name'] + ', '

            embed.add_field(
                name=f'Rarity: {rarity}',
                value=heroes_names
            )

        await send_message_to_channel(ctx, '', embed=embed)

    @commands.command(name='hero', help='List hero stats')
    async def hero_stats(self, ctx, *, hero_name: UserInputSanitizer):
        if not hero_name:
            await send_message_to_channel(ctx, 'Hero not found')
            return False

        creature_stats = await GemstoneStatsApi.get_api_response('stats/creature/' + quote(hero_name))

        if not creature_stats:
            await send_message_to_channel(ctx, 'Hero stats not available')
            return False

        embed = self._get_creature_embed(creature_stats, ctx)
        await send_message_to_channel(ctx, '', embed=embed)

    @commands.command(name='heroes', help='Heroes who use the skill')
    async def heroes_with_status(self, ctx, *, status_id):
        heroes = await GemstoneStatsApi.get_api_response('statuses/heroes/' + quote(status_id))
        if not heroes:
            await send_message_to_channel(ctx, f'No heroes using {status_id} found.')
            return

        msg: str = ''
        for hero in heroes:
            msg += f'{hero}, '
        msg = msg[:-2]

        embed = discord.Embed(title=f'Heroes with {status_id}:', description=msg)
        await send_message_to_channel(ctx, '', embed)

    def _get_creature_embed(self, creature_stats, ctx):
        embed = self._get_embed_header(creature_stats)
        embed = self._add_avatar_to_embed(creature_stats, embed)
        embed = self._add_stats_to_embed(creature_stats, ctx, embed)
        embed = self._add_abilities_to_embed(creature_stats, embed)
        embed = self._add_equipment_to_embed(creature_stats, ctx, embed)
        return embed

    def _get_embed_header(self, creature_stats):
        creature_name = creature_stats.get('Name', '')
        class_name = creature_stats.get('Class_abilities', {}).get('name', '').title()
        class_type = creature_stats.get('Class_abilities', {}).get('type', '').title()

        return discord.Embed(
            title=creature_name,
            description=f'{class_name}, {class_type}',
        )

    def _add_avatar_to_embed(self, creature_stats, embed):
        avatar_url = creature_stats.get('creature_avatar')

        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        return embed

    def _add_stats_to_embed(self, creature_stats, ctx, embed):
        visible_stats = self._get_visible_stats(ctx)

        for stat_name, stat_key in visible_stats.items():
            numeric_value = self._get_numeric_value(creature_stats, stat_key)
            embed.add_field(name=stat_name, value=numeric_value, inline=True)
        return embed

    def _get_numeric_value(self, creature_stats, stat_key):
        numeric_value = str(creature_stats.get(stat_key, '-'))

        if self._is_percentage(numeric_value):
            numeric_value = self._format_number_as_percent(numeric_value)
        return numeric_value

    def _is_percentage(self, value):
        return (value.replace('.', '', 1).isdigit() and 0 < float(value) < 1) or value == '0'

    def _format_number_as_percent(self, value):
        return f"{float(value):.0%}"

    def _get_ability_decription(self, ability):
        ability_description = namedtuple('ability', ['name', 'description'])
        name, description = ability.get('name'), ability.get('description')

        if name and description:
            return ability_description(name=name, description=description)
        return None

    def _get_ability_elements(self, creature_stats, ability_name):
        ability = creature_stats.get(ability_name)

        if isinstance(ability, dict):
            return self._get_ability_from_dict(ability)

        if isinstance(ability, list):
            return self._get_ability_from_list(ability)
        return []

    def _get_ability_from_dict(self, ability):
        result = []
        ability_description = self._get_ability_decription(ability)
        if ability_description:
            result.append(ability_description)
        return result

    def _get_ability_from_list(self, abilities):
        result = []
        for sub_ability in abilities:
            result.extend(self._get_ability_from_dict(sub_ability))
        return result

    def _add_abilities_to_embed(self, creature_stats, embed):
        abilities = [
            'Active_ability',
            'Passive_abilities',
            'Leader_ability'
        ]

        for ability_name in abilities:
            ability_elements = self._get_ability_elements(creature_stats, ability_name)

            for ability_element in ability_elements:
                skill_name = ability_element.name
                if ability_name == 'Active_ability' or ability_name == 'Passive_abilities':
                    skill_name = f'{ability_element.name}'
                embed.add_field(name=skill_name, value=ability_element.description, inline=False)
        return embed

    def _add_equipment_to_embed(self, creature_stats, ctx, embed):
        recommended_equipment = []

        for equipment_set in creature_stats.get('popular_equipment_sets', []):
            recommended_equipment.append(self._get_recommended_equipment(ctx, equipment_set))

        if recommended_equipment:
            embed.add_field(name='Recommended Sets', value=' '.join(recommended_equipment), inline=False)
        return embed

    def _get_recommended_equipment(self, ctx, equipment_set):
        emoji_name = f'set_{equipment_set.lower()}'
        icon = self._get_emoji(ctx, emoji_name)
        return f'{icon} {equipment_set}'

    def _get_emoji(self, ctx, emoji_name):
        icon = get(ctx.message.guild.emojis, name=emoji_name)
        return icon if icon else ''

    def _get_visible_stats(self, ctx):
        visible_stats = {}
        for icon in self._get_stats_icons():
            emoji = self._get_emoji(ctx, icon.file_name)
            visible_stats[f'{emoji} {icon.abbreviation}'] = icon.full_name
        return visible_stats

    def _get_stats_icons(self):
        icon = namedtuple('icon', ['file_name', 'abbreviation', 'full_name'])
        icons = [
            icon("hp_icon", 'HP', 'Health'),
            icon("spd_icon", 'SPD', 'SpeedGainFactor'),
            icon("cr_icon", 'CR', 'CriticalChanceFactor'),
            icon("atk_icon", 'ATK', 'Attack'),
            icon("res_icon", 'RES', 'Resistance'),
            icon("cd_icon", 'CD', 'CriticalDamageFactor'),
            icon("def_icon", 'DEF', 'Defense'),
            icon("acc_icon", 'ACC', 'Accuracy'),
            icon("mg_icon", 'MG', 'ManaGainFactor')
        ]
        return icons
