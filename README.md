[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/blswXyO9)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20098778&assignment_repo_type=AssignmentRepo)

# INTELLITOUR - A Transformer Based Conversational Chatbot for Personalized Travel and Tour Assistance

## Overview
**IntelliTour** is a fully functional Python project demonstrating the assistive capability of intelligent machine learning models in the Tourism industry.

This project utilizes **WhatsApp** as the interaction point between users and the model. It leverages **Natural Language Processing** (NLP) powered by OpenAI's GPT-3.5 Turbo to guide users in planning trips, discovering destinations, and receiving tailored suggestions based on their preferences and past interactions.

## Key Features

### Core Capabilities
- **Conversational Travel Assistant** - Natural language interactions via WhatsApp
- **Personalized Recommendations** - Context-aware suggestions based on user preferences and conversation history
- **Multi-API Integration** - Seamless integration with multiple third-party services
- **Dynamic Data Handling** - Real-time information retrieval and processing
- **Secure Environment Configuration** - Environment-based configuration management
- **Thread Management** - Persistent conversation threads for each user
- **Rate Limit Handling** - Intelligent retry mechanisms and error recovery

### Travel Services
- **Flight Search** - Find and compare flight offers between cities
- **Hotel Search** - Discover available accommodations in destination cities
- **Weather Information** - Get current weather conditions for any city
- **Location Search** - Search for places, attractions, and points of interest
- **Nearby Places Discovery** - Find restaurants, hotels, and attractions near a location
- **Street View & Photos** - Visual previews of destinations and locations

## Technologies Used

### Backend Framework
- **Flask** - Python web framework for handling webhooks and API endpoints
- **Python 3.x** - Core programming language

### AI/ML
- **OpenAI GPT-3.5 Turbo** - Transformer-based language model for conversational AI
- **OpenAI Assistants API** - Function calling and tool integration
- **File Search** - Knowledge base retrieval capabilities

### Third-Party APIs
- **WhatsApp Business API** - Messaging platform integration
- **Amadeus Travel API** - Flight and hotel search services
- **Google Maps API** - Location search, place details, and mapping services
- **OpenWeatherMap API** - Weather information services

### Data Storage
- **Shelve** - Python database for thread persistence
- **JSON** - Data serialization and API communication

### Security & Configuration
- **python-dotenv** - Environment variable management
- **HMAC-SHA256** - Webhook signature verification
- **Flask Decorators** - Security middleware

## Project Architecture

```
IntelliTour_Conversational_Tourism_Chatbot/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── views.py                 # Webhook endpoints
│   ├── decorators/
│   │   └── security.py         # Webhook signature validation
│   ├── services/
│   │   ├── openai_service.py   # OpenAI Assistant integration
│   │   ├── googlemaps_service.py  # Google Maps API services
│   │   ├── amadeus_service.py   # Flight & hotel search
│   │   ├── openweathermap_service.py  # Weather services
│   │   └── setup_assistant.py  # Assistant configuration
│   └── utils/
│       └── whatsapp_utils.py    # WhatsApp message processing
├── start/
│   └── WhatsApp_Start.py       # WhatsApp testing utilities
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## API Integrations

### 1. OpenAI Assistant API
- **Purpose**: Core conversational AI engine
- **Features**: 
  - Function calling for external API integration
  - File search for knowledge base retrieval
  - Thread-based conversation management
  - Automatic tool selection and execution

### 2. WhatsApp Business API
- **Purpose**: User interaction interface
- **Features**:
  - Webhook-based message receiving
  - Message sending via Graph API
  - Webhook verification
  - Signature validation for security

### 3. Amadeus Travel API
- **Purpose**: Travel booking services
- **Features**:
  - Flight offer search with flexible date options
  - Hotel search with availability and pricing
  - City-to-IATA code resolution
  - Multi-passenger support

### 4. Google Maps API
- **Purpose**: Location services
- **Features**:
  - Text-based location search
  - Place details retrieval (ratings, hours, contact info)
  - Nearby places search with filters
  - Street View image generation
  - Place photo retrieval

### 5. OpenWeatherMap API
- **Purpose**: Weather information
- **Features**:
  - Current weather conditions
  - Temperature, humidity, and weather descriptions
  - Metric unit support

## Setup & Installation

### Prerequisites
- Python 3.7 or higher
- WhatsApp Business Account with API access
- API keys for:
  - OpenAI
  - Amadeus Travel
  - Google Maps
  - OpenWeatherMap

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IntelliTour_Conversational_Tourism_Chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_ASSISTANT_ID=your_assistant_id
   
   # WhatsApp Configuration
   ACCESS_TOKEN=your_whatsapp_access_token
   PHONE_NUMBER_ID=your_phone_number_id
   APP_ID=your_app_id
   APP_SECRET=your_app_secret
   VERIFY_TOKEN=your_verify_token
   VERSION=v18.0
   RECIPIENT_WAID=your_recipient_waid
   YOUR_PHONE_NUMBER=your_phone_number
   
   # Amadeus API
   AMADEUS_API_KEY=your_amadeus_key
   AMADEUS_API_SECRET=your_amadeus_secret
   
   # Google Maps API
   GOOGLEMAPS_API_KEY=your_googlemaps_key
   
   # OpenWeatherMap API
   OPENWEATHERMAP_API_KEY=your_openweathermap_key
   ```

4. **Set up OpenAI Assistant**
   - Run the assistant setup script to create and configure the assistant
   - Note the Assistant ID and add it to your `.env` file

5. **Run the application**
   ```bash
   python run.py
   ```
   The Flask server will start on `http://0.0.0.0:5000`

6. **Configure WhatsApp Webhook**
   - Set your webhook URL to: `https://your-domain.com/webhook`
   - Use the `VERIFY_TOKEN` from your `.env` file for verification

## Security Features

- **Webhook Signature Validation**: HMAC-SHA256 signature verification for all incoming WhatsApp webhook requests
- **Environment-based Configuration**: Sensitive credentials stored in environment variables
- **Request Validation**: Comprehensive validation of incoming webhook payloads
- **Error Handling**: Graceful error handling with logging for debugging

## Usage

### Starting a Conversation
Users interact with IntelliTour by sending WhatsApp messages to the configured phone number. The assistant will:
1. Process the message through OpenAI's GPT-3.5 Turbo model
2. Determine if any tools/functions need to be called
3. Execute necessary API calls (weather, flights, hotels, etc.)
4. Generate a contextual response
5. Send the reply back via WhatsApp

### Example Queries
- "What's the weather like in Nairobi?"
- "Find flights from Nairobi to Dubai on 2024-12-25"
- "Show me hotels in Paris"
- "Search for restaurants near Nairobi National Park"
- "What are some tourist attractions in Tokyo?"

##  Conversation Management

- **Thread Persistence**: Each WhatsApp user has a dedicated conversation thread stored in `user_threads.db`
- **Context Retention**: Conversation history is maintained across multiple interactions
- **Thread Management**: Automatic thread rotation when conversations exceed 50 messages to prevent token limits
- **Rate Limit Handling**: Built-in retry mechanisms with exponential backoff

## Function Calling Capabilities

The assistant can automatically call the following functions based on user queries:

1. **get_weather(city)** - Fetch weather information
2. **get_flight_offers(origin, destination, departure_date, ...)** - Search flights
3. **get_hotels(city_code)** - Find hotels
4. **search_location(query)** - Search for places
5. **get_location_details(place_id)** - Get detailed place information
6. **get_place_photo(photo_reference)** - Retrieve place photos
7. **get_street_view_image(lat, lng)** - Generate street view images
8. **search_nearby_places(lat, lng, ...)** - Find nearby points of interest

## Testing

Use the `start/WhatsApp_Start.py` script to test WhatsApp message sending functionality before deploying the full webhook.

##  Notes

- The project uses OpenAI's GPT-3.5 turbo fine-tuned model for conversational capabilities
- All API keys should be kept secure and never committed to version control
- The application requires a publicly accessible URL for WhatsApp webhook verification
- Thread database files (`user_threads.db.*`) are created automatically on first run

