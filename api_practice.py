import requests

city = input("Enter a city: ").strip()

if not city:
    print("Enter a valid City name")
    raise SystemExit
try:
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name":city, "count":1},
        timeout=10
    )
except requests.exceptions.Timeout:
    print("The weather service took too long. Please try again.")

except requests.ConnectionError:
    print("Could not connect to the weather service.")

else:
    print(response.status_code)

    data = response.json()
    locations = data.get("results",[])

    if not locations:
        print("No matching city found. Please check the name.")
        raise SystemExit

    location = locations[0]
    latitude = location["latitude"]
    longitude = location["longitude"]

    try:
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m"
            },
            timeout = 10
        )
    except requests.exceptions.Timeout:
        print ("The weather service took too long. Please try again.")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the weather service.") 

    else:
        print("Request Received")
        weather_data = weather_response.json()
        # print (weather_data)
        current_weather = weather_data["current"]
        current_temperature = current_weather["temperature_2m"]
        print("temperature:",current_temperature, "\u00B0C")


