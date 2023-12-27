import os
import cv2
import numpy as np

from keras.models import load_model

import msvcrt

import utils

class Gameplay:
# Inisialisasi
    def __init__(self):
        # Menandakan apakah game telah dimulai atau belum
        self.game_started = False

        self.cap = cv2.VideoCapture(0)

        self.Past = np.array(0)

        self.photos_taken = 0

        # Deklarasi list kartu yang dimiliki pemain dan komputer
        self.player_cards = []
        self.computer_cards = []
        # Deklarasi list kartu open card selalu berisi 1
        self.open_cards = []
        # Inisialisasi list self.trash
        self.trash = [] 

        self.model = load_model('Fix.h5')

# Fungsi yang pertama kali dijalankan
    def start(self):
        print("###########################################")
        print("############## Playing Card ###############")
        print("########################################### \n")
        print("Menu")
        print("1. Press 'q' = Quit")
        print("2. Press 'w' = Save datasheet")
        print("3. Press 'e' = Take a card")
        print("4. Press 'p' = Check card")
        print("5. Press 'z' = Start the Game")

        # Inisialisasi kamera pada droid cam 
        self.cap = cv2.VideoCapture(2)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Tidak dapat membaca frame dari kamera.")
                break
            
            # Menangkap Kartu dari greenscreen
            self.readImage(frame)

            # Menekan menu yang diinginkan pada terminal
            err = self.readInput()

            # Exit lewat terminal
            if err == 'exit':
                break
            
            # Exit pada cv2.imshow agar imshow tidak abu-abu
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

        # Inisialisasi Indeks yang terus bertambah saat mengambil foto
        self.photos_taken = 0

# Fungsi yang mengelola bagian greenscreen, kontur kartu dan deteksi warna 
    def readImage(self, frame):
        # Proses citra untuk menghasilkan maska warna hijau
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green1 = np.array([35, 100, 100])
        upper_green1 = np.array([100, 255, 255])
        lower_green2 = np.array([40, 40, 40])
        upper_green2 = np.array([80, 255, 255])
        mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
        mask2 = cv2.inRange(hsv, lower_green2, upper_green2)

        combined_mask = cv2.bitwise_or(mask1, mask2)
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.erode(combined_mask, kernel, iterations=3)
        combined_mask = cv2.dilate(combined_mask, kernel, iterations=7)

        # Gunakan Canny Edge Detection pada maska
        edges = cv2.Canny(combined_mask, 50, 150)

        # Deteksi kontur pada citra hasil edge detection
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            # Threshold area sesuai kebutuhan
            if area > 1000:  
                # Menghitung kotak berbentuk persegi panjang
                rect = cv2.minAreaRect(contour)
                # Ambil koordinat keempat sudut kartu
                box = cv2.boxPoints(rect)
                box = np.asarray(box, dtype=int)

                # POTONG BAGIAN KARTUNYA SAJA
                # Mendapatkan lebar dan tinggi dari persegi panjang terkecil
                width = int(rect[1][0])
                height = int(rect[1][1])

                # Perbarui lebar dan tinggi menjadi dua kali lipat
                width *= 2
                height *= 2

                # Jika lebar > tinggi, lakukan transformasi perspektif
                if width > height:
                    width, height = height, width  # Tukar lebar dan tinggi

                src_pts = box.astype("float32")
                dst_pts = np.array([[0, height - 1], [0, 0], [width - 1, 0], [width - 1, height - 1]], dtype="float32")
                
                matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped = cv2.warpPerspective(frame, matrix, (width, height))

                # Lakukan adaptive thresholding
                gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray_warped, (11, 11), 0)
                biner = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

                # Resize
                self.Past = cv2.resize(biner, (200, 300))
                
                # Tampilkan gambar warped yang telah ditandai dengan kontur persegi panjang warna hitam dan merah
                cv2.imshow('Adaptive Thresholding', self.Past)    
                
                # Gambar kotak yang mengelilingi kontur kartu
                cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
                cv2.imshow('Deteksi Kartu', frame)


                # MEMBERIKAN KONTUR WARNA MERAH DAN HITAM
                # Mengubah ke skema warna HSV
                hsv_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

                # Definisikan rentang warna merah dan hitam di HSV
                lower_red = np.array([0, 120, 70])
                upper_red = np.array([10, 255, 255])

                lower_black = np.array([0, 0, 0])
                upper_black = np.array([179, 255, 30])

                # Buat maska untuk warna merah dan hitam
                mask_red = cv2.inRange(hsv_warped, lower_red, upper_red)
                mask_black = cv2.inRange(hsv_warped, lower_black, upper_black)

                # Gabungkan maska warna merah dan hitam
                mask_color = cv2.bitwise_or(mask_red, mask_black)
                kernel = np.ones((3, 3), np.uint8)
                mask_color = cv2.erode(mask_color, kernel, iterations=3)
                mask_color = cv2.dilate(mask_color, kernel, iterations=7)

                # Temukan kontur pada warna yang terdeteksi
                contours_color, _ = cv2.findContours(mask_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Loop melalui setiap kontur warna yang terdeteksi
                for contour in contours_color:
                    area = cv2.contourArea(contour)
                    if area > 100:  # Sesuaikan dengan threshold area yang sesuai
                        # Tentukan warna berdasarkan maska yang terdeteksi
                        if np.any(cv2.bitwise_and(mask_red, mask_black)):
                            color_detected = "Campuran Merah dan Hitam"
                        # np.any digunakan untuk    
                        elif np.any(mask_red):
                            color_detected = "Merah"
                        elif np.any(mask_black):
                            color_detected = "Hitam"
                        
                        # Gambar kotak mengelilingi kontur warna hitam dan merah
                        rect = cv2.minAreaRect(contour)
                        box = cv2.boxPoints(rect)
                        box = np.int0(box)
                        cv2.drawContours(warped, [box], 0, (0, 255, 0), 2)
                        
                        # Tambahkan teks pada kontur
                        cv2.putText(warped, f"Warna adalah: {color_detected}", (box[0][0], box[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # Tampilkan gambar warped yang telah ditandai dengan kontur persegi panjang warna hitam dan merah
                cv2.imshow('Deteksi Warna dengan Teks', warped) 
        
# Fungsi yang mengatur bagian tombol        
    def readInput(self):
        if msvcrt.kbhit():
            inp = msvcrt.getch()
    
            if inp == b'q':
                return 'exit'
            elif inp == b'e':
                card = self.takeCard()

                if card:
                    # Mencocokkan label benar, kartu dapat disimpan ke dalam pemain atau komputer
                    save_card = input("Press 'j' to add to player or 'k' to add to computer : ")
                    if save_card == 'j':  # Saat tombol 'j' ditekan (untuk pemain)
                        self.player_cards.append(card)
                        print("Card added to player cards.")
                    elif save_card == 'k':  # Saat tombol 'k' ditekan (untuk komputer)
                        self.computer_cards.append(card)
                        print("Card added to computer cards.")
                
            elif inp == b'w':
                self.saveData()
            elif inp == b'p':
                print('#######################################')
                utils.display_cards(self.player_cards, "Player")
                print('#######################################')
                utils.display_cards(self.computer_cards, "Computer")
                print('#######################################')
                utils.display_cards(self.open_cards, "Open")
                print('#######################################')
            elif inp == b'z':
                return self.play()

# Fungsi untuk mengambil gambar yang telah diberikan label ke list pemain
    def takeCard(self):
        cv2.imwrite(f'tmp.jpg', self.Past)
        img = np.array(cv2.imread('tmp.jpg'))
        img = img/255
        img = np.array(cv2.resize(img, (128, 128)))
        img = img.reshape(1,128,128,3)

        # Prediksi 
        label_prediction = self.model.predict(img)

        # Mendapatkan indeks label dengan nilai maksimum prediksi
        predicted_label_index = np.argmax(label_prediction)
        # Menampilkan label yang sesuai dengan indeks prediksi
        predicted_label = utils.labels[predicted_label_index]

        print(predicted_label)

        # Jika predicted_label sudah benar, lanjutkan dengan menyimpan kartu
        label_correct = input("Is the predicted label correct? (y/n): ")
        if label_correct.lower() == 'y':
            card = {'image': self.Past, 'label': predicted_label}
            
            self.Past = None
            predicted_label = None
            return card
        else:
            print("Label not confirmed.")
            return None

# Fungsi untuk Membuat Datasheet
    def saveData(self):
        # Cek apakah sudah diambil 10 foto, jika iya, pindah ke label berikutnya
        if self.photos_taken >= 20:
            self.photos_taken = 0  # Reset jumlah foto yang diambil
            label_state += 1   # Pindah ke label berikutnya
            print(f'Switched to label {utils.labels[label_state]}')
        
        # Cek apakah file ada
        if not os.path.exists(f'{utils.labels[label_state]}/'):
            os.mkdir(f'{utils.labels[label_state]}/')
        
        # Mengambil foto
        cv2.imwrite(f'{utils.labels[label_state]}/{utils.labels[label_state]}_{self.photos_taken}.jpg', self.Past)
        self.photos_taken += 1  # Menambah jumlah foto yang telah diambil
        
        print(f'Photo {self.photos_taken} taken for label {utils.labels[label_state]}')

# Game Dimulai
    def play(self):
        print('#######################################')
        print('#######################################')
        print("############ GAME STARTED #############")
        print('#######################################')
        
        self.game_started = True

        # 0 = com turn, 1 = player turn
        state = 0

        while True:
            ret, frame = self.cap.read()
            self.readImage(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if len(self.open_cards) == 0:
                print('#######################################')
                print('#######################################')
                utils.display_cards(self.computer_cards, "Computer")
                print('#######################################')
                utils.display_cards(self.open_cards, "Open")
                print('#######################################')
                print('#######################################')
                print('Tekan tombol u untuk membuka kartu....')
                
                # Menunggu tombol 'u' ditekan membuka kartu baru
                while True:
                    ret, frame = self.cap.read()
                    self.readImage(frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    if msvcrt.kbhit() and msvcrt.getch() == b'u':                        
                        card = self.takeCard()

                        if card:
                            self.open_cards.append(card)
                            print("Card added to open card.")  
                            break
                        
            if state == 0:
                print("Computer Take it First!")
                
                label_to_remove = self.open_cards[0]['label'].split('_')[-1]  # Memastikan card adalah string sebelum melakukan split()

                precedence = {}
                # Pilih kamus precedence berdasarkan jenis bentuk
                if label_to_remove == 'Club':
                    precedence = utils.precedence_Club
                elif label_to_remove == 'Diamond':
                    precedence = utils.precedence_Diamond
                elif label_to_remove == 'Heart':
                    precedence = utils.precedence_Heart
                elif label_to_remove == 'Spades':
                    precedence = utils.precedence_Spades


                matching_cards = []
                for c in self.computer_cards:
                    if c['label'].endswith(label_to_remove):
                        matching_cards.append(c)
                
                if len(matching_cards) == 0:
                    # Komputer tidak memiliki kartu yang sesuai, maka ambil kartu sampai mendapatkan yang sesuai
                    print(f"Computer doesn't have a matching card for {label_to_remove}. Press 't' to take a card.")
                    # Menunggu tombol 't' ditekan sebelum mengambil kartu
                    while True:
                        if self.checkEnd():
                            break

                        ret, frame = self.cap.read()
                        self.readImage(frame)

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        
                        if msvcrt.kbhit() and msvcrt.getch() == b't':                        
                            c = self.takeCard()
                            if c:
                                # Jika komputer berhasil mengambil kartu yang sesuai, keluar dari loop
                                if c['label'].split('_')[1] == label_to_remove:
                                    print("Computer got a matching card!")
                                    # Hapus kartu dengan label yang sama dari self.computer_cards dengan precedence terbesar pada jenis bentuk tertentu
                                    # Pindahkan kartu-kartu yang ingin dihapus ke dalam list self.trash
                                    self.open_cards.append(c)
                                    # Komputer memiliki kartu yang sesuai
                                    print(f"Computer has a matching card for {label_to_remove}.")
                                    break
                                else:
                                    self.computer_cards.append(c)
                                    print(f"Computer doesn't have a matching card for {label_to_remove}. Press 't' to take a card.")

                else:
                    # Hapus kartu dengan label yang sama dari self.computer_cards dengan precedence terbesar pada jenis bentuk tertentu
                    max_precedence = -1
                    max = 0
                    for i in range(len(self.computer_cards)):
                        card = self.computer_cards[i]
                        if card['label'].split('_')[1] == label_to_remove and precedence[card['label']] > max:
                            max_precedence = i
                            max = precedence[card['label']]

                    if max_precedence != -1:
                        # Pindahkan kartu yang ingin dihapus ke dalam list self.trash
                        removed_card = self.computer_cards.pop(max_precedence)
                        self.open_cards.append(removed_card)
                        # Hapus kartu-kartu tersebut dari self.computer_cards
                        # Komputer memiliki kartu yang sesuai
                        print(f"Computer has a matching card for {label_to_remove}.")

                state = 1
            
            elif state == 1:
                
                # Player Turn
                while True:
                    if self.checkEnd():
                        break

                    # Pilih Menu yang ingin diambil
                    print("##############################################")
                    print("################# PLAYER TURN ################")
                    print("##############################################")
                    utils.display_cards(self.player_cards, "Player")
                    utils.display_cards(self.open_cards, "Open")
                    print("##############################################")
                    utils.display_cards(self.computer_cards, "Computer")

                    print("Menu:")
                    print("1. Remove a card")
                    print("2. Take a card")
                    player_choice = input("Enter your choice (1 or 2): ")
                    # Jika pemain memilih untuk menghapus kartu
                    if player_choice == '1':
                        # Setelah input dari pemain untuk memilih kartu yang ingin dihapus
                        selected_card_index = int(input("Enter the index of the card you want to choose: ")) - 1

                        # Pilih kartu yang ingin dihapus berdasarkan indeks yang dimasukkan pemain
                        selected_card = self.player_cards[selected_card_index]

                        # Periksa jenis bentuk kartu yang dipilih pemain
                        selected_card_shape = selected_card['label'].split('_')[-1]

                        # Mencari kartu yang sesuai dengan jenis bentuk pada self.open_cards
                        if self.open_cards[0]['label'].endswith(selected_card_shape):
                            ##########################
                            print(selected_card_shape)
                            ##########################
                            # Memindahkan kartu dari self.player_cards ke self.trash
                            self.open_cards.append(self.player_cards.pop(selected_card_index))
                            print(f"Card {selected_card_index + 1} moved from player's cards to open card.")
                            state = 0
                            break
                        else:
                            print("Selected card doesn't match any shape in open cards. Please choose another card.")

                    if player_choice == '2':
                        print("Press 't' to take a card.")
                        while True:
                            ret, frame = self.cap.read()
                            self.readImage(frame)

                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                            
                            if msvcrt.kbhit() and msvcrt.getch() == b't':                        
                                card = self.takeCard()

                                if card:
                                    self.player_cards.append(card)
                                    print("Card added to player cards.")
                                    break



            ## If open_card length >= 3, then open_card = 0
            if len(self.open_cards) == 3:
                for c in self.open_cards:
                    self.trash.append(c)

                self.open_cards.clear()
                print("open cards moved to trash")

                state = 0

            ## KEADAAN MENANG DAN KALAH
            if self.checkEnd():
                print("##############################################")
                print("################## Game Over! ################")
                print("##############################################")
                utils.display_cards(self.player_cards, "Player :")

                utils.display_cards(self.computer_cards, "Computer :")
                # Hitung total precedence dari setiap list kartu
                total_player_precedence = utils.calculate_total_precedence(self.player_cards)
                total_computer_precedence = utils.calculate_total_precedence(self.computer_cards)
                total_trash_precedence = utils.calculate_total_precedence(self.trash)
                # Tentukan pemenang berdasarkan total precedence terkecil di antara self.player_cards dan self.computer_cards
                if total_player_precedence <= total_computer_precedence and total_player_precedence <= total_trash_precedence:
                    print("####################################")
                    print("##### Congratulations! You win! ####")
                    print("####################################")
                elif total_computer_precedence <= total_player_precedence and total_computer_precedence <= total_trash_precedence:
                    print("##############################")
                    print("####### Computers Wins #######")
                    print("##############################")
                else:
                    print("It's a tie!")
                break

            if len(self.player_cards) == 0 and len(self.computer_cards) == 0:
                print("There are no winners !")
                break
            elif len(self.player_cards) == 0:
                print("##############################")
                print("######### Player Wins ########")
                print("##############################")
                break
            elif len(self.computer_cards) == 0:
                print("##############################")
                print("######## Computer Wins #######")
                print("##############################")
                break
        
        print("##############################")
        print("###### congratulation !! #####")
        print("##############################")

# Kondisi 52 kartu telah terpakai
    def checkEnd(self):
        if len(self.trash) + len(self.player_cards) + len(self.computer_cards) == 52:
            return True
        
        return False