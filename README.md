# Discord Multi-Purpose Bot

A comprehensive Discord bot with moderation, music playback, manga lookup, and utility features.

## Features

### 🛡️ Moderation Commands (Admin Only)
- `x!ban <user> [reason]` - Ban a member from the server
- `x!kick <user> [reason]` - Kick a member from the server
- `x!warn <user> [reason]` - Warn a member
- `x!warnings <user>` - Check warnings for a member
- `x!quarantine <user> [duration] [reason]` - Quarantine (timeout) a member
- `x!hackban <user_id> [reason]` - Ban a user by ID who isn't in the server

### 🎵 Music Commands
- `x!join` - Join your voice channel
- `x!leave` - Leave the voice channel
- `x!play <song/url>` - Play music from YouTube
- `x!skip` - Skip the current song
- `x!stop` - Stop music and clear queue
- `x!pause` - Pause the current song
- `x!resume` - Resume the paused song
- `x!queue` - Show the current music queue
- `x!volume <0-100>` - Change the music volume

### 📚 Manga Commands
- `x!manga <title>` - Search for manga information from MangaDex
- `x!randommanga` - Get a random manga recommendation

### 🔧 Utility Commands
- `x!ping` - Check bot latency
- `x!avatar [user]` - Display user's avatar
- `x!banner [user]` - Display user's banner
- `x!userinfo [user]` - Display information about a user
- `x!serverinfo` - Display information about the server
- `x!botinfo` - Display information about the bot

### ⚙️ Admin Commands
- `x!setprefix <prefix>` - Change the server prefix (default: x!)
- `x!setlogchannel <channel>` - Set the logging channel for moderation actions
- `x!clearlogchannel` - Clear the current log channel
- `x!settings` - Show current server settings

### 📝 Help Command
- `x!help` - Show all commands
- `x!help <command>` - Show detailed help for a specific command

## Setup Instructions

### 1. Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Copy the bot token (keep this secret!)

### 2. Configure Bot Permissions
In the "Bot" section, enable these privileged intents:
- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ Message Content Intent

### 3. Invite Bot to Server
1. Go to "OAuth2" > "URL Generator" in your application
2. Select "bot" in scopes
3. Select these permissions:
   - Send Messages
   - Read Message History
   - Use Slash Commands
   - Connect (for voice)
   - Speak (for voice)
   - Ban Members
   - Kick Members
   - Manage Messages
   - Moderate Members
4. Copy the generated URL and open it to invite the bot

### 4. Set Environment Variables
You need to set your Discord bot token as an environment variable:

**In Replit:**
1. Go to the "Secrets" tab (lock icon) in your Replit
2. Add a new secret:
   - Key: `DISCORD_TOKEN`
   - Value: Your bot token from step 1

**Locally:**
```bash
export DISCORD_TOKEN="your_bot_token_here"
```

### 5. Run the Bot
```bash
python main.py
```

## Configuration

### Default Settings
- **Prefix:** `x!` (can be changed per server)
- **Admin Permissions:** Administrator, Manage Server, Manage Channels, Manage Roles, Ban Members, Kick Members

### Server-Specific Settings
Each server can customize:
- Command prefix
- Moderation log channel
- All settings are automatically saved

## Requirements

- Python 3.8+
- discord.py
- yt-dlp
- aiohttp
- psutil
- pynacl (for voice support)

All dependencies are automatically installed when running the bot.

## File Structure

```
├── main.py                 # Main bot file
├── config.py              # Configuration settings
├── database.py            # Simple JSON database
├── cogs/
│   ├── admin.py           # Admin commands
│   ├── moderation.py      # Moderation commands
│   ├── music.py           # Music commands
│   ├── manga.py           # Manga lookup commands
│   └── utility.py         # Utility commands
├── utils/
│   ├── helpers.py         # Helper functions
│   └── music_queue.py     # Music queue management
└── data/
    └── server_configs.json # Server configurations
```

## Features Overview

### 🔄 24/7 Uptime
The bot includes a keep-alive system that runs every 30 minutes to maintain connection.

### 🗃️ Data Storage
Uses a simple JSON-based database for:
- Server prefixes
- Log channels
- User warnings
- Music queues

### 🛡️ Security
- Admin commands require proper permissions
- Role hierarchy checks for moderation actions
- Error handling for invalid operations

### 🎵 Music Features
- YouTube integration via yt-dlp
- Queue management with repeat and shuffle
- Volume control
- Voice channel auto-join

### 📚 Manga Integration
- Real-time data from MangaDex API
- Detailed manga information
- Cover art display
- Random recommendations

## Troubleshooting

### Bot Not Responding
1. Check if bot token is set correctly
2. Verify bot has necessary permissions
3. Ensure bot is online in Discord

### Music Not Working
1. Check voice permissions
2. Verify PyNaCl is installed
3. Ensure bot can connect to voice channels

### Commands Not Working
1. Check server prefix with `//settings`
2. Verify user has required permissions
3. Check bot has Send Messages permission

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all setup steps are completed
3. Check console logs for error messages

## License

This project is open source and available under the MIT License.