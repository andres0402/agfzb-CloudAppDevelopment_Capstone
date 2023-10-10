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
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "your-cloud-function-domain/reviews/review-get"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        json_data = json.dumps(reviews)
        # Return a list of dealer short name
        return HttpResponse(json_data, content_type='application/json')
# ...

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = 11
        review["review"] = "This is a great car dealer"

        json_payload = {
            "review" : "This is a great car dealer"
        }
        response = post_request("https://us-south.functions.cloud.ibm.com/api/v1/namespaces/e773bc6c-32ee-49e2-b433-0a1ac8f13eb0/actions/dealership-package/get-dealership", json_payload, dealerId = dealer_id)
        return HttpResponse(response)

        
# ...

