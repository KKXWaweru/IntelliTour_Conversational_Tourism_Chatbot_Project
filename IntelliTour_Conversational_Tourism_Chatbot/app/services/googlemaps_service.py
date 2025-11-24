import os
import googlemaps
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv() 

GOOGLEMAPS_API_KEY = os.getenv("GOOGLEMAPS_API_KEY")

gmaps = googlemaps.Client(key=GOOGLEMAPS_API_KEY)

#Location search capability

def search_location(query: str):
    """
    Search for a specific location based on a text query.
    Returns the top match including name, coordinates and place_id.
    """
    results = gmaps.find_place(
        input=query,
        input_type="textquery",
        fields=["name", "geometry", "place_id", "formatted_address"]
    )

    if not results or results.get("status") != "OK":
        return {"error": "No results found"}

    candidate = results["candidates"][0]

    return {
        "name": candidate.get("name"),
        "address": candidate.get("formatted_address"),
        "place_id": candidate.get("place_id"),
        "lat": candidate["geometry"]["location"]["lat"],
        "lng": candidate["geometry"]["location"]["lng"],
    }

def search_nearby_places(lat: float, lng: float, radius: int = 3000, keyword=None, place_type=None):
    """
    Search nearby places using coordinates and optional filters.
    """
    results = gmaps.places_nearby(
        location=(lat, lng),
        radius=radius,
        keyword=keyword,
        type=place_type
    )

    if not results or results.get("status") != "OK":
        return {"error": "No nearby results found"}

    places = []

    for item in results["results"]:
        places.append({
            "name": item.get("name"),
            "address": item.get("vicinity"),
            "rating": item.get("rating"),
            "place_id": item.get("place_id")
        })

    return places

# Obtain additional information about a place
def get_location_details(place_id: str):
    """
    Retrieve detailed information about a location from its place_id.
    """
    details = gmaps.place(
        place_id=place_id,
        fields=[
            "name",
            "formatted_address",
            "rating",
            "opening_hours",
            "formatted_phone_number",
            "website",
            "photo",
            "geometry"
        ]
    )

    if not details or details.get("status") != "OK":
        return {"error": "Could not retrieve details"}

    result = details["result"]

    # Extract first photo reference if available
    photo_reference = None
    if result.get("photos"):
        photo_reference = result["photos"][0]["photo_reference"]

    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "rating": result.get("rating"),
        "phone": result.get("formatted_phone_number"),
        "website": result.get("website"),
        "opening_hours": result.get("opening_hours", {}).get("weekday_text"),
        "photo_reference": photo_reference,
        "lat": result["geometry"]["location"]["lat"],
        "lng": result["geometry"]["location"]["lng"],
    }
# Generating the photo url
def get_place_photo(photo_reference: str, max_width=800):
    """
    Returns a Google Maps Place Photo URL that is directly viewable.
    Follows the redirect from the Places Photo API to get the final image URL.
    """
    if not photo_reference:
        return {"error": "No photo_reference provided"}

    # Build the initial URL with proper parameter encoding
    base_url = "https://maps.googleapis.com/maps/api/place/photo"
    params = {
        "maxwidth": max_width,
        "photo_reference": photo_reference,
        "key": GOOGLEMAPS_API_KEY
    }
    
    # Create properly encoded URL
    photo_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        # Follow the redirect to get the actual image URL
        # Use allow_redirects=False to get the redirect location without downloading the image
        response = requests.get(photo_url, allow_redirects=False, timeout=5)
        
        if response.status_code == 302 or response.status_code == 301:
            # Get the final URL from the Location header
            final_url = response.headers.get('Location', photo_url)
            return {
                "photo_url": final_url,
                "photo_reference": photo_reference,
                "max_width": max_width
            }
        elif response.status_code == 200:
            # If no redirect, return the original URL
            return {
                "photo_url": photo_url,
                "photo_reference": photo_reference,
                "max_width": max_width
            }
        else:
            # If there's an error, return the original URL as fallback
            return {
                "photo_url": photo_url,
                "photo_reference": photo_reference,
                "max_width": max_width,
                "warning": f"Could not follow redirect (status: {response.status_code}). Using original URL."
            }
    except requests.RequestException as e:
        # If request fails, return the original URL as fallback
        return {
            "photo_url": photo_url,
            "photo_reference": photo_reference,
            "max_width": max_width,
            "warning": f"Could not resolve redirect: {str(e)}. Using original URL."
        }

#Obtain the street view of the location
def get_street_view_image(lat: float, lng: float, width=600, height=400):
    """
    Returns a Google Street View image URL.
    """
    return (
        "https://maps.googleapis.com/maps/api/streetview"
        f"?size={width}x{height}&location={lat},{lng}&key={GOOGLEMAPS_API_KEY}"
    )

