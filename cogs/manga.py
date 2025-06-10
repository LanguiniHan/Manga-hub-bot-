import discord
from discord.ext import commands
import aiohttp
import asyncio

class Manga(commands.Cog):
    """Manga lookup commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        """Clean up session when cog is unloaded"""
        asyncio.create_task(self.session.close())
    
    @commands.command(name='manga')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def manga_search(self, ctx, *, query):
        """Search for manga information"""
        async with ctx.typing():
            try:
                # Search MangaDex for manga
                search_url = "https://api.mangadex.org/manga"
                params = {
                    'title': query,
                    'limit': 1,
                    'includes[]': ['cover_art', 'author', 'artist']
                }
                
                async with self.session.get(search_url, params=params) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="❌ API Error",
                            description="Could not connect to MangaDex API.",
                            color=discord.Color.red()
                        )
                        return await ctx.send(embed=embed)
                    
                    data = await response.json()
                    
                    if not data.get('data'):
                        embed = discord.Embed(
                            title="❌ No Results",
                            description=f"No manga found for '{query}'.",
                            color=discord.Color.red()
                        )
                        return await ctx.send(embed=embed)
                    
                    manga = data['data'][0]
                    await self.send_manga_info(ctx, manga)
                    
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="❌ Timeout",
                    description="Request timed out. Please try again.",
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
    
    async def send_manga_info(self, ctx, manga_data):
        """Send formatted manga information"""
        try:
            attributes = manga_data['attributes']
            relationships = manga_data.get('relationships', [])
            
            # Get title (prefer English, fall back to others)
            title_obj = attributes.get('title', {})
            title = (title_obj.get('en') or 
                    title_obj.get('ja-ro') or 
                    title_obj.get('ja') or 
                    list(title_obj.values())[0] if title_obj else "Unknown Title")
            
            # Get description (prefer English)
            desc_obj = attributes.get('description', {})
            description = (desc_obj.get('en') or 
                          desc_obj.get('ja-ro') or 
                          list(desc_obj.values())[0] if desc_obj else "No description available.")
            
            # Truncate description if too long
            if len(description) > 300:
                description = description[:297] + "..."
            
            # Create embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue(),
                url=f"https://mangadex.org/title/{manga_data['id']}"
            )
            
            # Add basic info
            status = attributes.get('status', 'Unknown').title()
            embed.add_field(name="Status", value=status, inline=True)
            
            year = attributes.get('year')
            if year:
                embed.add_field(name="Year", value=str(year), inline=True)
            
            # Add tags (genres)
            tags = attributes.get('tags', [])
            if tags:
                genres = []
                for tag in tags[:5]:  # Limit to 5 genres
                    tag_name = tag.get('attributes', {}).get('name', {})
                    genre = tag_name.get('en', 'Unknown')
                    genres.append(genre)
                
                if genres:
                    embed.add_field(name="Genres", value=", ".join(genres), inline=False)
            
            # Get author/artist info
            authors = []
            artists = []
            
            for relationship in relationships:
                if relationship['type'] == 'author':
                    author_name = relationship.get('attributes', {}).get('name', 'Unknown')
                    authors.append(author_name)
                elif relationship['type'] == 'artist':
                    artist_name = relationship.get('attributes', {}).get('name', 'Unknown')
                    artists.append(artist_name)
            
            if authors:
                embed.add_field(name="Author(s)", value=", ".join(authors), inline=True)
            if artists:
                embed.add_field(name="Artist(s)", value=", ".join(artists), inline=True)
            
            # Try to get cover image
            cover_art = None
            for relationship in relationships:
                if relationship['type'] == 'cover_art':
                    cover_filename = relationship.get('attributes', {}).get('fileName')
                    if cover_filename:
                        cover_art = f"https://uploads.mangadex.org/covers/{manga_data['id']}/{cover_filename}.256.jpg"
                        break
            
            if cover_art:
                embed.set_thumbnail(url=cover_art)
            
            embed.set_footer(text="Data from MangaDex", icon_url="https://mangadex.org/favicon.ico")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Processing Data",
                description=f"Could not process manga information: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='randommanga')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def random_manga(self, ctx):
        """Get a random manga recommendation"""
        async with ctx.typing():
            try:
                # Get random manga from MangaDex
                search_url = "https://api.mangadex.org/manga/random"
                params = {
                    'includes[]': ['cover_art', 'author', 'artist']
                }
                
                async with self.session.get(search_url, params=params) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="❌ API Error",
                            description="Could not connect to MangaDex API.",
                            color=discord.Color.red()
                        )
                        return await ctx.send(embed=embed)
                    
                    data = await response.json()
                    manga = data.get('data')
                    
                    if not manga:
                        embed = discord.Embed(
                            title="❌ No Results",
                            description="Could not get random manga.",
                            color=discord.Color.red()
                        )
                        return await ctx.send(embed=embed)
                    
                    await self.send_manga_info(ctx, manga)
                    
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Manga(bot))
