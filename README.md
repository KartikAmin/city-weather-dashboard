# City Weather Dashboard

A Flask application that displays current weather for a city using Open-Meteo, with SQLite search history and a one-hour cache.

## Features

- Search by city name and view its region and country.
- Display temperature, weather condition, humidity, cloud cover, wind speed, feels-like temperature, and retrieval time.
- Show weather effects and day/night styling in the current-weather card.
- Display the five latest saved city results without duplicate city rows.
- Reuse complete cached weather results for one hour.
- Refresh expired results in the existing database row.
- Handle empty searches, unknown cities, connection failures, timeouts, rate limits, and several malformed-response cases.
- Log initialization, searches, cache use, results, and empty-input validation.

## Technologies

Python, Flask, Requests, SQLite, PyYAML, python-dotenv, HTML, and CSS.

## Setup on Windows

Clone the repository:

```powershell
git clone https://github.com/KartikAmin/city-weather-dashboard.git
cd city-weather-dashboard
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install Flask requests PyYAML python-dotenv
```

Run the application:

```powershell
python -m flask --app app run
```

Open [the dashboard](http://127.0.0.1:5000/) in your browser.

The application creates `weather.db` automatically. Internet access is needed to retrieve fresh weather.

## Optional Development Configuration

Create a local `.env` file containing:

```dotenv
FLASK_DEBUG=1
```

This enables Flask development debugging. The `.env` file, virtual environment, and database are excluded from Git.

## Main Files

- `app.py`: Flask route, database setup, caching, search history, and weather-display settings.
- `api_practice.py`: City lookup, weather retrieval, and API error handling.
- `weather.yaml`: Weather-code descriptions.
- `templates/index.html`: Dashboard layout and weather effects.

## Search and Cache Behavior

A new city search retrieves weather and saves the result. Searches for the same city reuse a complete saved result while it is less than one hour old. Expired results are fetched again and updated.

The displayed retrieval time remains the time the weather was fetched, including when a cached result is shown.

City lookup uses the first geocoding match. Check the displayed region and country to confirm the intended location.