from django import forms

class IlceMahalleForm(forms.Form):
    ilce = forms.CharField(label='İlçe', max_length=100)
    mahalle = forms.CharField(label='Mahalle', max_length=100)

class BinaBilgileriForm(forms.Form):
    bina_yasi = forms.IntegerField(label='Bina Yaşı')
    kat_sayisi = forms.IntegerField(label='Kat Sayısı')
    bulundugu_kat = forms.IntegerField(label='Bulunduğu Kat')
    oda_sayisi = forms.CharField(label='Oda Sayısı', max_length=100)
    toplam_oda_sayisi = forms.IntegerField(label='Toplam Oda Sayısı')

class AlanBilgileriForm(forms.Form):
    net_alan = forms.FloatField(label='Net Alan')
    brut_alan = forms.FloatField(label='Brüt Alan')

class DigerBilgilerForm(forms.Form):
    isitma = forms.IntegerField(label='Isıtma')
    esya = forms.IntegerField(label='Eşya Durumu')
    kullanim_durumu = forms.IntegerField(label='Kullanım Durumu')
    kredi_durumu = forms.IntegerField(label='Kredi Durumu')
