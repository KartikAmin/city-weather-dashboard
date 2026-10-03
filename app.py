from flask import Flask, render_template, request
from api_practice import get_weather
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging

IST = timezone(timedelta(hours=5, minutes=30))     

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = Flask(__name__)

DATABASE = Path(__file__).with_name("weather.db")

def initialise_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS searches (
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        region TEXT,
        country TEXT,
        temperature REAL NOT NULL,
        condition TEXT,
        humidity INTEGER,
        retrieved_at TEXT NOT NULL
       )
    """)

    existing_columns={
        row[1] for row in connection.execute("PRAGMA table_info(searches)")
    }

    new_columns = {
        "feels_like": "REAL",
        "cloud_cover": "INTEGER",
        "wind_speed": "REAL",
        "weather_code": "INTEGER",
        "is_day": "INTEGER",
        "weather_time": "TEXT",
        "sunrise": "TEXT",
        "sunset": "TEXT",
    }

    for column, data_type in new_columns.items():
        if column not in existing_columns:
            connection.execute(
                f"ALTER TABLE searches ADD COLUMN {column} {data_type}"
            )

    connection.commit()
    connection.close()

initialise_database()
app.logger.info("Weather dashboard initialized; database ready")

def get_recent_Weather(city):
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    row = connection.execute("""
        SELECT *
        FROM searches
        WHERE lower(trim(city)) = lower(trim(?))
        ORDER BY id DESC
        LIMIT 1
    """,(city,)).fetchone()

    connection.close()

    if row is None:
        return None, None

    try:
        retrieved_at = datetime.fromisoformat(row["retrieved_at"])
    except ValueError:
        return None, row["id"]

    if retrieved_at.tzinfo is None:
        retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)

    age = datetime.now(timezone.utc) - retrieved_at.astimezone(timezone.utc)

    required_fields = (
        "feels_like", "cloud_cover", "wind_speed", "weather_code",
        "is_day", "weather_time", "sunrise", "sunset",
    )

    if age >= timedelta(hours=1) or any(row[field] is None for field in required_fields):
        return None, row["id"]

    weather = {
        "city": row["city"],
        "region": row["region"],
        "country": row["country"],
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "weather": row["condition"],
        "feels_like": row["feels_like"],
        "cloudy": row["cloud_cover"],
        "wind": row["wind_speed"],
        "weather_code": row["weather_code"],
        "is_day": row["is_day"],
        "weather_time": row["weather_time"],
        "sunrise": row["sunrise"],
        "sunset": row["sunset"],
        "retrieved_at": retrieved_at,
    }

    return weather, row["id"]

def save_weather(weather, row_id=None):
    connection = sqlite3.connect(DATABASE)

    values = (
        weather["city"],        
        weather["region"],
        weather["country"],
        weather["temperature"],
        weather["weather"],
        weather["humidity"],
        weather["retrieved_at"].isoformat(),
        weather["feels_like"],
        weather["cloudy"],
        weather["wind"],
        weather["weather_code"],
        weather["is_day"],
        weather["weather_time"],
        weather["sunrise"],
        weather["sunset"],
    )

    if row_id is None:
        connection.execute("""
            INSERT INTO searches(
            city, region, country, temperature, condition, humidity, retrieved_at,
            feels_like, cloud_cover, wind_speed, weather_code, is_day, weather_time,
            sunrise, sunset
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,values)

    else:
        connection.execute("""
            UPDATE searches
            SET city=?, region=?, country=?, temperature=?, condition=?, humidity=?, retrieved_at=?,
                feels_like=?, cloud_cover=?, wind_speed=?, weather_code=?, is_day=?, weather_time=?,
                sunrise=?, sunset=? 
            WHERE id=?
        """,values + (row_id,))

    connection.commit()   
    connection.close()
     

def get_sky_phase(weather_time, sunrise, sunset, is_day):
    """Return a gentle day-cycle class using the city's local API times."""
    try:
        now = datetime.fromisoformat(weather_time)
        sunrise_at = datetime.fromisoformat(sunrise)
        sunset_at = datetime.fromisoformat(sunset)
    except (TypeError, ValueError):
        return "day" if is_day else "night"

    minutes_to_sunrise = (sunrise_at - now).total_seconds() / 60
    minutes_to_sunset = (sunset_at - now).total_seconds() / 60
    if -25 <= minutes_to_sunrise <= 40:
        return "dawn"
    if -40 <= minutes_to_sunset <= 55:
        return "sunset"
    return "day" if is_day else "night"


def get_condition_theme(weather_code):
    """Group WMO weather codes into a small set of calm background effects."""
    if weather_code in {95, 96, 97, 99}:
        return "storm"
    if weather_code in {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}:
        return "rain"
    if weather_code in {71, 73, 75, 77, 85, 86}:
        return "snow"
    if weather_code in {45, 48}:
        return "fog"
    if weather_code in {0, 1}:
        return "clear"
    if weather_code in {2, 3}:
        return "cloudy"
    return "cloudy"


@app.route("/")
def dashboard():
    city = request.args.get("city","").strip()
    error = ""
    weather_city = ""
    weather_region = ""
    weather_country = ""
    weather_temp = None
    weather_humidity = None
    weather_code = None
    weather_feels = None
    weather_cloud = None
    weather_wind = None
    weather_condition = None
    weather_retrieved_at = None
    sky_phase = "day"
    condition_theme = "cloudy"
    is_windy = False
    
    if "city" in request.args and city == "":
        error = "please enter a valid City Name"
        app.logger.warning("Weather search rejected: empty city input")
    else:
        if city:
            weather, cached_row_id = get_recent_Weather(city)
            used_cache = weather is not None

            if used_cache:
                app.logger.info("Using Cached Weather for %s", weather["city"])
            else:
                app.logger.info("Weather search requested for %s", city)
                weather = get_weather(city)
            if "error" in weather:
                error = weather["error"]
                app.logger.info("Weather Search Failed: %s", error)
            else:   
                weather_city = weather["city"]  
                weather_temp = weather["temperature"]
                weather_humidity = weather["humidity"]
                weather_condition = weather["weather"]
                weather_feels = weather["feels_like"]
                weather_cloud = weather["cloudy"]
                weather_wind = weather["wind"]
                weather_code = weather["weather_code"]
                is_day = weather["is_day"]
                weather_region = weather["region"]
                weather_country = weather["country"]
                weather_retrievetime = weather["retrieved_at"]

                app.logger.info("Weather Search Succeeded for %s", weather_city)

                retrieved_at_ist = weather_retrievetime.astimezone(IST)

                weather_retrieved_at = retrieved_at_ist.strftime(
                    "%d %b %Y, %I:%M:%S %p"
                )+ " IST"

                sky_phase = get_sky_phase(
                    weather["weather_time"], weather["sunrise"], weather["sunset"], is_day
                )
                condition_theme = get_condition_theme(weather_code)
                is_windy = weather_wind >= 22

                if not used_cache:
                    save_weather(weather, cached_row_id)  

    connection = sqlite3.connect(DATABASE)
    recent_searches = connection.execute("""
    SELECT city, region, country, temperature, condition, humidity, retrieved_at
    FROM searches AS search
    where search.id = (
        SELECT MAX(candidate.id)
        FROM searches AS candidate
        WHERE lower(trim(candidate.city)) = lower(trim(search.city))
    )
    ORDER BY search.retrieved_at DESC, search.id DESC
    LIMIT 5
    """).fetchall()

    connection.close()
    
    return render_template("index.html",    
                           city=weather_city,
                           temperature=weather_temp,
                           humidity=weather_humidity,
                           feels_like= weather_feels,
                           cloud_cover=weather_cloud,
                           wind_speed=weather_wind,
                           condition=weather_condition,
                           region=weather_region,
                           country=weather_country,
                           retrieved_at=weather_retrieved_at,
                           sky_phase=sky_phase,
                           condition_theme=condition_theme,
                           is_windy=is_windy,
                           recent_searches=recent_searches,
                           error = error
                           )        
