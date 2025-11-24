'''from openweathermap_service import get_weather

def main():
    city = input("Enter a city name: ")
    try:
        weather_info = get_weather(city)
        print("\n Weather data retrieved successfully:")
        print(weather_info)
    except Exception as e:
        print(f"\n Error: {e}")

if __name__ == "__main__":
    main()
    

import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError

# Load API credentials from .env
load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
    raise ValueError(" Missing AMADEUS_API_KEY or AMADEUS_API_SECRET in .env file.")

# Initialize Amadeus client
amadeus = Client(
    client_id=AMADEUS_API_KEY,
    client_secret=AMADEUS_API_SECRET
)

def test_flight_offers():
    print("\n Testing Flight Offers Search...")
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode="NBO",
            destinationLocationCode="MBA",
            departureDate="2025-12-26",
            adults=1
        )
        flights = response.data
        print(f" Found {len(flights)} flight offers.")
        # Display a sample of the results
        for i, flight in enumerate(flights[:3]):
            itineraries = flight["itineraries"][0]["segments"]
            departure = itineraries[0]["departure"]["iataCode"]
            arrival = itineraries[-1]["arrival"]["iataCode"]
            price = flight["price"]["total"]
            print(f"  {i+1}. {departure} → {arrival} | ${price}")
    except ResponseError as error:
        print(f" Flight API Error: {error}")

def test_hotels():
    print("\n Testing Hotel Search...")
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode="DXB")
        hotels = response.data
        print(f" Found {len(hotels)} hotels")
        # Display a few hotel names
        for i, hotel in enumerate(hotels[:5]):
            print(f"  {i+1}. {hotel['name']}")
    except ResponseError as error:
        print(f" Hotel API Error: {error}")

if __name__ == "__main__":
    print(" Running Amadeus API Tests...")
    test_flight_offers()
    test_hotels()
    print("\n Testing complete.")
'''
import os
from googlemaps_service import (
    search_location,
    get_location_details,
    get_place_photo,
    get_street_view_image,
    search_nearby_places

)

def test_search_location():
    print("\n===== TEST: search_location() =====")
    query = input("Enter a place to search (e.g. 'Eiffel Tower'): ")

    result = search_location(query)

    print("\n--- RESULT ---")
    print(result)

    if "error" in result:
        print("❌ Search failed.")
    else:
        print("✅ Search function is working correctly.")

def test_search_nearby_places():
    print("\n===== TEST: search_nearby_places() =====")
    print("You must provide coordinates. Example: latitude 48.8584, longitude 2.2945 (Eiffel Tower).")

    lat = float(input("Enter latitude: "))
    lng = float(input("Enter longitude: "))
    radius = input("Enter radius in meters (default 3000): ")
    keyword = input("Enter keyword (optional, press ENTER to skip): ")
    place_type = input("Enter place type (optional, e.g. 'restaurant', 'hotel'): ")

    radius = int(radius) if radius.strip() else 3000
    keyword = keyword if keyword.strip() else None
    place_type = place_type if place_type.strip() else None

    result = search_nearby_places(
        lat=lat,
        lng=lng,
        radius=radius,
        keyword=keyword,
        place_type=place_type
    )

    print("\n--- RESULT ---")
    print(result)

    if "error" in result:
        print("❌ No nearby places found.")
    else:
        print("✅ Nearby places function is working correctly.")

def test_get_location_details():
    print("\n===== TEST: get_location_details() =====")
    place_id = input("Enter a Google Maps place_id: ")

    result = get_location_details(place_id)

    print("\n--- RESULT ---")
    print(result)

    if "error" in result:
        print("❌ Could not retrieve details.")
    else:
        print("✅ Details function is working correctly.")

def test_get_place_photo():
    print("\n===== TEST: get_place_photo() =====")
    photo_reference = input("Enter a Google Maps photo_reference: ")

    result = get_place_photo(photo_reference)

    print("\n--- RESULT ---")
    print(result)

    if result:
        print("Photo URL generated successfully.")
        print(result)
        print("✅ Photo function is working correctly.")
    else:
        print("❌ Photo reference error.")

def test_get_street_view_image():
    print("\n===== TEST: get_street_view_image() =====")
    lat = float(input("Enter latitude: "))
    lng = float(input("Enter longitude: "))

    result = get_street_view_image(lat, lng)

    print("\n--- RESULT ---")
    print(result)

    if result:
        print("Street View URL generated successfully.")
        print("✅ Street view function is working correctly.")
    else:
        print("❌ Error generating street view image.")

def main():
    print("======= GOOGLE MAPS API TEST TOOL =======")
    print("Choose a function to test:")
    print("1. search_location")
    print("2. get_location_details")
    print("3. get_place_photo")
    print("4. get_street_view_image")
    print("5. search_nearby_places")

    choice = input("\nEnter choice (1-5): ")

    if choice == "1":
        test_search_location()
    elif choice == "2":
        test_get_location_details()
    elif choice == "3":
        test_get_place_photo()
    elif choice == "4":
        test_get_street_view_image()
    elif choice == "5":
        test_search_nearby_places()
    else:
        print("Invalid choice.")
4
if __name__ == "__main__":
    main()
