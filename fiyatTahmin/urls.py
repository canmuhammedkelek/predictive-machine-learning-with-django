from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ev_fiyat_tahmin/', include('ev_fiyat_tahmin.urls')),
    path('', RedirectView.as_view(url='ev_fiyat_tahmin/')),
]
