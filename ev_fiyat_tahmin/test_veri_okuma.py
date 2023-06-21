import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
import os
# from fiyatTahmin.settings import DATA_DIR

# print("askjdasdadas", DATA_DIR)
# Veri setini yükleme
veri_seti = pd.read_csv('../data/ilan.csv')
veri_seti['oda_sayisi'] = veri_seti['oda_sayisi'].apply(lambda x: sum(map(int, x.split('+'))))
# İl, ilçe ve mahalle için Label Encoding işlemi
label_encoder_il = LabelEncoder()
label_encoder_ilce = LabelEncoder()
label_encoder_mahalle = LabelEncoder()

# Veri setindeki il, ilçe ve mahalle sütunlarını dönüştürme
veri_seti['il'] = label_encoder_il.fit_transform(veri_seti['il'])
veri_seti['ilce'] = label_encoder_ilce.fit_transform(veri_seti['ilce'])
veri_seti['mahalle'] = label_encoder_mahalle.fit_transform(veri_seti['mahalle'])

# Kullanıcının girdiği bilgileri encode etme
kullanici_il = input('İl: ')
kullanici_ilce = input('İlçe: ')
kullanici_mahalle = input('Mahalle: ')
kullanici_bina_yas = input('Bina Yaşı: ')
kullanici_kat_sayisi = input('Kat Sayısı: ')
kullanici_bulundugu_kat = input('Bulunduğu Kat: ')
kullanici_oda_sayisi = input('Oda Sayısı: ')
kullanici_toplam_oda_sayisi = input('Toplam Oda Sayısı: ')
kullanici_net_alan = input('Net Alan: ')
kullanici_brut_alan = input('Brüt Alan: ')
kullanici_isitma = input('Isıtma: ')
kullanici_esya = input('Esya ')



kullanici_il_encoded = label_encoder_il.transform([kullanici_il])[0]
kullanici_ilce_encoded = label_encoder_ilce.transform([kullanici_ilce])[0]
kullanici_mahalle_encoded = label_encoder_mahalle.transform([kullanici_mahalle])[0]

# Veri setinde sadece kullanıcının girdiği il, ilçe ve mahalle değerlerine ait satırları seçme
kullanici_veri = veri_seti[(veri_seti['il'] == kullanici_il_encoded) & (veri_seti['ilce'] == kullanici_ilce_encoded) & (veri_seti['mahalle'] == kullanici_mahalle_encoded)]

# Model oluşturma ve eğitme
ozellikler = kullanici_veri[['net_alan', 'brut_alan', 'kredi_durumu', 'kat_sayisi', 'isitma', 'bulundugu_kat', 'bina_yasi', 'esya', 'kullanim_durumu', 'il', 'ilce', 'mahalle', 'oda_sayisi', 'toplam_oda_sayisi', 'lat', 'lng']]
hedef = kullanici_veri['fiyat']

model = DecisionTreeRegressor()
model.fit(ozellikler, hedef)

# Kullanıcının girdiği bilgileri modele vererek tahmin yapma
kullanici_veri = pd.DataFrame({'net_alan': [kullanici_net_alan], 'brut_alan': [kullanici_brut_alan], 'kredi_durumu': [0], 'kat_sayisi': [kullanici_kat_sayisi], 'isitma': [1], 'bulundugu_kat': [kullanici_bulundugu_kat], 'bina_yasi': [kullanici_bina_yas], 'esya': [kullanici_esya], 'kullanim_durumu': [0], 'il': [kullanici_il_encoded], 'ilce': [kullanici_ilce_encoded], 'mahalle': [kullanici_mahalle_encoded], 'oda_sayisi': [kullanici_oda_sayisi], 'toplam_oda_sayisi': [kullanici_toplam_oda_sayisi], 'lat': [40.8741659], 'lng': [29.1293251]})

# 'oda_sayisi' sütununu işleyerek oda sayısını ayrıştırma
kullanici_veri['oda_sayisi'] = kullanici_veri['oda_sayisi'].str.strip().str.extract('(\d+)', expand=False).astype(int)

tahmin_degeri = model.predict(kullanici_veri)
print("Kullanıcının evinin tahmini değeri:", tahmin_degeri)
