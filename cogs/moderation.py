import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Moderation(commands.Cog):
    """Moderation commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def has_admin_role(ctx):
        """Check if user has admin role or permissions"""
        if ctx.author.guild_permissions.administrator:
            return True
        
        admin_roles = ['admin', 'administrator', 'mod', 'moderator']
        user_roles = [role.name.lower() for role in ctx.author.roles]
        
        return any(role in admin_roles for role in user_roles)
    
    @commands.command(name='ban')
    @commands.guild_only()
    @commands.check(has_admin_role)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server"""
        try:
            # Check if bot can ban this member
            if member.top_role >= ctx.guild.me.top_role:
                embed = discord.Embed(
                    title="❌ Cannot Ban Member",
                    description="I cannot ban this member due to role hierarchy.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # Check if member is bot owner or has higher role than command user
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                embed = discord.Embed(
                    title="❌ Cannot Ban Member",
                    description="You cannot ban this member due to role hierarchy.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # Ban the member
            await member.ban(reason=f"Banned by {ctx.author}: {reason}")
            
            # Create embed
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_action(ctx.guild, "BAN", ctx.author, member, reason)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to ban members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='kick')
    @commands.guild_only()
    @commands.check(has_admin_role)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server"""
        try:
            # Similar checks as ban
            if member.top_role >= ctx.guild.me.top_role:
                embed = discord.Embed(
                    title="❌ Cannot Kick Member",
                    description="I cannot kick this member due to role hierarchy.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                embed = discord.Embed(
                    title="❌ Cannot Kick Member",
                    description="You cannot kick this member due to role hierarchy.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # Kick the member
            await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_action(ctx.guild, "KICK", ctx.author, member, reason)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to kick members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='warn')
    @commands.guild_only()
    @commands.check(has_admin_role)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def warn_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member"""
        try:
            # Add warning to database
            warning_count = await self.bot.db.add_warning(
                ctx.guild.id, member.id, ctx.author.id, reason
            )
            
            embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}\n**Warning Count:** {warning_count}",
                color=discord.Color.yellow(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="⚠️ You've been warned",
                    description=f"**Server:** {ctx.guild.name}\n**Moderator:** {ctx.author}\n**Reason:** {reason}\n**Total Warnings:** {warning_count}",
                    color=discord.Color.yellow()
                )
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Log the action
            await self.log_action(ctx.guild, "WARN", ctx.author, member, reason)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='warnings')
    @commands.guild_only()
    @commands.check(has_admin_role)
    async def check_warnings(self, ctx, member: discord.Member):
        """Check warnings for a member"""
        warnings = await self.bot.db.get_warnings(ctx.guild.id, member.id)
        
        if not warnings:
            embed = discord.Embed(
                title="📋 No Warnings",
                description=f"{member.mention} has no warnings.",
                color=discord.Color.green()
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="📋 Warning History",
            description=f"**Member:** {member.mention}\n**Total Warnings:** {len(warnings)}",
            color=discord.Color.yellow()
        )
        
        for i, warning in enumerate(warnings[-5:], 1):  # Show last 5 warnings
            moderator = ctx.guild.get_member(warning['moderator_id'])
            mod_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Moderator:** {mod_name}\n**Reason:** {warning['reason']}\n**Date:** {warning['timestamp'][:10]}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='quarantine')
    @commands.guild_only()
    @commands.check(has_admin_role)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quarantine_user(self, ctx, member: discord.Member, duration: int = 60, *, reason="No reason provided"):
        """Quarantine a member (timeout)"""
        try:
            # Calculate timeout duration
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            
            # Apply timeout
            await member.timeout(timeout_until, reason=f"Quarantined by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="🔒 Member Quarantined",
                description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Duration:** {duration} minutes\n**Reason:** {reason}",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_action(ctx.guild, "QUARANTINE", ctx.author, member, f"{reason} ({duration} minutes)")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to timeout members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='hackban')
    @commands.guild_only()
    @commands.check(has_admin_role)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hackban_user(self, ctx, user_id: int, *, reason="No reason provided"):
        """Ban a user by ID (hackban)"""
        try:
            # Try to get user object
            user = await self.bot.fetch_user(user_id)
            
            # Check if user is already in guild
            member = ctx.guild.get_member(user_id)
            if member:
                embed = discord.Embed(
                    title="❌ User in Server",
                    description="This user is in the server. Use the regular ban command instead.",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)
            
            # Ban the user
            await ctx.guild.ban(user, reason=f"Hackban by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="🔨 User Hackbanned",
                description=f"**User:** {user.name}#{user.discriminator} ({user_id})\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_action(ctx.guild, "HACKBAN", ctx.author, user, reason)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ User Not Found",
                description="Could not find a user with that ID.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to ban users.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    async def log_action(self, guild, action, moderator, target, reason):
        """Log moderation action to log channel"""
        log_channel_id = await self.bot.db.get_log_channel(guild.id)
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(log_channel_id)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"🛡️ Moderation Action: {action}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="Target", value=f"{target.name}#{target.discriminator}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"User ID: {target.id}")
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass  # Channel might not exist or no permissions

async def setup(bot):
    await bot.add_cog(Moderation(bot))
