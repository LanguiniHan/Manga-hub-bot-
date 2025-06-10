import asyncio
from collections import deque
import random

class MusicQueue:
    """Music queue management for the bot"""
    
    def __init__(self):
        self.songs = deque()
        self.current_song = None
        self.repeat_mode = "off"  # off, song, queue
        self.shuffle = False
        self.volume = 0.5
    
    def add(self, song_info):
        """Add a song to the queue"""
        self.songs.append(song_info)
    
    def get_next(self):
        """Get the next song from the queue"""
        if self.repeat_mode == "song" and self.current_song:
            return self.current_song
        
        if not self.songs:
            if self.repeat_mode == "queue" and self.current_song:
                # If queue is empty but we're repeating queue, don't play anything
                return None
            return None
        
        if self.shuffle:
            # Remove a random song from queue
            index = random.randint(0, len(self.songs) - 1)
            song = self.songs[index]
            del self.songs[index]
        else:
            # Remove first song from queue
            song = self.songs.popleft()
        
        self.current_song = song
        
        # If repeating queue, add song back to end
        if self.repeat_mode == "queue":
            self.songs.append(song.copy())
        
        return song
    
    def skip(self):
        """Skip current song"""
        if self.repeat_mode == "song":
            self.repeat_mode = "off"  # Temporarily disable repeat to skip
            next_song = self.get_next()
            self.repeat_mode = "song"  # Re-enable repeat
            return next_song
        return self.get_next()
    
    def clear(self):
        """Clear the entire queue"""
        self.songs.clear()
        self.current_song = None
    
    def remove(self, index):
        """Remove a song at specific index"""
        if 0 <= index < len(self.songs):
            removed = self.songs[index]
            del self.songs[index]
            return removed
        return None
    
    def move(self, from_index, to_index):
        """Move a song from one position to another"""
        if (0 <= from_index < len(self.songs) and 
            0 <= to_index < len(self.songs)):
            song = self.songs[from_index]
            del self.songs[from_index]
            self.songs.insert(to_index, song)
            return True
        return False
    
    def set_repeat(self, mode):
        """Set repeat mode: off, song, queue"""
        if mode in ["off", "song", "queue"]:
            self.repeat_mode = mode
            return True
        return False
    
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle = not self.shuffle
        return self.shuffle
    
    def is_empty(self):
        """Check if queue is empty"""
        return len(self.songs) == 0
    
    def size(self):
        """Get queue size"""
        return len(self.songs)
    
    def get_queue_list(self):
        """Get list of songs in queue for display"""
        return list(self.songs)
    
    def get_current_info(self):
        """Get current song information"""
        return self.current_song
    
    def get_next_songs(self, count=5):
        """Get next few songs without removing them"""
        return list(self.songs)[:count]
    
    def insert_next(self, song_info):
        """Insert song to play next"""
        self.songs.appendleft(song_info)
    
    def search_queue(self, query):
        """Search for songs in queue by title"""
        results = []
        for i, song in enumerate(self.songs):
            if query.lower() in song.get('title', '').lower():
                results.append((i, song))
        return results
    
    def get_total_duration(self):
        """Get total duration of all songs in queue"""
        total = 0
        for song in self.songs:
            duration = song.get('duration')
            if duration:
                total += duration
        return total
    
    def duplicate_check(self, url):
        """Check if URL already exists in queue"""
        for song in self.songs:
            if song.get('url') == url:
                return True
        return False
