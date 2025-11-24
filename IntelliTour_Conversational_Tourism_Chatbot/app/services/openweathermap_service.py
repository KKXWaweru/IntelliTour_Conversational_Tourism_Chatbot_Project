import datetime as dt
import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

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