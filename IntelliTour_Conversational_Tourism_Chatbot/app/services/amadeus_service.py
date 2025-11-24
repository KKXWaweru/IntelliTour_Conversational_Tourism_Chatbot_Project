from amadeus import Client, ResponseError
import os
from dotenv import load_dotenv

load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

amadeus = Client(
    client_id = AMADEUS_API_KEY,
    client_secret = AMADEUS_API_SECRET
)

def resolve_city_to_iata(city_code_or_name):
    """
    Resolves a city name to its corresponding IATA code using the Amadeus API.
    If the input is already an IATA code (length == 3), it returns it unchanged.
    """
    try:
        if len(city_code_or_name) == 3 and city_code_or_name.isalpha():
            return city_code_or_name.upper()
        
        response = amadeus.reference_data.locations.get(
            keyword = city_code_or_name,
            subType = 'CITY'
        )

        if response.data and "iataCode" in response.data[0]:
            return response.data[0]["iataCode"]
        
        else:
            print(f"Could not find IATA code for city '{city_code_or_name}'.")
            return None
        
    except ResponseError as error:
            print(f"Error resolving city name '{city_code_or_name}': {error}")
            return None

    
def get_flight_offers(origin,destination,departure_date,return_date,adults):
    """
    Retrieve flight offers between two locations.
    Accepts either city names or IATA airport/city codes.
    
    """
    try:
        #Resolve both origin and destination
        origin_code = resolve_city_to_iata(origin)
        destination_code = resolve_city_to_iata(destination)

        if not origin_code or not destination_code:
            return {"error": "Could not resolve one or both city names to IATA codes."}
        
        params = {
            'originLocationCode': origin_code,
            'destinationLocationCode': destination_code,
            'departureDate': departure_date,
            'adults': adults
        }
        
        if return_date:
            params['returnDate'] = return_date

        response = amadeus.shopping.flight_offers_search.get(**params)
        print(f"Amadeus flight offers response received with {len(response.data)} offers.")

        #  process response.data to return a simplified summary
        offers_summary = []
        for offer in response.data[:5]:  # limit to top 5 offers to avoid overload
            summary = {
                "price": offer['price']['total'],
                "currency": offer['price']['currency'],
                "itinerary": []
            }
            for segment in offer['itineraries'][0]['segments']:
                summary["itinerary"].append({
                    "departure": segment['departure']['iataCode'],
                    "arrival": segment['arrival']['iataCode'],
                    "departure_time": segment['departure']['at'],
                    "arrival_time": segment['arrival']['at'],
                    "carrier": segment['carrierCode'],
                    "flight_number": segment['number']
                })
            offers_summary.append(summary)

        return offers_summary

    except ResponseError as error:
        print(f"Amadeus API error: {error}")
        return {"error": str(error)}
    
def get_hotels(city_code_or_name, adults=1, check_in_date=None, check_out_date=None):
    """
    Retrieve a list of hotels in a given city.
    Accepts either the IATA code or the city name.
    Uses Amadeus Hotel Offers Search API.
    """
    try:
        # Resolve the city name to its corresponding IATA Code
        city_code = resolve_city_to_iata(city_code_or_name)
        if not city_code:
            return {"error": f"Could not find the IATA code for the city '{city_code_or_name}'."}

        # First, get hotel IDs in the city using the reference data API
        try:
            hotels_response = amadeus.reference_data.locations.hotels.by_city.get(
                cityCode=city_code.upper()
            )
            
            if not hotels_response.data or len(hotels_response.data) == 0:
                return {"error": f"No hotels found in the reference data for city '{city_code_or_name}' ({city_code})."}
            
            # Get hotel IDs (limit to first 10 for performance)
            hotel_ids = [hotel['hotelId'] for hotel in hotels_response.data[:10]]
            
        except ResponseError as ref_error:
            print(f"Error getting hotel reference data: {ref_error}")
            return {"error": f"Could not retrieve hotel reference data: {str(ref_error)}"}

        # Now search for hotel offers using the hotel IDs
        hotels_summary = []
        
        # If check-in/check-out dates are provided, use hotel offers search
        if check_in_date and check_out_date:
            try:
                # Try using hotel offers search API with city code
                # This is more efficient than searching individual hotels
                try:
                    # Method 1: Try hotel_offers_search with cityCode
                    offers_response = amadeus.shopping.hotel_offers_search.get(
                        cityCode=city_code,
                        checkInDate=check_in_date,
                        checkOutDate=check_out_date,
                        adults=adults
                    )
                    
                    if offers_response.data:
                        for offer_data in offers_response.data[:5]:  # Limit to 5 results
                            hotel_info = offer_data.get('hotel', {})
                            offers = offer_data.get('offers', [])
                            
                            if offers:
                                first_offer = offers[0]
                                price_info = first_offer.get('price', {})
                                
                                hotels_summary.append({
                                    "name": hotel_info.get('name', 'N/A'),
                                    "hotel_id": hotel_info.get('hotelId', 'N/A'),
                                    "rating": hotel_info.get('rating', 'N/A'),
                                    "address": hotel_info.get('address', {}).get('lines', ['N/A'])[0] if hotel_info.get('address', {}).get('lines') else 'N/A',
                                    "price": price_info.get('total', 'N/A'),
                                    "currency": price_info.get('currency', 'N/A'),
                                    "check_in_date": check_in_date,
                                    "check_out_date": check_out_date,
                                    "contact": hotel_info.get('contact', {}).get('phone', 'N/A'),
                                })
                
                except (ResponseError, AttributeError) as search_error:
                    # If cityCode method doesn't work, try individual hotel IDs
                    print(f"City code search failed, trying individual hotels: {search_error}")
                    for hotel_id in hotel_ids[:5]:  # Limit to 5 hotels to avoid too many API calls
                        try:
                            # Method 2: Try with individual hotel IDs
                            offers_response = amadeus.shopping.hotel_offers_search.get(
                                hotelIds=hotel_id,
                                checkInDate=check_in_date,
                                checkOutDate=check_out_date,
                                adults=adults
                            )
                            
                            if offers_response.data:
                                for offer_data in offers_response.data:
                                    hotel_info = offer_data.get('hotel', {})
                                    offers = offer_data.get('offers', [])
                                    
                                    if offers:
                                        first_offer = offers[0]
                                        price_info = first_offer.get('price', {})
                                        
                                        hotels_summary.append({
                                            "name": hotel_info.get('name', 'N/A'),
                                            "hotel_id": hotel_info.get('hotelId', 'N/A'),
                                            "rating": hotel_info.get('rating', 'N/A'),
                                            "address": hotel_info.get('address', {}).get('lines', ['N/A'])[0] if hotel_info.get('address', {}).get('lines') else 'N/A',
                                            "price": price_info.get('total', 'N/A'),
                                            "currency": price_info.get('currency', 'N/A'),
                                            "check_in_date": check_in_date,
                                            "check_out_date": check_out_date,
                                            "contact": hotel_info.get('contact', {}).get('phone', 'N/A'),
                                        })
                        except ResponseError as offer_error:
                            # Skip hotels that don't have offers for the given dates
                            continue
                        
            except ResponseError as error:
                print(f"Error searching hotel offers: {error}")
                # Fall through to return basic hotel info without pricing
        else:
            # If no dates provided, return basic hotel information
            for hotel in hotels_response.data[:5]:
                hotels_summary.append({
                    "name": hotel.get('name', 'N/A'),
                    "hotel_id": hotel.get('hotelId', 'N/A'),
                    "address": hotel.get('address', {}).get('lines', ['N/A'])[0] if hotel.get('address', {}).get('lines') else 'N/A',
                    "contact": hotel.get('contact', {}).get('phone', 'N/A'),
                    "note": "Check-in and check-out dates required for pricing information"
                })

        if not hotels_summary:
            return {"error": f"No available hotel offers found for '{city_code_or_name}' ({city_code}). Try specifying check-in and check-out dates."}
        
        print(f"Found {len(hotels_summary)} hotels for city code {city_code}.")
        return hotels_summary
        
    except ResponseError as error:
        print(f"Hotel search error: {error}")
        return {"error": f"Amadeus API error: {str(error)}"}
    except Exception as e:
        print(f"Unexpected error in get_hotels: {e}")
        import traceback
        print(traceback.format_exc())
        return {"error": f"Unexpected error: {str(e)}"}

