import discord
from discord.ext import commands
import asyncio
import re

def format_duration(seconds):
    """Format duration in seconds to readable format"""
    if not seconds:
        return "Unknown"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def clean_content(content, max_length=2000):
    """Clean and truncate content for Discord messages"""
    if not content:
        return "No content"
    
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Truncate if too long
    if len(content) > max_length:
        content = content[:max_length-3] + "..."
    
    return content

def create_error_embed(title, description, color=discord.Color.red()):
    """Create a standard error embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

def create_success_embed(title, description, color=discord.Color.green()):
    """Create a standard success embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

async def send_confirmation(ctx, message, timeout=30):
    """Send a confirmation message and wait for user response"""
    embed = discord.Embed(
        title="⚠️ Confirmation Required",
        description=f"{message}\n\nReact with ✅ to confirm or ❌ to cancel.",
        color=discord.Color.orange()
    )
    
    confirmation_msg = await ctx.send(embed=embed)
    await confirmation_msg.add_reaction("✅")
    await confirmation_msg.add_reaction("❌")
    
    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["✅", "❌"] and 
                reaction.message.id == confirmation_msg.id)
    
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
        
        if str(reaction.emoji) == "✅":
            return True
        else:
            return False
            
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="⏰ Timeout",
            description="Confirmation timed out.",
            color=discord.Color.red()
        )
        await confirmation_msg.edit(embed=embed)
        return False

def has_higher_role(member1, member2):
    """Check if member1 has a higher role than member2"""
    return member1.top_role > member2.top_role

def get_member_permissions(member):
    """Get a list of important permissions for a member"""
    permissions = []
    
    important_perms = {
        'administrator': 'Administrator',
        'manage_guild': 'Manage Server',
        'manage_channels': 'Manage Channels',
        'manage_roles': 'Manage Roles',
        'ban_members': 'Ban Members',
        'kick_members': 'Kick Members',
        'manage_messages': 'Manage Messages',
        'mention_everyone': 'Mention Everyone',
        'manage_webhooks': 'Manage Webhooks',
        'manage_emojis': 'Manage Emojis'
    }
    
    for perm, name in important_perms.items():
        if getattr(member.guild_permissions, perm):
            permissions.append(name)
    
    return permissions

def parse_time(time_str):
    """Parse time string to seconds (e.g., '1h30m' -> 5400)"""
    if not time_str:
        return None
    
    time_regex = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
    match = time_regex.match(time_str.lower())
    
    if not match:
        return None
    
    days, hours, minutes, seconds = match.groups()
    
    total_seconds = 0
    if days:
        total_seconds += int(days) * 86400
    if hours:
        total_seconds += int(hours) * 3600
    if minutes:
        total_seconds += int(minutes) * 60
    if seconds:
        total_seconds += int(seconds)
    
    return total_seconds if total_seconds > 0 else None

def is_url(string):
    """Check if string is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(string) is not None

def get_status_emoji(status):
    """Get emoji for Discord status"""
    status_emojis = {
        'online': '🟢',
        'idle': '🟡',
        'dnd': '🔴',
        'offline': '⚫',
        'streaming': '🟣'
    }
    return status_emojis.get(str(status), '❓')

async def paginate_content(ctx, content_list, title="Content", items_per_page=10):
    """Paginate content across multiple embeds"""
    if not content_list:
        embed = discord.Embed(
            title=title,
            description="No content to display.",
            color=discord.Color.orange()
        )
        return await ctx.send(embed=embed)
    
    pages = []
    for i in range(0, len(content_list), items_per_page):
        page_content = content_list[i:i + items_per_page]
        
        embed = discord.Embed(
            title=title,
            color=discord.Color.blue()
        )
        
        for j, item in enumerate(page_content, start=i + 1):
            embed.add_field(
                name=f"{j}. {item.get('name', 'Item')}",
                value=item.get('value', 'No description'),
                inline=False
            )
        
        embed.set_footer(text=f"Page {len(pages) + 1}/{(len(content_list) - 1) // items_per_page + 1}")
        pages.append(embed)
    
    if len(pages) == 1:
        return await ctx.send(embed=pages[0])
    
    # Multi-page pagination
    current_page = 0
    message = await ctx.send(embed=pages[current_page])
    
    await message.add_reaction("◀️")
    await message.add_reaction("▶️")
    
    def check(reaction, user):
        return (user == ctx.author and 
                str(reaction.emoji) in ["◀️", "▶️"] and 
                reaction.message.id == message.id)
    
    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60, check=check)
            
            if str(reaction.emoji) == "▶️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=pages[current_page])
            elif str(reaction.emoji) == "◀️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=pages[current_page])
            
            await message.remove_reaction(reaction, user)
            
        except asyncio.TimeoutError:
            break
    
    # Remove reactions after timeout
    try:
        await message.clear_reactions()
    except:
        pass
