from mask_json_convert_python import Ui_converter
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QProgressBar
from PyQt5.QtGui import QIntValidator

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import codecs, json
import ast
from glob import glob
import os
from tqdm import tqdm
import shutil




class Converter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_converter()
        self.ui.setupUi(self)

        self.Mask_to_JSON = 0
        self.JSON_to_Mask = 1 

        self.ui.lineEdit_widht.setValidator(QIntValidator(0,10000,self))
        self.ui.lineEdit_height.setValidator(QIntValidator(0,10000,self))

        self.ui.actionMask_to_JSON.triggered.connect(self.go_Mask_to_JSON) # Mask_to_JSON simge tuşuna basıldı bilgisi ve yapılacak fonk. 
        self.ui.actionJSON_to_Mask.triggered.connect(self.go_JSON_to_Mask) # JSON_to_Mask inceleme simge tuşuna basıldı bilgisi ve yapılacak fonk.
        self.ui.pushButton_masktojson.clicked.connect(self.go_Mask_to_JSON)
        
        
        self.ui.pushButton.clicked.connect(self.go_JSON_to_Mask)
        self.ui.Buton_mask.clicked.connect(self.clickbuton_dataMaskPath)
        self.ui.Buton_json.clicked.connect(self.clickbuton_dataJSONPath)
        self.ui.Start.clicked.connect(self.convert_Mask_to_JSON)

        self.ui.pushButton_loadjson.clicked.connect(self.loadjson)
        self.ui.pushButton_maskpath.clicked.connect(self.save_dataMaskPath)
        self.ui.pushButton_baslat.clicked.connect(self.convert_json_to_mask)
        




#========= kullanıcı load json butonuna bastığında json dosya yolunu seçer===================================
    def loadjson(self):
        options = QFileDialog.Options()
        #self.fileName = QFileDialog.getExistingDirectory(self, "QFileDialog.getOpenFileName()", "" ,options=options)
        self.json_fileName = QFileDialog.getOpenFileName(self,"Open Json", "C:\\", "json Files (*.json)")[0]
        if self.json_fileName:
            self.ui.pushButton_loadjson.setText(self.json_fileName)
#========= Kullanıcı maskelerin kayıt edeceği yolu seçer =================================================
    def save_dataMaskPath(self):
            options = QFileDialog.Options()
            self.savemask_fileName = QFileDialog.getExistingDirectory(self, "choose save mask path", "" ,options=options)
            if self.savemask_fileName:
                self.ui.pushButton_maskpath.setText(self.savemask_fileName)



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
        count = 0
        self.ui.progressBar_2.setMaximum(len(img_paths))
        for img_path in img_paths:
            count +=1
            self.ui.progressBar_2.setValue(count)
        
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
        self.ui.statusbar.showMessage('İşlem Tamamlandı.',3000)
        self.ui.statusbar.setStyleSheet('color:rgb(0,0,255);font-weight:bold')
#============ convert json to mask başlatılcak =============================================================
    def convert_json_to_mask(self):
        source_folder = os.path.join(self.savemask_fileName, "sep_masks")
        try:
            os.mkdir(source_folder)
        except:
            pass

        print('source_folder',source_folder)
        json_path = self.json_fileName                   # Relative to root directory
        count = 0                                           # Count of total images saved
        file_bbs = {}                                       # Dictionary containing polygon coordinates for mask
        MASK_WIDTH=int(self.ui.lineEdit_widht.text())
        MASK_HEIGHT=int(self.ui.lineEdit_height.text())						

        # Read JSON file
        with open(json_path) as f:
            data = json.load(f)

        # Extract X and Y coordinates if available and update dictionary
        def add_to_dict(data, itr, key, count):
            try:
                x_points = data[itr]["regions"][f'{count}']["shape_attributes"]["all_points_x"]
                y_points = data[itr]["regions"][f'{count}']["shape_attributes"]["all_points_y"]
            except:
                print("No BB. Skipping", key)
                return
            
            all_points = []
            for i, x in enumerate(x_points):
                all_points.append([x, y_points[i]])
            
            file_bbs[key] = all_points
        
        for itr in data:
            file_name_json = data[itr]["filename"]
            sub_count = 0               # Contains count of masks for a single ground truth image
            
            if len(data[itr]["regions"]) > 1:
                for _ in range(len(data[itr]["regions"])):
                    key = file_name_json[:-4] + "*" + str(sub_count+1)
                    add_to_dict(data, itr, key, sub_count)
                    sub_count += 1
            else:
                add_to_dict(data, itr, file_name_json[:-4], 0)

                    
        print("\nDict size: ", len(file_bbs))
        try:
            for itr in data:
                
                to_save_folder = os.path.join(source_folder,data[itr]["filename"].split('.')[0])
                mask_folder = os.path.join(to_save_folder, "masks")
            
                
                # make folders and copy image to new location
                os.mkdir(to_save_folder)
            
                os.mkdir(mask_folder)
            
        except:
            pass        
        # For each entry in dictionary, generate mask and save in correponding 
        # folder
        #print(file_bbs)

        for itr in file_bbs:
            array = []
            num_masks = itr.split("*")
            to_save_folder = os.path.join(source_folder, num_masks[0])
            mask_folder = os.path.join(to_save_folder, "masks")
            img = cv2.imread(to_save_folder+'/images/'+num_masks[0])
            mask = np.zeros((MASK_WIDTH, MASK_HEIGHT))
            try:
                arr = np.array(file_bbs[itr],dtype=np.int32)
            
            except:
                print("Not found:", itr)
                continue
            count += 1
            cv2.fillPoly(mask, [arr], color=(255))

            if len(num_masks) > 1:
                
                cv2.imwrite(os.path.join(mask_folder, itr.replace("*", "_") + ".png") , mask)    
            else:
                cv2.imwrite(os.path.join(mask_folder, itr + ".png") , mask)
            #print(mask_folder)
                
        #buradaki işlem bitince hepsini birleştirecek
        self.and_or()

    def and_or(self):
        mask_folder = os.path.join(self.savemask_fileName, "masks")
        try:
            os.mkdir(mask_folder)
        except:
            pass

        MASK_WIDTH=int(self.ui.lineEdit_widht.text())
        MASK_HEIGHT=int(self.ui.lineEdit_height.text())						


        def img_read(i):
            images = []

            files = glob(str(i)+'/masks/*png')
            for j in range(len(files)):
                img = cv2.imread(files[j])
                images.append(img)

            return images


        
        black = np.zeros((MASK_WIDTH, MASK_HEIGHT), np.uint8)
        black_path = os.path.join(self.savemask_fileName+'/black.png')
        cv2.imwrite(black_path, black)

        def bitwise(images):
            mask = cv2.imread(self.savemask_fileName+'/black.png')
            for i in range(len(images)):
                mask = cv2.bitwise_or(mask,images[i])  

            return mask
                
        img_folder = os.path.join(self.savemask_fileName, "sep_masks")
        files_img = glob(img_folder+'/*')
        #print('files number',len(files_img))
        count = 0
        self.ui.progressBar.setMaximum(len(files_img))
        for i in tqdm(files_img):
            count +=1
            self.ui.progressBar.setValue(count)
            name = i
            img_name = name.split('\\')[-1]
            #print(name)
            
            images = img_read(name)
            res = bitwise(images)

            cv2.imwrite(os.path.join(mask_folder+'/'+str(img_name)+ ".png"), res)
        
        shutil.rmtree(img_folder)
        os.remove(black_path)
        self.ui.statusbar.showMessage('İşlem Tamamlandı.',3000)
        self.ui.statusbar.setStyleSheet('color:rgb(0,0,255);font-weight:bold')
            