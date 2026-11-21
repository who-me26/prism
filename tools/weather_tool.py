"""
Weather Tool for PRISM Research Assistant.
Fetches real-time weather information using Open-Meteo API (no API key required)
with an automatic fallback to wttr.in.
"""

import requests
from typing import Dict, Any, Optional

WMO_WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "🌨️"),
    75: ("Heavy snow fall", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⚡"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def _geocode_city(city_name: str) -> Optional[Dict[str, Any]]:
    """Geocode a city name to latitude and longitude using Open-Meteo Geocoding API."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    headers = {"User-Agent": "prism-research-assistant/1.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "name": result.get("name"),
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", ""),
                    "timezone": result.get("timezone", "UTC"),
                }
    except Exception:
        pass
    return None


def _get_wttr_fallback(city_name: str) -> Dict[str, Any]:
    """Fallback weather retriever using wttr.in JSON format."""
    try:
        url = f"https://wttr.in/{city_name}?format=j1"
        headers = {"User-Agent": "prism-research-assistant/1.0"}
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            current = data["current_condition"][0]
            temp_c = float(current.get("temp_C", 0))
            feels_c = float(current.get("FeelsLikeC", temp_c))
            desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
            humidity = int(current.get("humidity", 0))
            wind = float(current.get("windspeedKmph", 0))
            
            return {
                "status": "success",
                "city": city_name.title(),
                "country": "",
                "temp_c": temp_c,
                "feels_like_c": feels_c,
                "humidity": humidity,
                "wind_kmh": wind,
                "condition": desc,
                "emoji": "⛅",
                "source": "wttr.in",
                "summary": f"Live weather in {city_name.title()}: {temp_c}°C (feels like {feels_c}°C), {desc}, humidity {humidity}%, wind speed {wind} km/h.",
            }
    except Exception as e:
        return {"status": "error", "message": f"Could not fetch weather: {str(e)}"}
    return {"status": "error", "message": "Weather service unavailable."}


def get_weather(city_name: str, units: str = "metric") -> Dict[str, Any]:
    """
    Fetch comprehensive live weather data for a city.
    
    Args:
        city_name: Name of the city (e.g. "Tokyo", "London", "New York")
        units: "metric" (°C, km/h) or "imperial" (°F, mph)
        
    Returns:
        Structured dictionary with temperature, condition, humidity, wind, and forecast.
    """
    cleaned_city = city_name.strip().strip("?.,")
    if not cleaned_city:
        return {"status": "error", "message": "City name is empty."}

    geo = _geocode_city(cleaned_city)
    if not geo:
        # Try wttr.in fallback
        fallback = _get_wttr_fallback(cleaned_city)
        if fallback.get("status") == "success":
            return fallback
        return {
            "status": "error",
            "message": f"Location '{cleaned_city}' could not be resolved. Please verify the spelling.",
        }

    lat = geo["latitude"]
    lon = geo["longitude"]
    loc_display = f"{geo['name']}, {geo['country']}" if geo["country"] else geo["name"]

    forecast_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
        f"&timezone=auto"
    )

    try:
        resp = requests.get(forecast_url, timeout=7)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            w_code = curr.get("weather_code", 0)
            desc, emoji = WMO_WEATHER_CODES.get(w_code, ("Fair", "☀️"))

            temp_c = curr.get("temperature_2m", 0.0)
            feels_c = curr.get("apparent_temperature", temp_c)
            humidity = curr.get("relative_humidity_2m", 0)
            wind_kmh = curr.get("wind_speed_10m", 0.0)
            is_day = curr.get("is_day", 1) == 1

            if not is_day and emoji in ["☀️", "🌤️"]:
                emoji = "🌙"

            # Parse daily forecast (next 5 days)
            daily = data.get("daily", {})
            daily_list = []
            dates = daily.get("time", [])[:5]
            max_temps = daily.get("temperature_2m_max", [])[:5]
            min_temps = daily.get("temperature_2m_min", [])[:5]
            daily_codes = daily.get("weather_code", [])[:5]

            for d, t_max, t_min, c in zip(dates, max_temps, min_temps, daily_codes):
                c_desc, c_emoji = WMO_WEATHER_CODES.get(c, ("Fair", "⛅"))
                daily_list.append({
                    "date": d,
                    "max_c": t_max,
                    "min_c": t_min,
                    "condition": c_desc,
                    "emoji": c_emoji,
                })

            summary = (
                f"Live weather for {loc_display}: {temp_c}°C (feels like {feels_c}°C), "
                f"{desc} {emoji}. Humidity: {humidity}%, Wind: {wind_kmh} km/h."
            )

            return {
                "status": "success",
                "city": geo["name"],
                "country": geo["country"],
                "location": loc_display,
                "latitude": lat,
                "longitude": lon,
                "temp_c": temp_c,
                "feels_like_c": feels_c,
                "temp_f": round((temp_c * 9 / 5) + 32, 1),
                "feels_like_f": round((feels_c * 9 / 5) + 32, 1),
                "humidity": humidity,
                "wind_kmh": wind_kmh,
                "condition": desc,
                "emoji": emoji,
                "is_day": is_day,
                "daily_forecast": daily_list,
                "source": "Open-Meteo Live API",
                "summary": summary,
            }
    except Exception as e:
        # Fall back to wttr
        fallback = _get_wttr_fallback(cleaned_city)
        if fallback.get("status") == "success":
            return fallback
        return {"status": "error", "message": f"Error contacting weather service: {str(e)}"}

    return _get_wttr_fallback(cleaned_city)
