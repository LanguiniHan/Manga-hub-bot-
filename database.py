import json
import os
import asyncio
from datetime import datetime

class Database:
    """Simple JSON-based database for bot data"""
    
    def __init__(self):
        self.db_file = "data/bot_database.json"
        self.ensure_data_dir()
        self.data = self.load_data()
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default structure
        return {
            "guilds": {},
            "users": {},
            "warnings": {},
            "music_queues": {}
        }
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    async def add_guild(self, guild_id):
        """Add a new guild to database"""
        guild_id = str(guild_id)
        if guild_id not in self.data["guilds"]:
            self.data["guilds"][guild_id] = {
                "prefix": "//",
                "log_channel": None,
                "created_at": datetime.now().isoformat()
            }
            self.save_data()
    
    async def remove_guild(self, guild_id):
        """Remove guild from database"""
        guild_id = str(guild_id)
        if guild_id in self.data["guilds"]:
            del self.data["guilds"][guild_id]
            self.save_data()
    
    async def get_guild_prefix(self, guild_id):
        """Get guild prefix"""
        guild_id = str(guild_id)
        return self.data["guilds"].get(guild_id, {}).get("prefix", "//")
    
    async def set_guild_prefix(self, guild_id, prefix):
        """Set guild prefix"""
        guild_id = str(guild_id)
        if guild_id not in self.data["guilds"]:
            await self.add_guild(guild_id)
        
        self.data["guilds"][guild_id]["prefix"] = prefix
        self.save_data()
    
    async def get_log_channel(self, guild_id):
        """Get log channel for guild"""
        guild_id = str(guild_id)
        return self.data["guilds"].get(guild_id, {}).get("log_channel")
    
    async def set_log_channel(self, guild_id, channel_id):
        """Set log channel for guild"""
        guild_id = str(guild_id)
        if guild_id not in self.data["guilds"]:
            await self.add_guild(guild_id)
        
        self.data["guilds"][guild_id]["log_channel"] = channel_id
        self.save_data()
    
    async def add_warning(self, guild_id, user_id, moderator_id, reason):
        """Add warning to user"""
        key = f"{guild_id}_{user_id}"
        if key not in self.data["warnings"]:
            self.data["warnings"][key] = []
        
        warning = {
            "moderator_id": moderator_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["warnings"][key].append(warning)
        self.save_data()
        
        return len(self.data["warnings"][key])
    
    async def get_warnings(self, guild_id, user_id):
        """Get user warnings"""
        key = f"{guild_id}_{user_id}"
        return self.data["warnings"].get(key, [])
    
    async def clear_warnings(self, guild_id, user_id):
        """Clear user warnings"""
        key = f"{guild_id}_{user_id}"
        if key in self.data["warnings"]:
            del self.data["warnings"][key]
            self.save_data()
