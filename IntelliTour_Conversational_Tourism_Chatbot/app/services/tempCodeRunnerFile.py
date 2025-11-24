import datetime as dt
import os
import requests
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

amadeus = Client(
    client_id = AMADEUS_API_KEY,
    client_secret = AMADEUS_API_SECRET
)

def get_weather(city_name):
    #Fetch the conditions for a specified city 
    if not city_name:
        return {"error": "City name required."}

    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(base_url)
    data = response.json()

    if response.status_code == 200:
        main = data["main"]
        weather = data["weather"][0]["description"]
        return {
            "city": city_name,
            "temperature": main["temp"],
            "feels_like": main["feels_like"],
            "humidity": main["humidity"],
            "description": weather,
        }
    else:
        return {"error": "Could not retrieve weather data for that city."}
    

def get_flight_offers(origin,destination,departure_date,return_date,adults):
    try:
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults
        }
        
        if return_date:
            params['returnDate'] = return_date

        response = amadeus.shopping.flight_offers_search.get(**params)
        print(f"Amadeus flight offers response: {response.data}")
        return response.data
    
    except ResponseError as error:
        print(f"Amadeus API error: {error}")
        return None
    

def get_hotels(city_code):
    """
    Retrieve a list of hotels in a given city.
    """
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(citycode=city_code)
        return response.data
    except ResponseError as error:
        print(f"Hotel search error: {error}")
        print(f"Amadeus hotel offers response: {response.data}")
        return None
