import discord
from discord.ext import commands
import time
import platform
import psutil
from datetime import datetime

class Utility(commands.Cog):
    """Utility commands for general use"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """Check bot latency"""
        start_time = time.time()
        message = await ctx.send("Pinging...")
        end_time = time.time()
        
        # Calculate latencies
        api_latency = round(self.bot.latency * 1000)
        message_latency = round((end_time - start_time) * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green()
        )
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Message Latency", value=f"{message_latency}ms", inline=True)
        
        # Color based on latency
        if api_latency < 100:
            embed.color = discord.Color.green()
        elif api_latency < 200:
            embed.color = discord.Color.orange()
        else:
            embed.color = discord.Color.red()
        
        await message.edit(content=None, embed=embed)
    
    @commands.command(name='avatar', aliases=['av'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def avatar(self, ctx, member: discord.Member = None):
        """Display user's avatar"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=member.color or discord.Color.blue()
        )
        
        # Get avatar URL
        avatar_url = member.display_avatar.url
        embed.set_image(url=avatar_url)
        
        # Add download links
        embed.add_field(
            name="Download Links",
            value=f"[PNG]({avatar_url}?format=png) | [JPG]({avatar_url}?format=jpg) | [WEBP]({avatar_url}?format=webp)",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='banner')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def banner(self, ctx, member: discord.Member = None):
        """Display user's banner"""
        if member is None:
            member = ctx.author
        
        # Need to fetch user to get banner
        try:
            user = await self.bot.fetch_user(member.id)
            
            if not user.banner:
                embed = discord.Embed(
                    title="❌ No Banner",
                    description=f"{member.display_name} doesn't have a banner set.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            embed = discord.Embed(
                title=f"{member.display_name}'s Banner",
                color=member.color or discord.Color.blue()
            )
            
            banner_url = user.banner.url
            embed.set_image(url=banner_url)
            
            # Add download links
            embed.add_field(
                name="Download Links",
                value=f"[PNG]({banner_url}?format=png) | [JPG]({banner_url}?format=jpg) | [WEBP]({banner_url}?format=webp)",
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Could not fetch banner: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='userinfo', aliases=['ui'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, member: discord.Member = None):
        """Display information about a user"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title="User Information",
            color=member.color or discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic info
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        
        # Dates
        embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
        
        # Status
        status_emoji = {
            'online': '🟢',
            'idle': '🟡',
            'dnd': '🔴',
            'offline': '⚫'
        }
        embed.add_field(name="Status", value=f"{status_emoji.get(str(member.status), '❓')} {str(member.status).title()}", inline=True)
        
        # Roles
        if len(member.roles) > 1:
            roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
            if len(roles) > 10:
                roles = roles[:10] + [f"... and {len(roles) - 10} more"]
            embed.add_field(name=f"Roles ({len(member.roles) - 1})", value=" ".join(roles), inline=False)
        
        # Permissions
        if member.guild_permissions.administrator:
            embed.add_field(name="Key Permissions", value="Administrator", inline=True)
        else:
            key_perms = []
            perms_to_check = [
                ('manage_guild', 'Manage Server'),
                ('manage_channels', 'Manage Channels'),
                ('manage_roles', 'Manage Roles'),
                ('ban_members', 'Ban Members'),
                ('kick_members', 'Kick Members'),
                ('manage_messages', 'Manage Messages')
            ]
            
            for perm, name in perms_to_check:
                if getattr(member.guild_permissions, perm):
                    key_perms.append(name)
            
            if key_perms:
                embed.add_field(name="Key Permissions", value=", ".join(key_perms), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='serverinfo', aliases=['si'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def serverinfo(self, ctx):
        """Display information about the server"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"Server Information - {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Basic info
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        # Counts
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        # Boost info
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        
        # Features
        if guild.features:
            features = [feature.replace('_', ' ').title() for feature in guild.features]
            embed.add_field(name="Features", value=", ".join(features[:5]), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='botinfo')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def botinfo(self, ctx):
        """Display information about the bot"""
        embed = discord.Embed(
            title="Bot Information",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Basic info
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
        # System info
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        
        # Performance
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
            embed.add_field(name="Memory Usage", value=f"{memory.percent}%", inline=True)
        except:
            pass
        
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Uptime
        uptime = datetime.utcnow() - self.bot.start_time if hasattr(self.bot, 'start_time') else None
        if uptime:
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx, *, command_name=None):
        """Display help information"""
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name.lower())
            if not command:
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"No command named '{command_name}' found.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            embed = discord.Embed(
                title=f"Help - {command.name}",
                description=command.help or "No description available.",
                color=discord.Color.blue()
            )
            
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
            
            usage = f"{await self.bot.get_prefix(ctx.message)}{command.name}"
            if command.signature:
                usage += f" {command.signature}"
            embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
            
            await ctx.send(embed=embed)
            return
        
        # Show general help
        prefix = await self.bot.get_prefix(ctx.message)
        
        embed = discord.Embed(
            title="🤖 Bot Help",
            description=f"Use `{prefix}help <command>` for detailed information about a command.",
            color=discord.Color.blue()
        )
        
        # Moderation commands
        moderation_commands = [
            "ban", "kick", "warn", "warnings", "quarantine", "hackban"
        ]
        embed.add_field(
            name="🛡️ Moderation (Admin Only)",
            value=f"`{prefix}" + f"`, `{prefix}".join(moderation_commands) + "`",
            inline=False
        )
        
        # Music commands
        music_commands = [
            "join", "leave", "play", "skip", "stop", "pause", "resume", "queue", "volume"
        ]
        embed.add_field(
            name="🎵 Music",
            value=f"`{prefix}" + f"`, `{prefix}".join(music_commands) + "`",
            inline=False
        )
        
        # Manga commands
        manga_commands = [
            "manga", "randomanga"
        ]
        embed.add_field(
            name="📚 Manga",
            value=f"`{prefix}" + f"`, `{prefix}".join(manga_commands) + "`",
            inline=False
        )
        
        # Utility commands
        utility_commands = [
            "ping", "avatar", "banner", "userinfo", "serverinfo", "botinfo"
        ]
        embed.add_field(
            name="🔧 Utility",
            value=f"`{prefix}" + f"`, `{prefix}".join(utility_commands) + "`",
            inline=False
        )
        
        # Admin commands
        admin_commands = [
            "setprefix", "setlogchannel"
        ]
        embed.add_field(
            name="⚙️ Admin",
            value=f"`{prefix}" + f"`, `{prefix}".join(admin_commands) + "`",
            inline=False
        )
        
        embed.set_footer(text=f"Current prefix: {prefix}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
