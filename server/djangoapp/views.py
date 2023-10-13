from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
#from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)



# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return HttpResponse('Invalid credentials')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")



# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST['password']
        
        user = User.objects.create_user(username=username, first_name=firstname, last_name=lastname, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')  
        else:
            return HttpResponse('Error')

    return render(request, 'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/e773bc6c-32ee-49e2-b433-0a1ac8f13eb0/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships": dealerships}
        # Concat all dealer's short name
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/e773bc6c-32ee-49e2-b433-0a1ac8f13eb0/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        d = None
        for dealer in dealerships:
            if int(dealer.id) == int(dealer_id):
                d = dealer
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context = {"reviews": reviews, "dealer_id": dealer_id, "dealer": d}
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)
# ...

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        context = {"dealer_id": dealer_id}
        if request.method == "POST":
            apikey = "dVIhdt97UGAYBfyMZ86Gc62OUxgya3-zzz63J1wxSQar"
            service_url = "https://1b522e13-22d2-46ba-a070-0e002f16b400-bluemix.cloudantnosqldb.appdomain.cloud"
            database_name = "reviews"

            authenticator = IAMAuthenticator(apikey)
            service = CloudantV1(authenticator=authenticator)
            service.set_service_url(service_url)

            data_to_store = {
            "_id": "f89ab52a881e13008754a2988944546",
            "_rev": "3-e3296395480f236c7405dadbdf67417",
            "id": 6,
            "name": request.user.username,
            "dealership": dealer_id,
            "review": request.POST.get('content'),
            "purchase": request.POST.get('purchasecheck'),
            "purchase_date": request.POST.get('purchasedate'),
            "car_make": "Mazda",
            "car_model": "MX-5",
            "car_year": 2003
            }

            response = service.post_document(
            db=database_name,
            document=data_to_store
            )

            if response.status_code == 201:
                print("Objeto guardado exitosamente en Cloudant.")
            else:
                print(f"Error al guardar el objeto. Código de estado: {response.status_code}")
            
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

        return render(request, 'djangoapp/add_review.html', context)

        
# ...

