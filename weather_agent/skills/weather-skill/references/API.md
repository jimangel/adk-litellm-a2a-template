# Weather Data API Reference

## Data Format

Each city entry in `assets/cities.json` contains:

| Field       | Type   | Description                                |
|-------------|--------|--------------------------------------------|
| `city`      | string | City name                                  |
| `country`   | string | ISO 3166-1 country code                    |
| `condition` | string | Sunny, Cloudy, Rain, Snow, Foggy, or Windy |
| `temp_c`    | number | Temperature in Celsius                     |
| `humidity`  | number | Relative humidity percentage (0–100)       |
| `wind_kph`  | number | Wind speed in km/h                         |

## Temperature Conversion

°F = (°C × 9/5) + 32

## Notes

This is mock data. In production, replace `assets/cities.json` with a live
API integration (OpenWeatherMap, WeatherAPI, AccuWeather, etc.).
