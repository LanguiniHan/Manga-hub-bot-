import os

class Config:
    """Configuration class for the Discord bot"""
    
    # Bot settings
    DEFAULT_PREFIX = "x!"
    BOT_NAME = "Multi-Purpose Bot"
    BOT_VERSION = "1.0.0"
    
    # Colors
    PRIMARY_COLOR = 0x7289DA
    SUCCESS_COLOR = 0x00FF00
    ERROR_COLOR = 0xFF0000
    WARNING_COLOR = 0xFFFF00
    
    # Music settings
    MAX_VOLUME = 100
    DEFAULT_VOLUME = 50
    MAX_QUEUE_SIZE = 50
    
    # Command cooldowns (in seconds)
    MODERATION_COOLDOWN = 5
    MUSIC_COOLDOWN = 3
    UTILITY_COOLDOWN = 2
    
    # API URLs
    MANGADEX_API = "https://api.mangadex.org"
    
    # File paths
    DATABASE_FILE = "data/bot_database.json"
    CONFIG_FILE = "data/server_configs.json"
    
    # Permissions
    ADMIN_PERMISSIONS = [
        "administrator",
        "manage_guild",
        "manage_channels",
        "manage_roles",
        "ban_members",
        "kick_members"
    ]
    
    @staticmethod
    def get_api_key(service):
        """Get API key for specific service"""
        return os.getenv(f'{service.upper()}_API_KEY', '')
