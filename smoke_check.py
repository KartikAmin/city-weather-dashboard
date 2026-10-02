from datetime import datetime, timezone

import app as dashboard


def fake_weather(_city):
    return {
        "city": "Kannur",
        "temperature": 27.6,
        "humidity": 88,
        "weather": "Light rain",
        "feels_like": 31.0,
        "cloudy": 92,
        "wind": 14,
        "weather_code": 61,
        "is_day": 1,
        "weather_time": "2026-10-03T17:35",
        "sunrise": "2026-10-03T06:12",
        "sunset": "2026-10-03T18:01",
        "region": "Kerala",
        "country": "India",
        "retrieved_at": datetime.now(timezone.utc),
    }


dashboard.get_weather = fake_weather
response = dashboard.app.test_client().get("/?city=Kannur")
body = response.get_data(as_text=True)
assert response.status_code == 200
assert "sky-sunset condition-rain" in body
assert "Kannur, Kerala" in body
assert "Recent searches" in body
assert "Weather details" not in body  # Accessible label is not visible copy.
print("Passed: Flask response, sunset phase, rain class, and dashboard template render.")
