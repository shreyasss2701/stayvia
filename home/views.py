from django.shortcuts import render
from django.shortcuts import render,redirect,HttpResponse,HttpResponsePermanentRedirect,get_object_or_404,HttpResponseRedirect
from django.contrib import messages
from datetime import datetime
from accounts.views import login_page
from accounts.models import *
from accounts.utils import *

# Create your views here.

def about(request):
    return render(request, 'about.html')

def index(request):
    hotels = Hotel.objects.all()
    if request.GET.get('search'):
        hotels = hotels.filter(hotel_name__icontains = request.GET.get('search'))

    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
        if sort_by == "sort_low":
            hotels = hotels.order_by('hotel_offer_price')
        elif sort_by == "sort_high":
            hotels = hotels.order_by('-hotel_offer_price')
    return render(request, 'index.html', context = {'hotels' : hotels[:50]})


def hotel_details(request, slug):
    hotel = Hotel.objects.get(hotel_slug = slug)

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date , '%Y-%m-%d')
        end_date = datetime.strptime(end_date , '%Y-%m-%d')
        days_count = (end_date - start_date).days

        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date.")

            return HttpResponseRedirect(request.path_info)

        booking_slug=generateSlug(str(start_date) + str(end_date))
        HotelBooking.objects.create(
            hotel = hotel,
            booking_user = HotelUser.objects.get(id = request.user.id),
            booking_start_date = start_date,
            booking_end_date =end_date,
            price = hotel.hotel_offer_price * days_count,
            booking_slug=booking_slug
        )

        return redirect(f'/account/checkout/{booking_slug}')

        # messages.warning(request, "Booking Captured.")

        # return HttpResponseRedirect(request.path_info)


    return render(request, 'hotel_detail.html', context = {'hotel' : hotel})

# #########################################################################################33


from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from stayvia.settings import RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET,RAZORPAY_CALLBACK_URL
import json

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def homepage(request):
    currency = 'INR'
    amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = RAZORPAY_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    # context['callback_url'] = callback_url
    context['callback_url'] = "http://127.0.0.1:8000/paymenthandler/"
    print("form submitted")
    return render(request, 'index3.html', context=context)


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
from django.http import JsonResponse

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get('razorpay_payment_id', '')
            razorpay_order_id = data.get('razorpay_order_id', '')
            signature = data.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                amount = 20000  # Rs. 200 in paise
                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    return JsonResponse({"success": True, "message": "Payment Successful! Thank you."})
                except:
                    return JsonResponse({"success": False, "message": "Payment capture failed."})
            else:
                return JsonResponse({"success": False, "message": "Signature verification failed."})
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
    else:
        return JsonResponse({"success": False, "message": "Invalid HTTP method"}, status=400)
