from mask_json_convert_python import Ui_converter
from PyQt5.QtWidgets import QMainWindow, QFileDialog

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import codecs, json
import ast
from glob import glob


class Converter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_converter()
        self.ui.setupUi(self)

        self.Mask_to_JSON = 0
        self.JSON_to_Mask = 1 

        self.ui.actionMask_to_JSON.triggered.connect(self.go_Mask_to_JSON) # Mask_to_JSON simge tuşuna basıldı bilgisi ve yapılacak fonk. 
        self.ui.actionJSON_to_Mask.triggered.connect(self.go_JSON_to_Mask) # JSON_to_Mask inceleme simge tuşuna basıldı bilgisi ve yapılacak fonk.
        
        self.ui.pushButton.clicked.connect(self.go_JSON_to_Mask)
        self.ui.Buton_mask.clicked.connect(self.clickbuton_dataMaskPath)
        self.ui.Buton_json.clicked.connect(self.clickbuton_dataJSONPath)
        self.ui.Start.clicked.connect(self.convert_Mask_to_JSON)

# ====== Kullanıcı Mask Path kısmında bulunan "ekle" butonuna bastığında sayfa yolunu seçecek ================
    def clickbuton_dataMaskPath(self):
        options = QFileDialog.Options()
        self.fileName = QFileDialog.getExistingDirectory(self, "QFileDialog.getOpenFileName()", "" ,options=options)
        if self.fileName:
            self.ui.lineEdit_mask.setText(self.fileName)

# ====== Kullanıcı JSON Path kısmında bulunan "ekle" butonuna bastığında sayfa yolunu seçecek ================
    def clickbuton_dataJSONPath(self):
        options = QFileDialog.Options()
        self.fileName = QFileDialog.getExistingDirectory(self, "QFileDialog.getOpenFileName()", "" ,options=options)
        if self.fileName:
            self.ui.lineEdit_json.setText(self.fileName)

# ====== Mask to JSON sayfasına yönlendirme =======================
    def go_Mask_to_JSON(self):
        self.ui.stackedWidget.setCurrentIndex(self.Mask_to_JSON)

# ====== JSON to Mask sayfasına yönlendirme =======================
    def go_JSON_to_Mask(self):
        self.ui.stackedWidget.setCurrentIndex(self.JSON_to_Mask)

# =========== Json içerisine değer eklemek için kullanılır. =========
    def add_value( dict_obj, key, value):
        if key not in dict_obj:
            dict_obj.update({key: value})
    
# ============== Başlat butonuna basıldığında convert işleminin yapılacığı yer. ==============
    def convert_Mask_to_JSON(self):

        def add_value(dict_obj, key, value):
            if key not in dict_obj:
                dict_obj.update({key: value})

        img_paths = glob(f"{self.ui.lineEdit_mask.displayText()}/*")

        
        labels = {}


        for img_path in img_paths:
        
            # -------------- Kontur Kısmı --------------------
            img = cv2.imread(img_path)

            kopya = img.copy()
            kopya = cv2.cvtColor(kopya, cv2.COLOR_RGB2GRAY)

            blur = cv2.cv2.GaussianBlur(kopya,(5,5),0)
            thresh = cv2.threshold(blur,10,255,cv2.THRESH_BINARY)[1]
            kontur_1 = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

            if len(kontur_1[0]) == 1:

                kontur = kontur_1[0:-1][0][0]

                x_list = [[]]
                y_list = [[]]
                for num, i in enumerate(kontur):
                    x_list[0].append(kontur[num][0][0])
                    y_list[0].append(kontur[num][0][1])

            elif len(kontur_1[0]) > 1:

                kontur = kontur_1[0:-1][0]
                x_list = []
                y_list = []

                for i in range(len(kontur)):
                    kontur_2 = kontur[i]
                    xara_list = []
                    yara_list = []

                    for num, i in enumerate(kontur_2):
                        xara_list.append(kontur_2[num][0][0])
                        yara_list.append(kontur_2[num][0][1])

                    x_list.append(xara_list)
                    y_list.append(yara_list)
            
            # ------------- Json İçeriği Oluşturma Kısmı ------------------------
            name = img_path.split("\\")[-1]
            add_value(labels, name, {"filename": f"{name}", "regions": {}})

            label_id = 0
            for i in range(len(x_list)):
                a = labels[f"{name}"]['regions']
                add_value(a, label_id, {"shape_attributes": {"all_points_x": f"{x_list[i]}", "all_points_y": f"{y_list[i]}", "name": "polygon"}})
                label_id += 1
            
            # ---------------- Json İçini Düzenleme ve Kaydetme Kısmı -----------------
        str_labels = str(labels)
        str_labels = str_labels.replace("'[", "[")
        str_labels = str_labels.replace("]'", "]")

        labels = ast.literal_eval(str_labels)

        json.dump(labels, codecs.open(f'{self.ui.lineEdit_json.displayText()}/data.json', 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent= 4) 