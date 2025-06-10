import discord
from discord.ext import commands

class Admin(commands.Cog):
    """Admin commands for server configuration"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def has_admin_permissions(ctx):
        """Check if user has admin permissions"""
        return ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner
    
    @commands.command(name='setprefix')
    @commands.guild_only()
    @commands.check(has_admin_permissions)
    async def set_prefix(self, ctx, *, new_prefix=None):
        """Set the server prefix"""
        if not new_prefix:
            current_prefix = await self.bot.db.get_guild_prefix(ctx.guild.id)
            embed = discord.Embed(
                title="📝 Current Prefix",
                description=f"The current prefix for this server is: `{current_prefix}`",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Usage",
                value=f"`{current_prefix}setprefix <new_prefix>`",
                inline=False
            )
            return await ctx.send(embed=embed)
        
        # Validate prefix
        if len(new_prefix) > 5:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix cannot be longer than 5 characters.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if '`' in new_prefix or '@' in new_prefix:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="Prefix cannot contain backticks (`) or mentions (@).",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Set new prefix
        await self.bot.db.set_guild_prefix(ctx.guild.id, new_prefix)
        
        embed = discord.Embed(
            title="✅ Prefix Updated",
            description=f"Server prefix has been changed to: `{new_prefix}`",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Example Usage",
            value=f"`{new_prefix}help`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='setlogchannel')
    @commands.guild_only()
    @commands.check(has_admin_permissions)
    async def set_log_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the logging channel for moderation actions"""
        if not channel:
            # Show current log channel
            log_channel_id = await self.bot.db.get_log_channel(ctx.guild.id)
            if not log_channel_id:
                embed = discord.Embed(
                    title="📋 No Log Channel",
                    description="No log channel is currently set for this server.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Usage",
                    value=f"`{await self.bot.get_prefix(ctx.message)}setlogchannel #channel`",
                    inline=False
                )
                return await ctx.send(embed=embed)
            
            log_channel = ctx.guild.get_channel(log_channel_id)
            if not log_channel:
                embed = discord.Embed(
                    title="❌ Invalid Log Channel",
                    description="The set log channel no longer exists.",
                    color=discord.Color.red()
                )
                # Clear the invalid channel
                await self.bot.db.set_log_channel(ctx.guild.id, None)
                return await ctx.send(embed=embed)
            
            embed = discord.Embed(
                title="📋 Current Log Channel",
                description=f"The current log channel is: {log_channel.mention}",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # Check if bot can send messages to the channel
        if not channel.permissions_for(ctx.guild.me).send_messages:
            embed = discord.Embed(
                title="❌ No Permission",
                description=f"I don't have permission to send messages in {channel.mention}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Set log channel
        await self.bot.db.set_log_channel(ctx.guild.id, channel.id)
        
        embed = discord.Embed(
            title="✅ Log Channel Set",
            description=f"Moderation logs will now be sent to {channel.mention}.",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
        
        # Send test message to log channel
        test_embed = discord.Embed(
            title="🛡️ Log Channel Configured",
            description="This channel has been set as the moderation log channel.",
            color=discord.Color.blue()
        )
        test_embed.add_field(
            name="Configured by",
            value=ctx.author.mention,
            inline=True
        )
        test_embed.set_footer(text="Moderation actions will be logged here")
        
        try:
            await channel.send(embed=test_embed)
        except:
            pass  # If we can't send the test message, that's okay
    
    @commands.command(name='clearlogchannel')
    @commands.guild_only()
    @commands.check(has_admin_permissions)
    async def clear_log_channel(self, ctx):
        """Clear the current log channel"""
        current_channel_id = await self.bot.db.get_log_channel(ctx.guild.id)
        
        if not current_channel_id:
            embed = discord.Embed(
                title="❌ No Log Channel",
                description="No log channel is currently set.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        await self.bot.db.set_log_channel(ctx.guild.id, None)
        
        embed = discord.Embed(
            title="✅ Log Channel Cleared",
            description="The log channel has been removed. Moderation actions will no longer be logged.",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='settings')
    @commands.guild_only()
    @commands.check(has_admin_permissions)
    async def show_settings(self, ctx):
        """Show current server settings"""
        prefix = await self.bot.db.get_guild_prefix(ctx.guild.id)
        log_channel_id = await self.bot.db.get_log_channel(ctx.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Server Settings",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Prefix", value=f"`{prefix}`", inline=True)
        
        if log_channel_id:
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                embed.add_field(name="Log Channel", value=log_channel.mention, inline=True)
            else:
                embed.add_field(name="Log Channel", value="❌ Invalid Channel", inline=True)
                # Clear invalid channel
                await self.bot.db.set_log_channel(ctx.guild.id, None)
        else:
            embed.add_field(name="Log Channel", value="Not Set", inline=True)
        
        embed.set_footer(text=f"Server ID: {ctx.guild.id}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
