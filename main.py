import tkinter
import customtkinter
import pygame
from PIL import Image, ImageTk
from threading import Thread
import time

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

FONT = ("Segoe UI", 12)

class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MyBand')
        self.root.geometry('750x480') # Aumentado para acomodar melhor os elementos
        self.root.resizable(False, False)
        pygame.mixer.init()

        self.list_of_songs = [
            'music/A Great Day for Freedom.mp3',
            'music/Cluster One - Pink Floyd.mp3',
            'music/Keep Talking - Pink Floyd.mp3',
            'music/Marooned - Pink Floyd.mp3',
            'music/Pink Floyd - Coming Back To Life.mp3',
            'music/Pink Floyd - High Hopes.mp3',
            'music/Pink Floyd - Lost For Words.mp3',
            'music/Pink Floyd - Wearing The Inside Out.mp3',
            'music/Pink Floyd - What Do You Want From Me.mp3',
            'music/Poles Apart - Pink Floyd.mp3',
            'music/Take It Back - Pink Floyd.mp3',
        ]
        self.current_song_index = 0
        self.song_length = 0
        self.user_seeking = False
        self.playback_thread = None
        self.playback_start_time = 0
        self.seek_offset = 0
        self.paused = False

        self.single_cover_art_path = 'img/CoverArt.jpg'

        self._create_widgets()
        self.play_music() # Play the first song on startup

    def _create_widgets(self):
        # Frame da Lista de Músicas
        self.song_list_frame = customtkinter.CTkFrame(master=self.root, width=300, corner_radius=0)
        self.song_list_frame.pack(side='left', fill='y')
        self.song_list_frame.pack_propagate(False) # Impede que o frame se encolha

        song_list_label = customtkinter.CTkLabel(master=self.song_list_frame, text="Músicas", anchor="w", font=FONT)
        song_list_label.pack(padx=10, pady=(10, 0), anchor="w")

        self.song_listbox = tkinter.Listbox(
            self.song_list_frame,
            bg='#1e1e1e',
            fg='white',
            borderwidth=0,
            highlightthickness=0,
            font=FONT,
            selectbackground='#2A2D2E',
            selectforeground='white'
        )
        self.song_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.song_listbox.bind('<<ListboxSelect>>', self.on_song_select)

        for song in self.list_of_songs:
            song_name = song[6:-4] # Remove 'music/' e '.mp3'
            self.song_listbox.insert(tkinter.END, song_name)

        # Offsets para os elementos à direita da lista de músicas
        # A lista de músicas ocupa 300px. A largura total é 800px.
        # A área disponível para os controles é 800 - 300 = 500px.
        # O centro dessa área é 300 + (500 / 2) = 550px.
        # Em termos de relx (proporção da largura total), isso é 550 / 800 = 0.6875.
        # Usaremos 0.68 para arredondar e facilitar o ajuste visual.
        center_relx_offset = 0.68

        # Capa do Álbum e Rótulo do Nome da Música
        self.album_cover_label = customtkinter.CTkLabel(self.root, text="")
        self.album_cover_label.place(relx=center_relx_offset, rely=.06, anchor=tkinter.N) # Ajustado o anchor para o topo

        self.song_name_label = customtkinter.CTkLabel(master=self.root, text="", font=FONT)
        self.song_name_label.place(relx=center_relx_offset, rely=.61, anchor=tkinter.CENTER)

        # Botões de Controle (Play/Pause, Skip)
        self.play_pause_button = customtkinter.CTkButton(master=self.root, text='Play', command=self.toggle_play_pause, font=FONT)
        self.play_pause_button.place(relx=center_relx_offset, rely=0.7, anchor=tkinter.CENTER)

        # Ajuste a posição dos botões de pular em relação ao botão Play/Pause
        # Por exemplo, se o botão Play/Pause está em center_relx_offset,
        # o botão 'pular para trás' pode estar em center_relx_offset - 0.08
        # e o 'pular para frente' em center_relx_offset + 0.08
        skip_b_button = customtkinter.CTkButton(master=self.root, text='<', command=self.skip_back, width=2, font=FONT)
        skip_b_button.place(relx=center_relx_offset - 0.08, rely=0.7, anchor=tkinter.CENTER)

        skip_f_button = customtkinter.CTkButton(master=self.root, text='>', command=self.skip_forward, width=2, font=FONT)
        skip_f_button.place(relx=center_relx_offset + 0.08, rely=0.7, anchor=tkinter.CENTER)


        # Controle de Volume
        volume_label = customtkinter.CTkLabel(master=self.root, text="Volume:", font=FONT)
        # Ajustado o relx para o label do volume
        volume_label.place(relx=center_relx_offset - 0.12, rely=0.78, anchor=tkinter.E)

        self.volume_slider = customtkinter.CTkSlider(master=self.root, from_=0, to=1, command=self.set_volume, width=210)
        self.volume_slider.set(0.5)
        self.volume_slider.place(relx=center_relx_offset + 0.02, rely=0.78, anchor=tkinter.CENTER)

        # Slider de Progresso da Música
        self.song_slider = customtkinter.CTkSlider(master=self.root, from_=0, to=100, width=250)
        self.song_slider.place(relx=center_relx_offset, rely=0.85, anchor=tkinter.CENTER)
        self.song_slider.bind("<Button-1>", self.start_seek)
        self.song_slider.bind("<ButtonRelease-1>", self.end_seek)

        self.time_label = customtkinter.CTkLabel(master=self.root, text="00:00 / 00:00", font=FONT)
        self.time_label.place(relx=center_relx_offset, rely=0.9, anchor=tkinter.CENTER)

    def format_time(self, seconds):
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes:02}:{sec:02}"

    def get_album_cover(self, song_path):
        image1 = Image.open(self.single_cover_art_path)
        image2 = image1.resize((250, 250))
        load = ImageTk.PhotoImage(image2)

        self.album_cover_label.configure(image=load)
        self.album_cover_label.image = load # Mantém uma referência para evitar que a imagem seja coletada pelo garbage collector

        stripped_string = song_path[6:-4] # Assumes 'music/' and '.mp3'
        self.song_name_label.configure(text=stripped_string)

    def update_progress_slider(self):
        while pygame.mixer.music.get_busy() or self.user_seeking or self.paused:
            try:
                if not self.user_seeking and not self.paused:
                    current_pos = time.time() - self.playback_start_time + self.seek_offset
                    current_pos = min(current_pos, self.song_length)
                    self.song_slider.set(current_pos)
                    self.time_label.configure(text=f"{self.format_time(current_pos)} / {self.format_time(self.song_length)}")
                elif self.paused:
                    # Quando pausado, time_label deve mostrar a posição atual pausada
                    current_pos = self.song_slider.get()
                    self.time_label.configure(text=f"{self.format_time(current_pos)} / {self.format_time(self.song_length)}")
            except:
                pass
            time.sleep(0.1)

        # Quando a música para ou é explicitamente encerrada
        if not pygame.mixer.music.get_busy() and not self.user_seeking and not self.paused:
            self.song_slider.set(0)
            self.time_label.configure(text=f"00:00 / {self.format_time(self.song_length)}")
            self.skip_forward() # Toca a próxima música automaticamente

    def start_playback_thread(self):
        if self.playback_thread and self.playback_thread.is_alive():
            return
        self.playback_thread = Thread(target=self.update_progress_slider, daemon=True)
        self.playback_thread.start()

    def play_music(self):
        self.paused = False
        self.user_seeking = False
        song_path = self.list_of_songs[self.current_song_index]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)
        pygame.mixer.music.set_volume(self.volume_slider.get())
        self.play_pause_button.configure(text="Pause")

        sound = pygame.mixer.Sound(song_path)
        self.song_length = sound.get_length()
        self.song_slider.configure(to=self.song_length)
        self.song_slider.set(0)

        self.playback_start_time = time.time()
        self.seek_offset = 0

        self.get_album_cover(song_path)
        self.time_label.configure(text=f"00:00 / {self.format_time(self.song_length)}")
        self.start_playback_thread()

        self.song_listbox.select_clear(0, tkinter.END)
        self.song_listbox.select_set(self.current_song_index)
        self.song_listbox.activate(self.current_song_index)
        self.song_listbox.see(self.current_song_index)

    def toggle_play_pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            # Recalcula playback_start_time para retomar do ponto correto
            self.playback_start_time = time.time() - (self.song_slider.get() - self.seek_offset)
            self.play_pause_button.configure(text="Pause")
            self.start_playback_thread() # Reinicia a thread se ela tiver morrido enquanto pausada
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_pause_button.configure(text="Play")

    def skip_forward(self):
        self.current_song_index += 1
        if self.current_song_index >= len(self.list_of_songs):
            self.current_song_index = 0
        self.play_music()

    def skip_back(self):
        self.current_song_index -= 1
        if self.current_song_index < 0:
            self.current_song_index = len(self.list_of_songs) - 1
        self.play_music()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(value)

    def seek_music(self, value):
        if pygame.mixer.music.get_busy() or self.paused:
            pygame.mixer.music.set_pos(float(value))
            self.seek_offset = float(value)
            self.playback_start_time = time.time() # Reseta o tempo de início após a busca
            self.time_label.configure(text=f"{self.format_time(float(value))} / {self.format_time(self.song_length)}")

    def start_seek(self, event):
        self.user_seeking = True

    def end_seek(self, event):
        self.user_seeking = False
        self.seek_music(self.song_slider.get())

    def on_song_select(self, event):
        selected_index = self.song_listbox.curselection()
        if selected_index:
            self.current_song_index = selected_index[0]
            self.play_music()

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = MusicPlayerApp(root)
    root.mainloop()