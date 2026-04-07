#accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/' , views.login_page, name='login_page'),
    path('register/' , views.register, name='register'),
    path('send_otp/<email>/' , views.send_otp, name='send_otp'),
    path('verify-otp/<email>/' , views.verify_otp, name='verify_otp'),
    path('verify-account/<token>/', views.verify_email_token, name="verify_email_token"),
    path('login-vendor/' , views.login_vendor, name='login_vendor'),
    path('register-vendor/' , views.register_vendor, name='register_vendor'),
    path('send_otp_vendor/<email>/' , views.send_otp_vendor, name='send_otp_vendor'),
    path('verify-otp-vendor/<email>/' , views.verify_otp_vendor, name='verify_otp_vendor'),
    path('verify-account-vendor/<token>/', views.verify_email_token_vendor, name="verify_email_token_vendor"),
    path('dashboard/' , views.dashboard, name='dashboard'),
    path('add-hotel/', views.add_hotel , name="add_hotel"),
    path('upload-images/<slug>',views.upload_images, name="upload_images"),
    path('delete_image/<id>/' , views.delete_image , name="delete_image"),
    path('edit-hotel/<slug>/', views.edit_hotel , name="edit_hotel"),
    path('logout/' , views.logout_view , name="logout_view"),
    path('vendor_booking/<slug>/',views.vendor_booking , name="vendor_booking"),
    path('vendor_all_booking/',views.vendor_all_booking, name='vendor_all_booking'),
    path('user_booking/', views.user_booking, name="user_booking"),
    path('checkout/<slug>/',views.checkout,name="checkout"),
    path('payment/',views.home,name="home"),
    path('order/',views.create_order,name="create_order"),
    path('payment_success/',views.payment_success, name="payment_success"),
    path('verify_signature/',views.verify_signature,name="verify_signature"),
]