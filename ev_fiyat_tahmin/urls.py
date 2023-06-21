from django.urls import path
from . import views

urlpatterns = [
    path('', views.EvFiyatTahminiWizard.as_view(), name='ev_fiyat_tahmini'),
]
