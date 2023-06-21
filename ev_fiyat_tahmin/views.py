from django.shortcuts import render
from django.urls import reverse_lazy
from django import forms
import pandas as pd
import os
import csv
import locale
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from formtools.wizard.views import SessionWizardView

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

with open(os.path.join(DATA_DIR, 'coord.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    ILCE_CHOICES = [(row['ilce'].strip(), row['ilce'].strip()) for row in reader] 

with open(os.path.join(DATA_DIR, 'ilan.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    mahalle_set = set()
    for row in reader:
        mahalle_set.add(row['mahalle'].strip())
    MAHALLE_CHOICES = sorted([(mahalle, mahalle) for mahalle in mahalle_set])    

with open(os.path.join(DATA_DIR, 'rooms.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    ROOMS_CHOICES = [(row['value'].strip(), row['oda_sayisi'].strip()) for row in reader]

with open(os.path.join(DATA_DIR, 'fire.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    FIRE_CHOICES = [(row['value'].strip(), row['name'].strip()) for row in reader]

with open(os.path.join(DATA_DIR, 'furniture.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    FURNITURE_CHOICES = [(row['value'].strip(), row['name'].strip()) for row in reader]


class IlceMahalleForm(forms.Form):
    ilce = forms.ChoiceField(label='İlçe', choices=ILCE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    mahalle = forms.ChoiceField(label='Mahalle(Seçtiğiniz İlçede bulunan Mahalleyi Seçiniz)', choices=MAHALLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class BinaBilgileriForm(forms.Form):
    bina_yasi = forms.IntegerField(label='Bina Yaşı', widget=forms.TextInput(attrs={'class': 'form-control'}))
    kat_sayisi = forms.IntegerField(label='Kat Sayısı',widget=forms.TextInput(attrs={'class': 'form-control'}))
    bulundugu_kat = forms.IntegerField(label='Bulunduğu Kat',widget=forms.TextInput(attrs={'class': 'form-control'}))
    oda_sayisi = forms.ChoiceField(label='Oda Sayısı', choices=ROOMS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    toplam_oda_sayisi = forms.IntegerField(label='Toplam Oda Sayısı',widget=forms.TextInput(attrs={'class': 'form-control'}))


class AlanBilgileriForm(forms.Form):
    net_alan = forms.IntegerField(label='Net Alan',widget=forms.TextInput(attrs={'class': 'form-control'}))
    brut_alan = forms.IntegerField(label='Brüt Alan',widget=forms.TextInput(attrs={'class': 'form-control'}))


class DigerBilgilerForm(forms.Form):
    isitma = forms.ChoiceField(label='Isıtma', choices=FIRE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    esya = forms.ChoiceField(label='Eşya', choices=FURNITURE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class EvFiyatTahminiWizard(SessionWizardView):
    template_name = 'ev_fiyat_tahmini.html'
    form_list = [IlceMahalleForm, BinaBilgileriForm, AlanBilgileriForm, DigerBilgilerForm]
    file_storage = None
    data = {}

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        step = int(self.steps.current)
        total_steps = len(self.form_list)

         # Adım başlıklarını al
        step_titles = [
            'Eviniz hangi İlçe ve Mahallede ?',
            'Evin Bulunduğu Bina Bilgileri',
            'Evin m2 Cinsinden Bilgileri',
            'Diğer Bilgiler'
        ]

        # İlerleme durumu ve toplam adımları şablona aktar
        context['progress'] = {
            'step': step + 1,
            'total_steps': total_steps,
            'percentage': int((step / total_steps) * 100),
            'step_title': step_titles[step]
        }


        # Aktif formu şablona aktar
        context['active_form'] = form

        return context


    def done(self, form_list, **kwargs):
        for form in form_list:
            self.data.update(form.cleaned_data)

        # Veri setini yükleme
        veri_seti = pd.read_csv(os.path.join(DATA_DIR, 'ilan.csv'))
        veri_seti['oda_sayisi'] = veri_seti['oda_sayisi'].apply(lambda x: sum(map(int, x.split('+'))))

        # İlçe ve mahalle için Label Encoding işlemi
        label_encoder_ilce = LabelEncoder()
        label_encoder_mahalle = LabelEncoder()

        # Veri setindeki ilçe ve mahalle sütunlarını dönüştürme
        veri_seti['ilce'] = label_encoder_ilce.fit_transform(veri_seti['ilce'])
        veri_seti['mahalle'] = label_encoder_mahalle.fit_transform(veri_seti['mahalle'])

        # Kullanıcının girdiği bilgileri encode etme
        kullanici_ilce_encoded = label_encoder_ilce.transform([self.data['ilce']])[0]
        kullanici_mahalle_encoded = label_encoder_mahalle.transform([self.data['mahalle']])[0]


        # Veri setinde sadece kullanıcının girdiği ilçe ve mahalle değerlerine ait satırları seçme
        kullanici_veri = veri_seti[(veri_seti['ilce'] == kullanici_ilce_encoded) & (veri_seti['mahalle'] == kullanici_mahalle_encoded)]
       

        # Model oluşturma ve eğitme
        ozellikler = kullanici_veri[['ilce','mahalle','bina_yasi', 'kat_sayisi', 'bulundugu_kat', 'oda_sayisi', 'toplam_oda_sayisi', 'net_alan', 'brut_alan', 'isitma', 'esya']]
        hedef = kullanici_veri['fiyat']

        model = DecisionTreeRegressor()
        model.fit(ozellikler, hedef)

        # Kullanıcının girdiği bilgileri modele vererek tahmin yapma
        kullanici_veri = pd.DataFrame({
            'ilce': [kullanici_ilce_encoded],
            'mahalle': [kullanici_mahalle_encoded],
            'bina_yasi': [self.data['bina_yasi']],
            'kat_sayisi': [self.data['kat_sayisi']],
            'bulundugu_kat': [self.data['bulundugu_kat']],
            'oda_sayisi': [int(self.data['oda_sayisi'])],
            'toplam_oda_sayisi': [self.data['toplam_oda_sayisi']],
            'net_alan': [self.data['net_alan']],
            'brut_alan': [self.data['brut_alan']],
            'isitma': [self.data['isitma']],
            'esya': [self.data['esya']]
        })

        tahmin_degeri = model.predict(kullanici_veri)

        

        kullanici_veri['oda_sayisi'] = int(self.data['oda_sayisi'])
        kullanici_veri['isitma'] = int(self.data['isitma'])
        kullanici_veri['esya'] = int(self.data['esya'])


        tahmin_degeri = model.predict(kullanici_veri)
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        tahmin_degeri_tl = locale.currency(tahmin_degeri[0], grouping=True, symbol=False)
        tahmin_degeri_tl = "₺" + tahmin_degeri_tl

        print("canmuyhammedkelek", tahmin_degeri)
        # Tahmin sonucunu template'e aktar
        context = {
            'tahmin_degeri': tahmin_degeri_tl,
        }

        return render(self.request, 'tahmin_sonucu.html', context)
