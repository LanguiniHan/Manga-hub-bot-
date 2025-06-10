import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import logging
from datetime import datetime
from config import Config
from database import Database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

def get_custom_prefix(bot, message):
    """Get custom prefix for each guild"""
    async def inner():
        if not message.guild:
            return "//"
        
        prefix = await bot.db.get_guild_prefix(message.guild.id)
        return prefix or "//"
    
    return asyncio.create_task(inner())

class DiscordBot(commands.Bot):
    def __init__(self):
        # Get all intents
        intents = discord.Intents.all()
        
        # Initialize database first
        self.db = Database()
        self.config = Config()
        
        # Initialize bot with default prefix
        super().__init__(
            command_prefix=get_custom_prefix,
            intents=intents,
            help_command=None,  # We'll create custom help
            case_insensitive=True
        )
    
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        cogs = [
            'cogs.moderation',
            'cogs.music',
            'cogs.manga',
            'cogs.utility',
            'cogs.admin'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logging.info(f'Loaded cog: {cog}')
            except Exception as e:
                logging.error(f'Failed to load cog {cog}: {e}')
        
        # Start keep alive task
        self.keep_alive.start()
    
    async def on_ready(self):
        """Called when bot is ready"""
        logging.info(f'{self.user} has connected to Discord!')
        logging.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="//help for commands"
            )
        )
        
        # Add start time for uptime tracking
        self.start_time = datetime.now()
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        logging.info(f'Joined new guild: {guild.name} (ID: {guild.id})')
        await self.db.add_guild(guild.id)
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logging.info(f'Left guild: {guild.name} (ID: {guild.id})')
        await self.db.remove_guild(guild.id)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Try again in {error.retry_after:.2f} seconds.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Log other errors
        logging.error(f'Command error in {ctx.command}: {error}')
        
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="Something went wrong while executing this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    @tasks.loop(minutes=30)
    async def keep_alive(self):
        """Keep bot alive by logging status"""
        logging.info(f'Bot is alive! Latency: {round(self.latency * 1000)}ms')
    
    @keep_alive.before_loop
    async def before_keep_alive(self):
        await self.wait_until_ready()

# Run the bot
if __name__ == "__main__":
    bot = DiscordBot()
    
    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error('DISCORD_TOKEN environment variable not found!')
        logging.info('Please set your Discord bot token:')
        logging.info('1. Go to https://discord.com/developers/applications')
        logging.info('2. Create a new application or select existing one')
        logging.info('3. Go to Bot section and copy the token')
        logging.info('4. Add the token to your environment variables')
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        logging.error(f'Failed to start bot: {e}')
