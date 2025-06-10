import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
from utils.music_queue import MusicQueue

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    """Music commands for voice channels"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
    
    def get_queue(self, guild_id):
        """Get or create music queue for guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    @commands.command(name='join')
    @commands.guild_only()
    async def join_voice(self, ctx):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Not in Voice Channel",
                description="You need to be in a voice channel to use this command.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        embed = discord.Embed(
            title="🎵 Joined Voice Channel",
            description=f"Connected to {channel.name}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='leave')
    @commands.guild_only()
    async def leave_voice(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client is None:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Clear the queue
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        
        await ctx.voice_client.disconnect()
        
        embed = discord.Embed(
            title="👋 Left Voice Channel",
            description="Disconnected from voice channel and cleared queue.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='play')
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play_music(self, ctx, *, query):
        """Play music from YouTube"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Not in Voice Channel",
                description="You need to be in a voice channel to play music.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Join voice channel if not connected
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                queue = self.get_queue(ctx.guild.id)
                
                # Add to queue
                song_info = {
                    'player': player,
                    'title': player.title,
                    'url': player.url,
                    'duration': player.duration,
                    'uploader': player.uploader,
                    'requester': ctx.author
                }
                
                queue.add(song_info)
                
                if not ctx.voice_client.is_playing():
                    await self.play_next(ctx)
                else:
                    embed = discord.Embed(
                        title="📝 Added to Queue",
                        description=f"**{player.title}** has been added to the queue.",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Position", value=f"{len(queue.songs)}", inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    await ctx.send(embed=embed)
                    
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error Playing Music",
                    description=f"An error occurred: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
    
    async def play_next(self, ctx):
        """Play the next song in queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if queue.is_empty():
            embed = discord.Embed(
                title="✅ Queue Finished",
                description="No more songs in queue.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return
        
        song = queue.get_next()
        if not song:
            return
        
        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            else:
                # Schedule next song
                asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        
        ctx.voice_client.play(song['player'], after=after_playing)
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{song['title']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Uploader", value=song['uploader'] or "Unknown", inline=True)
        embed.add_field(name="Requested by", value=song['requester'].mention, inline=True)
        
        if song['duration']:
            minutes, seconds = divmod(song['duration'], 60)
            embed.add_field(name="Duration", value=f"{int(minutes)}:{int(seconds):02d}", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='skip')
    @commands.guild_only()
    async def skip_song(self, ctx):
        """Skip the current song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            embed = discord.Embed(
                title="❌ Nothing Playing",
                description="No music is currently playing.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        ctx.voice_client.stop()
        
        embed = discord.Embed(
            title="⏭️ Song Skipped",
            description="Skipped to the next song.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stop')
    @commands.guild_only()
    async def stop_music(self, ctx):
        """Stop music and clear queue"""
        if not ctx.voice_client:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        # Clear queue and stop
        queue = self.get_queue(ctx.guild.id)
        queue.clear()
        ctx.voice_client.stop()
        
        embed = discord.Embed(
            title="⏹️ Music Stopped",
            description="Stopped music and cleared the queue.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='pause')
    @commands.guild_only()
    async def pause_music(self, ctx):
        """Pause the current song"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            embed = discord.Embed(
                title="⏸️ Music Paused",
                description="Music has been paused.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Nothing Playing",
                description="No music is currently playing.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='resume')
    @commands.guild_only()
    async def resume_music(self, ctx):
        """Resume the paused song"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            embed = discord.Embed(
                title="▶️ Music Resumed",
                description="Music has been resumed.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Music Not Paused",
                description="Music is not currently paused.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='queue')
    @commands.guild_only()
    async def show_queue(self, ctx):
        """Show the current music queue"""
        queue = self.get_queue(ctx.guild.id)
        
        if queue.is_empty():
            embed = discord.Embed(
                title="📝 Queue Empty",
                description="The music queue is empty.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(
            title="📝 Music Queue",
            color=discord.Color.blue()
        )
        
        # Show up to 10 songs
        for i, song in enumerate(queue.songs[:10], 1):
            duration_str = ""
            if song['duration']:
                minutes, seconds = divmod(song['duration'], 60)
                duration_str = f" ({int(minutes)}:{int(seconds):02d})"
            
            embed.add_field(
                name=f"{i}. {song['title']}{duration_str}",
                value=f"Requested by {song['requester'].mention}",
                inline=False
            )
        
        if len(queue.songs) > 10:
            embed.add_field(
                name="...",
                value=f"And {len(queue.songs) - 10} more songs",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume')
    @commands.guild_only()
    async def change_volume(self, ctx, volume: int):
        """Change the music volume (0-100)"""
        if not ctx.voice_client:
            embed = discord.Embed(
                title="❌ Not Connected",
                description="I'm not connected to a voice channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if not 0 <= volume <= 100:
            embed = discord.Embed(
                title="❌ Invalid Volume",
                description="Volume must be between 0 and 100.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        ctx.voice_client.source.volume = volume / 100
        
        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to {volume}%",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
