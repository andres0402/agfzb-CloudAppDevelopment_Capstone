import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EmotionOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('dVIhdt97UGAYBfyMZ86Gc62OUxgya3-zzz63J1wxSQar', api_key))
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")
    
    

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        print("Network exception occurred")
    


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    authenticator = IAMAuthenticator(apikey="dVIhdt97UGAYBfyMZ86Gc62OUxgya3-zzz63J1wxSQar")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("https://1b522e13-22d2-46ba-a070-0e002f16b400-bluemix.cloudantnosqldb.appdomain.cloud")

    # Especifica el nombre de la base de datos que deseas consultar
    nombre_base_de_datos = "dealerships"

    # Realiza una consulta para obtener todos los documentos de la base de datos
    response = service.post_all_docs(db=nombre_base_de_datos, include_docs=True)

    # Accede a los documentos devueltos
    documentos = response.result

    # Los documentos están en el atributo "rows" dentro de la respuesta
    json_result = documentos["rows"]
    results = []
    # Call get_request with a URL parameter
    if json_result:
        # Get the row list in JSON as dealers
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    authenticator = IAMAuthenticator(apikey="dVIhdt97UGAYBfyMZ86Gc62OUxgya3-zzz63J1wxSQar")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("https://1b522e13-22d2-46ba-a070-0e002f16b400-bluemix.cloudantnosqldb.appdomain.cloud")

    api_key = "gvvUz5Yd1_E1SU0yeqrCJmLC5B3Do0FzMn6JK7hg4ofy"
    urlWatson = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/a85407f2-bd51-4fc1-b705-0cb2b18e63f7"
    authenticatorW = IAMAuthenticator(apikey=api_key)

    # Crea un objeto NaturalLanguageUnderstandingV1 con el autenticador
    nlu = NaturalLanguageUnderstandingV1(
        version="2021-08-01",
        authenticator=authenticatorW
    )

    nlu.set_service_url(urlWatson)

    
    
    # Especifica el nombre de la base de datos que deseas consultar
    nombre_base_de_datos = "reviews"

    # Realiza una consulta para obtener todos los documentos de la base de datos
    response = service.post_all_docs(db=nombre_base_de_datos, include_docs=True)

    # Accede a los documentos devueltos
    documentos = response.result

    # Los documentos están en el atributo "rows" dentro de la respuesta
    json_result = documentos["rows"]
    results = []
    if json_result:
        # Get the row list in JSON as dealers
        # For each dealer object
        for review in json_result:
            # Get its content in `doc` object
            review_doc = review["doc"]
            #if review_doc["dealership"] == dealer_id:
            if int(review_doc["dealership"]) == int(dealer_id): 
                responseW = nlu.analyze(
                text=review_doc["review"],
                features=Features(emotion=EmotionOptions()) )
                emocion = responseW.result["emotion"]["document"]["emotion"]
                #if review_doc["dealership"] == dealer_id:
                # Create a CarDealer object with values in `doc` object
                review_obj = DealerReview(dealership = review_doc["dealership"], name = review_doc["name"], purchase = review_doc["purchase"], review = review_doc["review"], purchase_date = review_doc["purchase_date"], car_make = review_doc["car_make"], car_model = review_doc["car_model"], car_year = review_doc["car_year"], sentiment = "emocion", id = review_doc["id"])
                review_obj.sentiment = max(emocion, key=emocion.get)
                results.append(review_obj)

    return results


def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    results = get_dealers_from_cf(url)
    for result in results:
        if result.id == dealerId:
            dealer = result
            return dealer


    # Call get_request with a URL parameter


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    params = dict()
    params["text"] = text
    params["version"] = kwargs["version"]
    params["features"] ==Features(emotion=EmotionOptions())
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                        auth=HTTPBasicAuth('dVIhdt97UGAYBfyMZ86Gc62OUxgya3-zzz63J1wxSQar', api_key))
    return response



