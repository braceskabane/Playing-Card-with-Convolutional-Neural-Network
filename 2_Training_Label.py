import os
from keras.models import load_model
import cv2
import numpy as np 
from keras.layers import Input, Dense
from keras.layers import Conv2D, MaxPooling2D, Flatten
from keras.models import Model
import matplotlib.pyplot as plt
from datetime import datetime
from numpy import expand_dims
from keras.utils import load_img
from keras.utils import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot

def ModelDeepLearningCNN(JumlahKelas):
    # Ukuran citra 128x128 piksel dan tiga saluran warna (RGB).
    input_img = Input(shape=(128, 128, 3)) 
    # Menambahkan layer konvolusi 32 filter dengan kernel 3*3
    # ReLU (Rectified Linear Activation)
    # ReLU mengonversi nilai input menjadi nol 
    # jika nilainya kurang dari nol, 
    # dan mempertahankan nilai inputnya
    #  jika nilainya lebih besar dari nol.
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)  
    x = MaxPooling2D((2, 2), padding='same')(x)   
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)   
    x = MaxPooling2D((2, 2), padding='same')(x)   
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)   
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = Flatten()(x)
    x = Dense(100,activation='relu')(x)
    x=Dense(JumlahKelas,activation='softmax')(x)
    ModelCNN = Model(input_img, x)  
    ModelCNN.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #ModelCNN.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    return ModelCNN



DirektoriDataSet="E:\\University\\Material\\Semester 5\\Pengolahan Citra Video\\Tugas Akhir"
#   Data Set disimpan dalam direktori yang sama dengan nama kelas    

#b. Label Data Set 
LabelKelas = (
        "2_Club", "3_Club", "4_Club", "5_Club", "6_Club", "7_Club", "8_Club", "9_Club", "10_Club", "ace_Club", 
        "J_Club", "Q_Club", "K_Club", "2_Diamond", "3_Diamond", "4_Diamond", "5_Diamond", "6_Diamond", "7_Diamond",
        "8_Diamond", "9_Diamond", "10_Diamond", "ace_Diamond", "J_Diamond", "Q_Diamond", "K_Diamond", "2_Heart", 
        "3_Heart", "4_Heart", "5_Heart", "6_Heart", "7_Heart", "8_Heart", "9_Heart", "10_Heart", "ace_Heart", 
        "J_Heart", "Q_Heart", "K_Heart", "2_Spades", "3_Spades", "4_Spades", "5_Spades", "6_Spades", "7_Spades", 
        "8_Spades", "9_Spades", "10_Spades", "ace_Spades", "J_Spades", "Q_Spades", "K_Spades"
)

x = []
y = []

# One-hot Encoding ada 52 kelas vektor  [1. 0. 0. (hingga 52 angka)]
t = np.eye(len( LabelKelas))

for i in range(len(LabelKelas)):
    label = LabelKelas[i]
    
    if not os.path.exists(f'{label}/'):
        continue

    j = 0
    while os.path.exists(f'{label}/{label}_{j}.jpg'):
        filename = f'{label}/{label}_{j}.jpg'
        img = np.double(cv2.imread(filename))
        img = cv2.resize(img,(128,128))
        img = np.asarray(img)/255
        img = img.astype('float32')
        x.append(img)
        
        y.append(t[i])

        j+=1

x = np.array(x).astype('float32')
y = np.array(y).astype('float32')

# # CEK APAKAH DATASET DAN LABEL BENAR
# print("Jumlah dataset (gambar):", len(x))
# print("Jumlah dataset (label):", len(y))

# for i in range(len(LabelKelas)):
#     label = LabelKelas[i]
    
#     if not os.path.exists(f'{label}/'):
#         continue

#     j = 0
#     while os.path.exists(f'{label}/{label}_{j}.jpg'):
#         filename = f'{label}/{label}_{j}.jpg'
#         print("File Gambar:", filename)
#         print("Label:", label)

#         j += 1

#c. Inisialisasi parameter Training
JumlahEpoh = 10
FileBobot = "Fix.h5"
#d. training
modelCNN =ModelDeepLearningCNN(len(LabelKelas))
#Trainng
history=modelCNN.fit(x, y, epochs=JumlahEpoh,shuffle=True)
#Menyimpan hasil learning
modelCNN.save(FileBobot)

#Mengembalikan output 
modelCNN.summary()
model = Model.load_weights

#c. Menampilkan Grafik Loss dan accuracy
plt.plot(history.history['loss'])
plt.plot(history.history['accuracy'])

plt.title('model loss')
plt.ylabel('loss/accuracy')
plt.xlabel('epoch')
plt.legend(['loss', 'acc'], loc='upper left')
plt.show()