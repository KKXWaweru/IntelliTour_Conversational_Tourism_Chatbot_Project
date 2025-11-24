from openai import OpenAI
import os
from dotenv import load_dotenv

# Import your local functions (used at runtime, not during assistant creation)
from openweathermap_service import get_weather
from amadeus_service import get_flight_offers
# You can later import get_hotels if implemented

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_assistant():
    """
    Creates a new OpenAI Assistant with retrieval and function-calling tools.
    Note: You cannot set temperature for assistants yet.
    """

    assistant = client.beta.assistants.create(
        name="IntelliTour: WhatsApp Travel and Tourism Assistant",
        instructions=(
            "You're a helpful WhatsApp assistant that assists travelers with queries "
            "related to tourism and travel. Use your knowledge base and provided tools "
            "to respond to user queries. If you don't know the answer, say so politely "
            "and suggest contacting the host. If a query is outside the travel/tourism scope, "
            "remind the user to stay within the travel and tousim scope only. Be friendly and funny."
        ),
        model="gpt-4.1",  # ✅ Always specify model!
        tools=[
            {"type": "file_search"},

            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": (
                        "Fetch the current weather for a given city using the OpenWeatherMap API. "
                        "Use this ONLY when the user asks about weather, temperature, climate, or conditions."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The name of the city (e.g., 'Nairobi')."
                            }
                        },
                        "required": ["city"]
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_flight_offers",
                    "description": (
                        "Search for flight offers between two cities using the Amadeus API. "
                        "Use this when the user asks about flights, airfares, or ticket prices."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "string",
                                "description": "Origin airport/city (IATA code or name, e.g., 'NBO' or 'Nairobi')."
                            },
                            "destination": {
                                "type": "string",
                                "description": "Destination airport/city (IATA code or name, e.g., 'DXB' or 'Dubai')."
                            },
                            "departure_date": {
                                "type": "string",
                                "description": "Departure date in YYYY-MM-DD format."
                            },
                            "return_date": {
                                "type": "string",
                                "description": "Optional return date in YYYY-MM-DD format."
                            },
                            "adults": {
                                "type": "integer",
                                "description": "Number of adult passengers.",
                                "default": 1
                            },
                        },
                        "required": ["origin", "destination", "departure_date"]
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_hotels",
                    "description": (
                        "Find available hotels in a destination city using the Amadeus API. "
                        "Use this when the user asks about hotels, accommodation, or places to stay."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_code": {
                                "type": "string",
                                "description": "IATA city code or city name (e.g., 'NBO' or 'Nairobi')."
                            }
                        },
                        "required": ["city_code"]
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_location",
                    "description": "Search for a location using a text query. Returns the top match with name, address, place_id, and coordinates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Free text search query, e.g., 'Nairobi National Park'."}
                        },
                        "required": ["query"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_location_details",
                    "description": "Given a Google place_id, return detailed information including photos and coordinates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "place_id": {"type": "string", "description": "Google Place ID."}
                        },
                        "required": ["place_id"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_place_photo",
                    "description": "Return a Google Maps Place Photo URL given a photo_reference.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "photo_reference": {"type": "string", "description": "Google photo_reference returned by place details."},
                            "max_width": {"type": "integer", "description": "Maximum width of the photo in pixels.", "default": 800},
                        },
                        "required": ["photo_reference"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_street_view_image",
                    "description": "Return a Google Street View image URL for given coordinates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lng": {"type": "number"},
                            "width": {"type": "integer", "description": "Image width in px", "default": 600},
                            "height": {"type": "integer", "description": "Image height in px", "default": 400},
                        },
                        "required": ["lat", "lng"],
                    },
                }
            }, 
            {
                "type": "function",
                "function": {
                    "name": "search_nearby_places",
                    "description": "Search for nearby points of interest using coordinates, keyword or place type. Useful for queries like 'find 5-star hotels near Nairobi'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number", "description": "Latitude of the center location"},
                            "lng": {"type": "number", "description": "Longitude of the center location"},
                            "radius": {"type": "integer", "description": "Search radius in meters", "default": 3000},
                            "keyword": {"type": "string", "description": "Search keyword filter", "nullable": True},
                            "place_type": {"type": "string", "description": "Google Maps place type filter (e.g. 'restaurant', 'hotel')", "nullable": True}
                        },
                        "required": ["lat", "lng"]
                    }
                }
            },
        ],
    )

    print("✅ Assistant created successfully!")
    print("Assistant ID:", assistant.id)
    return assistant


if __name__ == "__main__":
    create_assistant()
