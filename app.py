import webview
import MusicUtilities
import os

# cria janela ANTES de definir PlaySong
class api: # Metodos que vão estar expostos para o JavaScript
    def __init__(self):
        self.current_song = None

    def set_current_song(self, song_name):
        PlaySong(song_name)
        return song_name

    def on_song_end(self):
        print("[Python] Música terminou.")

    def test(self):
        print("[Python] Teste chamado com sucesso!")
        PlaySong("songs/LavaRushOst.wav")
        return "Teste chamado com sucesso!"
    

html_path = os.path.abspath('web/index.html')
url = f'file://{html_path}'
music_utilities = MusicUtilities.MusicUtilities()


window = webview.create_window(
    'MyBand Player',
    url,
    js_api=api(),
    width=500,
    height=600,
    resizable=False,
    fullscreen=False
)

def PlaySong(song_path):
    """Play a song from the given path."""
    # Agora 'window' está acessível aqui
    # window.get_elements('song-name-text').text = f'Now Playing: {os.path.basename(song_path)}'
    music_utilities.play_song(song_path)
    


if __name__ == '__main__':
    webview.start(debug=True)
