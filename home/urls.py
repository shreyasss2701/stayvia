from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('hotel-details/<slug>/', views.hotel_details, name="hotel_details"),
    path('about/', views.about, name="about"),
    path('paymenthandler/', views.paymenthandler, name="paymenthandler"),
    path('payment/', views.homepage, name="homepage"),



]