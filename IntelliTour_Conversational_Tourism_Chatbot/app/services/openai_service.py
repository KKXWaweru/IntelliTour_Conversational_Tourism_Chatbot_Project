from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
import json
from .openweathermap_service import get_weather
from .amadeus_service import get_flight_offers, get_hotels
from .googlemaps_service import (
    search_location,
    get_location_details,
    get_place_photo,
    get_street_view_image,
    search_nearby_places
)


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
GOOGLEMAPS_API_KEY = os.getenv("GOOGLEMAPS_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

THREAD_DB = "user_threads.db"

def get_or_create_thread_for_user(wa_id: str) -> str:
    """
    Returns the OpenAI thread_id associated with a WhatsApp user.
    Creates one if it doesn't exist.
    """
    try:
        with shelve.open(THREAD_DB) as db:
            if wa_id in db:
                thread_id = db[wa_id]
                logging.info(f"Existing thread found for {wa_id}: {thread_id}")
            else:
                thread = client.beta.threads.create()
                db[wa_id] = thread.id
                thread_id = thread.id
                logging.info(f"Created new thread for {wa_id}: {thread_id}")
        return thread_id
    except Exception as e:
        logging.error(f"Error accessing thread database: {e}")
        raise

def wait_for_run_completion(thread_id: str, run_id: str, timeout: int = 60) -> None:
    """
    Polls the OpenAI API until the specified run is completed or fails.
    Prevents trying to send a new message while the previous run is still active.
    """
    start_time = time.time()
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        status = run.status
        logging.info(f"Run {run_id} status: {status}")

        if status in ("completed", "failed", "cancelled", "expired"):
            break

        if time.time() - start_time > timeout:
            logging.warning(f"Run {run_id} timed out after {timeout} seconds.")
            break

        time.sleep(2)  # Wait 2 seconds before checking again


#def upload_file(path):
    # Upload a file with an "assistants" purpose
 #   file = client.files.create(
  #      file=open("../../data/airbnb-faq.pdf", "rb"), purpose="assistants"
   # )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp Travel and Tourism Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist travelers with queries based off tourism and travel. Use your knowledge base to best respond to customer queries related to travel and tourism. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. If the question is outside the travel and tourism scope, remind the user to remain within the scope for travel and tourism. Be friendly and funny.",
        tools=[{"type": "file_search"},
        {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": ( "Using the OpenWeatherMap API."
                "Do not use for flights or hotels."
                "Get the current weather for a city. "
                "Use this ONLY when the user specifically asks about weather,temperature, climate, or conditions in a city."
                            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city."
                            }
                            },
                "required": ["city"]
                        }
            } 
        },

        {
                "type": "function",
                "function": {
                    "name": "get_flight_offers",
                    "description":( "Search for flight offers between two cities using the Amadeus API."
                    "Use this when the user asks about flights, tickets, air travel,airfare or ticket prices between two cities."
                                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "string",
                                "description": "IATA code for the origin airport or the name of the city, e.g., 'NBO or Nairobi' for Nairobi."
                            },
                            "destination": {
                                "type": "string",
                                "description": "IATA code for the destination airport or name of the city, e.g., 'DXB or Dubai' for Dubai."
                            },
                            "departure_date": {
                                "type": "string",
                                "description": "Departure date in YYYY-MM-DD format."
                            },
                            "return_date": {
                                "type": "string",
                                "description": "Optional return date in YYYY-MM-DD format.",
                            },
                            "adults": {
                                "type": "integer",
                                "description": "Number of adult passengers.",
                                "default": 1
                            }
                        },
                        "required": ["origin", "destination", "departure_date"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                        "name": "get_hotels",
                        "description": (
                                    "Find available hotels in the destination city using the Amadeus API. "
                                    "Use this when the user asks about hotels, accommodation, or staying in a city."
                                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city_code": {
                                    "type": "string",
                                    "description": "IATA city code or name of the city, e.g., 'NBO or Nairobi' for Nairobi."
                                            }
                                        },
                "required": ["city_code"]
                                    }
                            }
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
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


'''def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions=f"You are having a conversation with {name}",
    )

    # Wait for completion
    # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Check if the assistant is requesting a tool
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool in tool_calls:
                 name = tool.function.name
                 import json
                 args = json.loads(tool.function.arguments or "{}")
                 logging.info(f"Tool requested: {name} with args: {args}")

            #Only run the requested tool
             if name == "get_weather":
                     city = args.get("city")
                     result = get_weather(city)

            if name == "get_flight_offers":
                origin = args.get("city")
                destination = args.get("destination")
                date = args.get("departure_date")
                result = get_flight_offers(origin,destination,date)
            
            elif name == "get_hotels":
                city = args.get("city")
                result = get_hotels(city)
            else:
                result = {"error": f"Unknown tool {name}"}
    
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(result)
            })

            for tool in tool_calls:
                if tool.function.name == "get_weather":
                    args = tool.function.arguments
                    city_name = json.loads(args).get("city")
                    result = get_weather(city_name)
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": json.dumps(result)
                    }) 
                    
          
                elif tool.function.name == "get_flight_offers":
                    args = json.loads(tool.function.arguments)
                    result = get_flight_offers(
                    origin=args["origin"],
                    destination=args["destination"],
                    departure_date=args["departure_date"],
                    return_date=args.get("return_date"),
                    adults=args.get("adults", 1)
                    )

                elif tool.function.name == "get_hotels":
                    args = json.loads(tool.function.arguments)
                    result = get_hotels(args["city_code"])

                else:
                    result = {"error": f"Unknown function call: {tool.function.name}"}
    

            # Submit the tool output back to the assistant
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status == "completed":
            break
    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

'''

def check_thread_size_and_manage(thread_id, wa_id):
    """Check thread size and manage it to prevent rate limit issues."""
    try:
        # Get message count to estimate thread size
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=100)
        message_count = len(messages.data)
        
        # If thread has more than 50 messages, create a new one to prevent token limit issues
        if message_count > 50:
            logging.info(f"Thread {thread_id} has {message_count} messages. Creating new thread to prevent rate limits.")
            new_thread = client.beta.threads.create()
            with shelve.open(THREAD_DB, writeback=True) as db:
                db[wa_id] = new_thread.id
            logging.info(f"Created new thread {new_thread.id} for user {wa_id}")
            return new_thread.id
        return thread_id
    except Exception as e:
        logging.warning(f"Error checking thread size: {e}. Continuing with existing thread.")
        return thread_id

def generate_response(message_body, wa_id, name):
    thread_id = get_or_create_thread_for_user(wa_id)
    
    # Check thread size and manage it to prevent rate limit issues
    thread_id = check_thread_size_and_manage(thread_id, wa_id)
    
    #Check for active threads
    active_runs = client.beta.threads.runs.list(thread_id=thread_id)
    for run in active_runs.data:
        if run.status in ["in_progress", "queued", "requires_action"]:
            logging.info(f"Active run {run.id} found. Waiting for it to finish...")
            wait_for_run_completion(thread_id, run.id)

    '''
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

        #Check if there is an active run
    runs = client.beta.threads.runs.list(
        thread_id=thread_id
    )
    active_runs = [r for r in runs.data if r.status not in ["completed", "failed", "cancelled"]]

    if active_runs:
        logging.warning(f"Thread {thread_id} already has an active run. Skipping message creation.")
        return "Please wait a moment while I finish processing your last request."       
    '''
    
    # Add message to thread with retry logic for rate limits
    max_retries = 3
    retry_delay = 2
    message = None
    
    for attempt in range(max_retries):
        try:
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_body,
            )
            break
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                logging.warning(f"Rate limit when adding message (attempt {attempt + 1}). Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
    
    if message is None:
        return "I'm experiencing high demand. Please try again in a moment."

    # Run the assistant with retry logic for rate limits
    run = None
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=OPENAI_ASSISTANT_ID,
            )
            break
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                logging.warning(f"Rate limit when creating run (attempt {attempt + 1}). Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
    
    if run is None:
        return "I'm experiencing high demand. Please try again in a moment."

    # Wait for run to complete and process any tool calls
    final_run, assistant_reply = wait_for_run_completion_and_get_response(thread_id, run.id)
    
    # If we got a rate limit error, handle it by creating a new thread
    if final_run.status == "failed" and hasattr(final_run, 'last_error') and final_run.last_error:
        error_code = getattr(final_run.last_error, 'code', None)
        if error_code == "rate_limit_exceeded" or "rate_limit" in str(getattr(final_run.last_error, 'message', '')).lower():
            # Create new thread for future requests
            new_thread_id, fallback_message = handle_rate_limit_error(wa_id, thread_id, str(final_run.last_error.message))
            # Return user-friendly message
            return fallback_message

    return assistant_reply

def wait_for_run_completion(thread_id, run_id, poll_interval=2, timeout = 60):
    """Wait for a run to complete, handling tool calls if needed. Returns the completed run."""
    start_time = time.time()
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        status = run.status
        logging.info(f"Run {run_id} current status: {status}")

        if status == "requires_action":
            # Process tool calls and continue waiting for completion
            logging.info(f"Run {run_id} requires action. Processing tool calls...")
            try:
                run, _ = process_tools_calls(thread_id, run)
                # After submitting tool outputs, the run will continue processing
                # Add a small delay to allow the run to transition back to in_progress
                time.sleep(1)
                # Continue polling to wait for the run to complete after tool execution
                continue
            except Exception as e:
                logging.error(f"Error processing tool calls for run {run_id}: {e}")
                import traceback
                logging.error(traceback.format_exc())
                # Re-retrieve the run to check if it failed
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                if run.status == "failed":
                    return run
                # If not failed, continue waiting
                continue

        elif status in ["completed", "failed", "cancelled"]:
            return run
        
        elif status == "queued" or status == "in_progress":
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Run {run_id} timed out waiting for completion.")
            time.sleep(poll_interval)
        
        else:
            logging.warning(f"Unexpected run status: {status}")
            time.sleep(poll_interval)

def handle_rate_limit_error(wa_id, thread_id, error_message):
    """Handle rate limit errors by creating a new thread and returning a user-friendly message."""
    logging.warning(f"Rate limit error detected. Creating new thread for user {wa_id}")
    try:
        # Create a new thread for the user
        new_thread = client.beta.threads.create()
        with shelve.open(THREAD_DB, writeback=True) as db:
            db[wa_id] = new_thread.id
        logging.info(f"Created new thread {new_thread.id} for user {wa_id}")
        return new_thread.id, "I've started a new conversation to continue helping you. Please try your request again."
    except Exception as e:
        logging.error(f"Failed to create new thread: {e}")
        return thread_id, "I'm experiencing high demand right now. Please try again in a moment."

def wait_for_run_completion_and_get_response(thread_id, run_id, poll_interval=2, timeout=60):
    """Wait for run completion and return the most recent assistant message."""
    final_run = wait_for_run_completion(thread_id, run_id, poll_interval, timeout)
    
    if final_run.status != "completed":
        # Get detailed error information
        error_message = f"Status: {final_run.status}"
        error_code = None
        if hasattr(final_run, 'last_error') and final_run.last_error:
            error_details = final_run.last_error
            error_message = f"Status: {final_run.status}"
            if hasattr(error_details, 'message'):
                error_message += f", Error: {error_details.message}"
            if hasattr(error_details, 'code'):
                error_code = error_details.code
                error_message += f", Code: {error_code}"
            logging.error(f"Run {run_id} failed. {error_message}")
        else:
            logging.error(f"Run {run_id} did not complete successfully. {error_message}")
        
        # Handle rate limit errors specifically
        if error_code == "rate_limit_exceeded" or (hasattr(final_run, 'last_error') and 
            final_run.last_error and "rate_limit" in str(final_run.last_error.message).lower()):
            # Rate limit error - return a user-friendly message
            user_message = ("I'm experiencing high demand right now. Your conversation history has grown quite long. "
                          "Please try your request again in a moment, or I can start a fresh conversation if you'd like.")
            return final_run, user_message
        
        # Even if the run failed, try to get any message that might have been created
        # Sometimes a partial response exists before the failure
        logging.info(f"Attempting to retrieve message despite run failure...")
        try:
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=5)
            for message in messages.data:
                if message.role == "assistant" and message.content:
                    for content_item in message.content:
                        if hasattr(content_item, 'text') and content_item.text:
                            reply = content_item.text.value
                            if reply and reply.strip():
                                logging.info(f"Found partial response despite run failure")
                                return final_run, reply
        except Exception as e:
            logging.warning(f"Could not retrieve partial message: {e}")
        
        # If no message found, return error
        return final_run, f"I encountered an error processing your request. {error_message}"
    
    # Retry mechanism to get the message (sometimes it takes a moment to be created)
    max_retries = 5
    retry_delay = 0.5
    for attempt in range(max_retries):
        if attempt > 0:
            time.sleep(retry_delay)
            logging.info(f"Retrying message retrieval (attempt {attempt + 1}/{max_retries})")
    
        # Try to get the message ID from run steps first (more reliable)
        try:
            run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id, limit=20)
            # Steps are in reverse chronological order, so we need to find the message_creation step
            for step in run_steps.data:
                if hasattr(step, 'step_details'):
                    step_details = step.step_details
                    # Check for message creation step
                    if hasattr(step_details, 'message_creation'):
                        message_id = step_details.message_creation.message_id
                        # Retrieve the specific message
                        message = client.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)
                        if message.role == "assistant" and message.content:
                            if len(message.content) > 0:
                                # Handle different content types
                                content_item = message.content[0]
                                if hasattr(content_item, 'text') and content_item.text:
                                    assistant_reply = content_item.text.value
                                    if assistant_reply and assistant_reply.strip():
                                        logging.info(f"Assistant reply retrieved from run step (message_id: {message_id}): {assistant_reply[:100]}...")
                                        return final_run, assistant_reply
        except Exception as e:
            logging.warning(f"Could not retrieve message from run steps (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                import traceback
                logging.debug(traceback.format_exc())
        
        # Fallback: Get the most recent messages (they are returned in reverse chronological order)
        try:
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=10)
            
            # Find the most recent assistant message that belongs to this run
            # Messages are ordered newest first, so we look for the first assistant message
            for message in messages.data:
                if message.role == "assistant":
                    # Check if message has content
                    if message.content and len(message.content) > 0:
                        # Handle different content types - iterate through content items
                        for content_item in message.content:
                            # Check if it's a text message (not just tool calls)
                            if hasattr(content_item, 'text') and content_item.text:
                                assistant_reply = content_item.text.value
                                if assistant_reply and assistant_reply.strip():  # Ensure it's not empty
                                    logging.info(f"Assistant reply retrieved from message list (message_id: {message.id}): {assistant_reply[:100]}...")
                                    return final_run, assistant_reply
        except Exception as e:
            logging.error(f"Error retrieving messages (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                import traceback
                logging.debug(traceback.format_exc())
    
    # Fallback if no assistant message found after all retries
    logging.error(f"No assistant message found in thread after run completion (tried {max_retries} times)")
    return final_run, "I apologize, but I couldn't generate a response. Please try again."
   
def process_tools_calls(thread_id, run):
    """
    Process tool calls for a run that requires action.
    Returns the updated run object (after submitting tool outputs).
    Note: This function does NOT wait for completion or retrieve messages.
    That is handled by wait_for_run_completion_and_get_response.
    """
    if run.required_action is None:
        logging.warning("process_tools_calls called but run.required_action is None")
        return run, None

    if not hasattr(run.required_action, "submit_tool_outputs") or run.required_action.submit_tool_outputs is None:
        logging.warning("process_tools_calls called but no tool outputs to submit")
        return run, None

    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool in tool_calls:
        try:
            #Weather tool
            if tool.function.name == "get_weather":
                args = json.loads(tool.function.arguments)
                city = args.get("city_name") or args.get("city")
                logging.info(f"Weather tool called for city: {city}")
                result = get_weather(city)

            #Flight search tool
            elif tool.function.name == "get_flight_offers":
                args = json.loads(tool.function.arguments)
                logging.info(f"Flight offers requested: {args}")
                result = get_flight_offers(
                    origin=args["origin"],
                    destination=args["destination"],
                    departure_date=args["departure_date"],
                    return_date=args.get("return_date"),
                    adults=args.get("adults", 1)
                )

            #Hotel search tool
            elif tool.function.name == "get_hotels":
                args = json.loads(tool.function.arguments)
                logging.info(f"Hotels requested for city code: {args.get('city_code')}")
                result = get_hotels(args["city_code"])
            
            #Location Search
            elif tool.function.name == "search_location":
                args = json.loads(tool.function.arguments)
                logging.info(f"Location search requested: {args}")
                result = search_location(query=args["query"])
            
            # Get Location Details
            elif tool.function.name == "get_location_details":
                args = json.loads(tool.function.arguments)
                logging.info(f"Location details requested: {args}")
                result = get_location_details(place_id=args["place_id"])
            
            #Get Place Photo
            elif tool.function.name == "get_place_photo":
                args = json.loads(tool.function.arguments)
                logging.info(f"Place photo requested: {args}")
                result = get_place_photo(
                    photo_reference=args["photo_reference"],
                    max_width=args.get("max_width", 800)
                )
            
            #Street View Image
            elif tool.function.name == "get_street_view_image":
                args = json.loads(tool.function.arguments)
                logging.info(f"Street view requested: {args}")
                result = get_street_view_image(
                    lat=args["lat"],
                    lng=args["lng"],
                    width=args.get("width", 600),
                    height=args.get("height", 400)
                )
            
            # Search nearby places tool
            elif tool.function.name == "search_nearby_places":
                args = json.loads(tool.function.arguments)
                logging.info(f"Nearby places requested: {args}")
                result = search_nearby_places(
                    lat=args["lat"],
                    lng=args["lng"],
                    radius=args.get("radius", 3000),
                    keyword=args.get("keyword"),
                    place_type=args.get("place_type")
                )

            else:
                result = {"error": f"Unknown function call: {tool.function.name}"}
                logging.warning(f"Unknown tool function: {tool.function.name}")

        except Exception as e:
            # Catch any errors during tool execution and return error result
            error_msg = str(e)
            logging.error(f"Error executing tool {tool.function.name}: {error_msg}")
            import traceback
            logging.error(traceback.format_exc())
            result = {"error": f"Tool execution failed: {error_msg}"}

        # Always append result, even if it's an error
        try:
            # Ensure result can be serialized to JSON
            if not isinstance(result, (dict, list, str, int, float, bool, type(None))):
                result = {"error": f"Tool returned invalid result type: {type(result)}"}
            
            output_str = json.dumps(result)
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": output_str
            })
        except (TypeError, ValueError) as e:
            # If JSON serialization fails, send error message
            logging.error(f"Failed to serialize tool result to JSON: {e}")
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps({"error": f"Failed to serialize result: {str(e)}"})
            })

    # Submit the tool outputs
    if tool_outputs:
        logging.info(f"Submitting {len(tool_outputs)} tool outputs for run {run.id}")
        for i, output in enumerate(tool_outputs):
            logging.debug(f"Tool output {i+1}: tool_call_id={output['tool_call_id']}, output_length={len(output['output'])}")
        
        try:
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            logging.info(f"Tool outputs successfully submitted for run {run.id}")
            # Retrieve the updated run to get the new status
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            logging.info(f"Run {run.id} status after tool submission: {run.status}")
        except Exception as e:
            logging.error(f"Error submitting tool outputs: {e}")
            import traceback
            logging.error(traceback.format_exc())
            raise
    else:
        logging.warning("No tool outputs to submit")
    
    return run, None