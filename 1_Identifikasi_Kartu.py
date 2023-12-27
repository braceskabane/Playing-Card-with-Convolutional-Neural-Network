import os
import cv2
import numpy as np


from keras.models import load_model
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions
from keras.applications.vgg16 import VGG16

# Load Model
model = load_model('Fix.h5')


# Inisialisasi kamera
cap = cv2.VideoCapture(2)

labels = (
        "2_Club", "3_Club", "4_Club", "5_Club", "6_Club", "7_Club", "8_Club", "9_Club", "10_Club", "ace_Club", 
        "J_Club", "Q_Club", "K_Club", "2_Diamond", "3_Diamond", "4_Diamond", "5_Diamond", "6_Diamond", "7_Diamond",
        "8_Diamond", "9_Diamond", "10_Diamond", "ace_Diamond", "J_Diamond", "Q_Diamond", "K_Diamond", "2_Heart", 
        "3_Heart", "4_Heart", "5_Heart", "6_Heart", "7_Heart", "8_Heart", "9_Heart", "10_Heart", "ace_Heart", 
        "J_Heart", "Q_Heart", "K_Heart", "2_Spades", "3_Spades", "4_Spades", "5_Spades", "6_Spades", "7_Spades", 
        "8_Spades", "9_Spades", "10_Spades", "ace_Spades", "J_Spades", "Q_Spades", "K_Spades"
)

label_state = 0
i = 0

# Variabel untuk menghitung jumlah foto yang telah diambil
photos_taken = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak dapat membaca frame dari kamera.")
        break

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
        if area > 1000:  # Ubah threshold area sesuai kebutuhan
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
            Past = cv2.resize(biner, (200, 300))
            
            # Tampilkan gambar warped yang telah ditandai dengan kontur persegi panjang warna hitam dan merah
            cv2.imshow('Adaptive Thresholding', Past)    
            
            # Gambar kotak yang mengelilingi kontur kartu
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
            cv2.imshow('Deteksi Kartu', frame)

            # # MEMOTONG KEMBALI MENGAMBIL POJOK KIRI ATAS
            # # Potong bagian pojok kiri atas dari hasil potongan sebelumnya 
            # x_offset, y_offset = 0, 0  
            # width_cut, height_cut = 99, 99  # Atur ukuran potongan sesuai kebutuhan
            # cropped_corner = warped[y_offset:y_offset+height_cut, x_offset:x_offset+width_cut]

            # # Resize gambar hasil potongan
            # resized_cropped = cv2.resize(cropped_corner, (300, 300))  # Ubah ukuran sesuai kebutuhan

            # # Proses gambar menjadi hitam-putih
            # gray = cv2.cvtColor(resized_cropped, cv2.COLOR_BGR2GRAY)
            # # Lakukan adaptive thresholdingi

            # # Lakukan erosi dan dilasi untuk meningkatkan ketajaman gambar
            # kernel = np.ones((3, 3), np.uint8)
            # binary = cv2.erode(binary, kernel, iterations=1)
            # binary = cv2.dilate(binary, kernel, iterations=1)

            # # Balikkan warna hitam dan putih
            # binary = cv2.bitwise_not(binary)

            # # Tampilkan gambar hasil proses
            # cv2.imshow('Potongan Kiri Atas dengan Kontur', binary)  

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

    # EXIT
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
    
    # SAVE DATASHEET
    if cv2.waitKey(1) & 0xFF == ord('w'):
        # Cek apakah sudah diambil 10 foto, jika iya, pindah ke label berikutnya
        if photos_taken >= 20:
            photos_taken = 0  # Reset jumlah foto yang diambil
            label_state += 1   # Pindah ke label berikutnya
            print(f'Switched to label {labels[label_state]}')
        
        # Cek apakah file ada
        if not os.path.exists(f'{labels[label_state]}/'):
            os.mkdir(f'{labels[label_state]}/')
        
        # Mengambil foto
        cv2.imwrite(f'{labels[label_state]}/{labels[label_state]}_{photos_taken}.jpg', Past)
        photos_taken += 1  # Menambah jumlah foto yang telah diambil
        
        print(f'Photo {photos_taken} taken for label {labels[label_state]}')
        
    # TESTING HASIL TRAINING .h5
    elif cv2.waitKey(1) & 0xFF == ord('e'):
        cv2.imwrite(f'tmp.jpg', Past)
        img = np.array(cv2.imread('tmp.jpg'))
        img = img/255
        img = np.array(cv2.resize(img, (128, 128)))
        img = img.reshape(1,128,128,3)

        # Prediksi 
        label_prediction = model.predict(img)

        # Mendapatkan indeks label dengan nilai maksimum prediksi
        predicted_label_index = np.argmax(label_prediction)
        # Menampilkan label yang sesuai dengan indeks prediksi
        predicted_label = labels[predicted_label_index]
        
        print(predicted_label)

cap.release()
cv2.destroyAllWindows()
