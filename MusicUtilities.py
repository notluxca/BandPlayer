import pygame


class MusicUtilities:
    def __init__(self):
        # Initialize Pygame mixer
        pygame.mixer.init()

    def play_song(self, song_path):
        """Play a song from the given path."""
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

    def advance_song_time(self, seconds):
        """Advance the song time by a specified number of seconds."""
        current_time = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
        new_time = current_time + seconds
        pygame.mixer.music.set_pos(new_time)

    def next_song(self, playlist, current_index):
        """Get the next song in the playlist."""
        next_index = (current_index + 1) % len(playlist)
        return playlist[next_index]