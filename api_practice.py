from pathlib import Path
import requests
from datetime import datetime, timezone
import yaml

# city = input("Enter a city: ").strip()
codes_path = Path(__file__).with_name("weather.yaml")

with codes_path.open("r", encoding="utf-8") as file:
    WEATHER_DESCRIPTIONS = yaml.safe_load(file)

def get_weather(city):

    if not city:
        return {"error":"Enter a Valid City Name"}

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name":city, "count":1},
            timeout=10
        )

        if response.status_code == 429:
            return {"error":"City Lookup is busy. Please try again later."}

        response.raise_for_status()

    except requests.exceptions.Timeout:
        return {"error":"The weather service took too long. Please try again."}

    except requests.ConnectionError:
        return {"error":"Could not connect to the weather service."}

    except requests.exceptions.HTTPError:
        return {"error":"The city lookup service returned an HTTP error."}

    else:
        print(response.status_code)

        try:
            data = response.json()
        except ValueError:
            return {"error":"The City Lookup Service returned an invalid response"}

        if not isinstance(data, dict):
            return {"error":"City lookup service returned unexpected data."}
        
        locations = data.get("results",[])

        if not isinstance(locations, list):
            return {"error": "City lookup service returned unexpected data."}

        if not locations:
            print("No matching city found. Please check the name.")
            return {"error": "No matching city found. Please check the name."}

        location = locations[0]
        if not isinstance(location,dict):
            return {"error": "City lookup service returned unexpected data."}

        required_fields = ("name", "latitude", "longitude")

        if any(field not in location for field in required_fields):
            return {"error": "City lookup service returned incomplete city data."}
        
        matched_city = location["name"]
        region = location.get("admin1","")
        country = location.get("country","")
        latitude = location["latitude"]
        longitude = location["longitude"]

        try:
            weather_response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,apparent_temperature,cloud_cover,wind_speed_10m,is_day",
                    "daily": "sunrise,sunset",
                    "timezone": "auto"
                },
                timeout = 10
            )

            if weather_response.status_code == 429:
                return {"error":"The Weather Service is busy. Please try again later."}

            weather_response.raise_for_status()

        except requests.exceptions.Timeout:
            return {"error":"The weather service took too long. Please try again."}

        except requests.exceptions.ConnectionError:
            return {"error":"Could not connect to the weather service."}
        
        except requests.exceptions.HTTPError:
            return {"error":"The weather service returned an HTTP error."}

        else:
            print("Request Received")
            try:
                weather_data = weather_response.json()
            except ValueError:
                return {"error":"Weather service returned an invalid response."}

            try:
                current_weather = weather_data["current"]
                daily_weather = weather_data["daily"]
                current_temperature = current_weather["temperature_2m"]
                current_humidity = current_weather["relative_humidity_2m"]
                current_feels_like = current_weather["apparent_temperature"]
                weather_cloud = current_weather["cloud_cover"]
                Weather_wind = current_weather["wind_speed_10m"]
                weather_code = current_weather["weather_code"]
                weather_sunrise = daily_weather["sunrise"][0]
                weather_sunset = daily_weather["sunset"][0]
            except (KeyError, TypeError, IndexError):
                return {"error":"The weather service returned incomplete data. Please try again later."}

            condition = WEATHER_DESCRIPTIONS.get(
                weather_code,
                "Unknown weather condition"
            )

            retrieved_at = datetime.now(timezone.utc)

            return {
                "city":matched_city,
                "temperature":current_temperature,
                "humidity": current_humidity,
                "weather": condition,
                "feels_like": current_feels_like,
                "cloudy": weather_cloud,
                "wind": Weather_wind,
                "weather_code": weather_code,
                "is_day": current_weather.get("is_day", 0),
                "weather_time": current_weather.get("time"),
                "sunrise": weather_sunrise,
                "sunset": weather_sunset,
                "region":region,
                "country":country,
                "retrieved_at":retrieved_at
                }


# weather = get_weather(city)
# print("Function returned", weather)
