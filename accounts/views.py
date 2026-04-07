from django.shortcuts import render,redirect,HttpResponse,HttpResponsePermanentRedirect,get_object_or_404,HttpResponseRedirect
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .utils import generateRandomToken,sendEmailToken,sendOTPtoEmail,generateSlug
from django.db.models import Q
import random
from stayvia.settings import RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET,RAZORPAY_CALLBACK_URL
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import razorpay
# Create your views here.
def register(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if first_name == "" or last_name=="" or email=="" or password=="" or phone_number=="":
            messages.warning(request, "All Fields are mandatory")
            return redirect('/account/register/')


        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register/')

        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        flag="user"
        sendEmailToken(flag,email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register/')


    return render(request, 'register.html')


def login_page(request):    
    if request.method == "POST":
        print("in login accounts.view")
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('login_page')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('login_page')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            login(request , hotel_user)
            return redirect('/')

        messages.warning(request, "Invalid credentials")
        return redirect('login_page')
    print("not in if")
    return render(request, 'login.html')

def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/account/login/')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid Token")
    


def send_otp(request, email):
    print("in send_otp: "+email )
    hotel_user = HotelUser.objects.filter(
            email = email)
    if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

    otp =  random.randint(1000 , 9999)
    hotel_user.update(otp =otp)

    sendOTPtoEmail(email , otp)

    return redirect(f'/account/verify-otp/{email}/')


def verify_otp(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/login/')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp/{email}/')

    return render(request , 'verify_otp.html')


def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelVendor.objects.filter(
            email = email)
        print(hotel_user)

        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login-vendor/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login-vendor/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login-vendor/')
    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if first_name == "" or last_name=="" or business_name=="" or email=="" or password=="" or phone_number=="":
            messages.warning(request, "All Fields are mandatory")
            return redirect('/account/register-vendor/')

        hotel_user = HotelVendor.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register-vendor/')

        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        flag="vendor"
        sendEmailToken(flag,email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register-vendor/')


    return render(request, 'vendor/register_vendor.html')

def verify_email_token_vendor(request, token):
    try:
        hotel_user = HotelVendor.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/account/login-vendor/')
    except HotelVendor.DoesNotExist:
        return HttpResponse("Invalid Token")

def send_otp_vendor(request, email):
    print("in send_otp_vendor: "+email )
    hotel_user = HotelVendor.objects.filter(
            email = email)
    if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login-vendor/')

    otp =  random.randint(1000 , 9999)
    hotel_user.update(otp =otp)

    sendOTPtoEmail(email , otp)

    return redirect(f'/account/verify-otp-vendor/{email}/')

def verify_otp_vendor(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelVendor.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/login-vendor/')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp-vendor/{email}/')

    return render(request , 'verify_otp.html')


@login_required(login_url='login_vendor')
def dashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)


@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id = request.user.id)

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id = ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()


        messages.success(request, "Hotel Created")
        return redirect('/account/add-hotel/')


    ameneties = Ameneties.objects.all()

    return render(request, 'vendor/add_hotel.html', context = {'ameneties' : ameneties})



@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES.get('image')
        print(image)
        if image==None:
            return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    print(id)
    print("#######")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/account/dashboard/')


@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug=slug)
    
    # Check if the current user is the owner of the hotel
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")

    if request.method == "POST":
        # Retrieve updated hotel details from the form
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        
        # Update hotel object with new details
        hotel_obj.hotel_name = hotel_name
        hotel_obj.hotel_description = hotel_description
        hotel_obj.hotel_price = hotel_price
        hotel_obj.hotel_offer_price = hotel_offer_price
        hotel_obj.hotel_location = hotel_location
        hotel_obj.save()
        
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)

    # Retrieve amenities for rendering in the template
    ameneties = Ameneties.objects.all()
    
    # Render the edit_hotel.html template with hotel and amenities as context
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties})


def logout_view(request):
    logout(request)
    messages.success(request, "Logout Success")

    return redirect('/account/login/')




@login_required(login_url='login_vendor')
def vendor_booking(request, slug):
    print("in vendor_booking func")
    hotel_obj = Hotel.objects.get(hotel_slug=slug)
    # Check if the current user is the owner of the hotel
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")
    
    try:
        booking_obj=HotelBooking.objects.filter(hotel__hotel_slug=slug)
    except HotelBooking.DoesNotExist:
        booking_obj = None
        print("No matching HotelBooking found.")
        print(booking_obj)
        booking_list=[]
        hotel=[]
        return render(request, 'vendor/vendor_booking.html', context={'booking_list': booking_list, 'hotel': hotel})
    booking_list=[]
    for i in booking_obj:
        booking_rec=[i.booking_user.first_name,
                      i.booking_user.last_name,
                      i.booking_user.email,
                      i.booking_user.phone_number,
                      i.booking_start_date,
                      i.checkin_time,
                      i.booking_end_date,
                      i.checkout_time,
                      i.price,
                      i.status]
        booking_list.append(booking_rec)
    print(booking_list)
    hotel=[hotel_obj.hotel_name]
    
    # Render the edit_hotel.html template with hotel and amenities as context
    return render(request, 'vendor/vendor_booking.html', context={'booking_list': booking_list, 'hotel': hotel})


@login_required(login_url='login_vendor')
def vendor_all_booking(request):
    print("in vendor_all_booking func")
    hotel_obj_list = Hotel.objects.filter(hotel_owner=request.user)
    booking_list=[]
    for hotel_obj in hotel_obj_list:
        try:
            booking_obj=HotelBooking.objects.filter(hotel__hotel_slug=hotel_obj.hotel_slug)
        except HotelBooking.DoesNotExist:
            booking_obj = None
            print("No matching HotelBooking found.")
            print(booking_obj)
            booking_list=[]
            hotel=[]
            return render(request, 'vendor/vendor_all_booking.html', context={'booking_list': booking_list, 'hotel': hotel})
        for i in booking_obj:
            booking_rec=[hotel_obj.hotel_name,
                        hotel_obj.hotel_location,
                        i.booking_user.first_name,
                        i.booking_user.last_name,
                        i.booking_user.email,
                        i.booking_user.phone_number,
                        i.booking_start_date,
                        i.checkin_time,
                        i.booking_end_date,
                        i.checkout_time,
                        i.price,
                        i.status]
            print(booking_rec)
            booking_list.append(booking_rec)
    print(booking_list)
    
    # Render the edit_hotel.html template with hotel and amenities as context
    return render(request, 'vendor/vendor_all_booking.html', context={'booking_list': booking_list})




@login_required(login_url='login_page')
def user_booking(request):
    hotels = Hotel.objects.all()
    # if request.GET.get('search'):
    #     hotels = hotels.filter(hotel_name__icontains = request.GET.get('search'))
    try:
        booking_obj=HotelBooking.objects.filter(booking_user__id=request.user.id)
    except HotelBooking.DoesNotExist:
        booking_obj = None
        print("No matching HotelBooking found.")
        print(booking_obj)
        booking_list=[]
        hotel=[]
        return render(request, 'user_booking.html', context = {'booking_list' : booking_list})
    booking_list=[]
    for booking_rec in booking_obj:
        i={
            "hotel_name":booking_rec.hotel.hotel_name,
            "hotel_description":booking_rec.hotel.hotel_description,
            "hotel_location":booking_rec.hotel.hotel_location,
            "hotel_slug":booking_rec.hotel.hotel_slug,
            "booking_start_date":booking_rec.booking_start_date,
            "booking_checkin_time":booking_rec.checkin_time,
            "booking_end_date":booking_rec.booking_end_date,
            "booking_checkout_time":booking_rec.checkout_time,
            "booking_price":booking_rec.price,
            "booking_status":booking_rec.status,
            "hotel":booking_rec.hotel
            # "hotel":Hotel.objects.get(hotel_slug = booking_rec.hotel.hotel_slug)
        }
        booking_list.append(i)
    print(booking_list)
    return render(request, 'user_booking.html', context = {'booking_list' : booking_list})


def checkout(request,slug):

    try:
        booking_obj=HotelBooking.objects.get(booking_slug=slug)
    except HotelBooking.DoesNotExist:
        return render(request, 'checkout.html')   
    if request.user.id != booking_obj.booking_user.id:
        return HttpResponse("You are not authorized")
    print(booking_obj.booking_slug)
    if request.method=="POST":
        print(booking_obj.booking_slug)
        print("in checkout func")
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = booking_obj.price
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        bookingslug= booking_obj.booking_slug
        return render(request, 'checkout.html', context=  {'thank':thank, 'id': id, 'booking_obj': booking_obj})
    return render(request, 'checkout.html', context=  {'booking_obj': booking_obj})


def home(request):
    return render(request,'index2.html', context=  {'key_id':RAZORPAY_KEY_ID})
    # return render(request,'index2.html', context=  {'key_id':RAZORPAY_KEY_ID,
    #           "callback_url": request.build_absolute_uri('/account/verify_signature/')})

@csrf_exempt
def create_order(request):
    # Create an order with Razorpay
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    amount = 500  # Amount in paise (e.g., ₹500)
    currency = "INR"

    order_data = {
        "amount": amount,
        "currency": currency
    }
    razorpay_order = razorpay_client.order.create(data=order_data)
    print("Exiting order function")
    return JsonResponse({
        "order_id": razorpay_order['id'],
        "amount": amount,
        "razorpay_callback_url" : RAZORPAY_CALLBACK_URL
    })
    # return {"order_id": razorpay_order['id'], "amount": amount}
    # return render(request,context={"order_id": razorpay_order['id'], "amount": amount})

def payment_success(request):
    return render(request,"success.html")

@csrf_exempt
def verify_signature(request):
    if request.method == "POST":
        print("in verify function")
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            return redirect('/account/payment_success')  # Or your success URL
        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("Signature verification failed", status=400)
    else:
        return HttpResponse("Invalid request method", status=405)
# def verify_signature(request):
#     # Data from Razorpay Checkout
#     razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
#     payment_id = request.form.get("razorpay_payment_id")
#     order_id = request.form.get("razorpay_order_id")
#     signature = request.form.get("razorpay_signature")

#     # Verify signature
#     try:
#         razorpay_client.utility.verify_payment_signature({
#             "razorpay_order_id": order_id,
#             "razorpay_payment_id": payment_id,
#             "razorpay_signature": signature
#         })
#         return redirect('/account/success')  # Redirect to success page
#     except razorpay.errors.SignatureVerificationError:
#         return "Signature verification failed", 400



# def home(request):
#     return render(request, 'index2.html', {'key_id': RAZORPAY_KEY_ID})


# from django.views.decorators.csrf import csrf_protect

# @csrf_protect
# def create_order(request):
#     import razorpay
#     import json

#     if request.method == "POST":
#         client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
#         amount = 500  # in paise = ₹5
#         order = client.order.create({
#             'amount': amount,
#             'currency': 'INR',
#             'payment_capture': 1
#         })
#         return JsonResponse({
#             'order_id': order['id'],
#             'amount': amount
#         })
#     return JsonResponse({"error": "Invalid method"}, status=405)


# @csrf_protect
# def verify_signature(request):
#     import razorpay

#     if request.method == "POST":
#         client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
#         payment_id = request.POST.get("razorpay_payment_id")
#         order_id = request.POST.get("razorpay_order_id")
#         signature = request.POST.get("razorpay_signature")

#         try:
#             client.utility.verify_payment_signature({
#                 "razorpay_order_id": order_id,
#                 "razorpay_payment_id": payment_id,
#                 "razorpay_signature": signature
#             })
#             return redirect("/account/payment_success/")
#         except razorpay.errors.SignatureVerificationError:
#             return HttpResponse("Signature verification failed", status=400)
#     return HttpResponse("Invalid method", status=405)


# def payment_success(request):
#     return render(request, "success.html")
