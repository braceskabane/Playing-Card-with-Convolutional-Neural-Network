# Akses file gameplay.py
import gameplay
# import pygame

# def play_initial_sound():
#    pygame.init()
#    pygame.mixer.init()
#    pygame.mixer.music.load("aku.mp3")
#    pygame.mixer.music.play()

if __name__ == "__main__":
    # Memanggil fungsi untuk memutar lagu saat program pertama kali dijalankan
    # play_initial_sound()
    # Program utama
    # Memjadikan kelas Gameplay() dari file gameplay.py sebagai objek 
    game = gameplay.Gameplay()
    # Memanggil fungsi start pada kelas Gameplay()
    game.start()