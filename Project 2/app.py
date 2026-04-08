# Imports
import requests
from flask import Flask, render_template, request
from time import time

_cache = {}
CACHE_TTL = 900  # 15 minutes


def cached_get(url, headers=None):
    """Cache implementation

    Args:
        url (str): The url to fetch
        headers (str, optional): The headers to use. Defaults to None.

    Returns:
        json: The json returned by the request
    """
    if url in _cache:
        data, timestamp = _cache[url]
        if time() - timestamp < CACHE_TTL:
            return data  # Yay, a hit
    # Fetch the original request if no cache hit
    response = requests.get(url, headers=headers).json()
    _cache[url] = (response, time())  # Store in cache for next time
    return response


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page for Weather Lookup Flask app.

    - GET: Shows the form to enter a ZIP code.
    - POST: Processes the submitted ZIP code, fetches city, state, latitude,
      longitude from zippopotam.us, then retrieves the weather forecast from
      api.weather.gov. Returns data to display in the template, including period,
      short forecast, temperature, and icon.

    Returns:
        Rendered 'index.html' template.
    """

    result = None

    if request.method == "POST":
        # We are asking ourselves for the info
        zip_code = request.form.get("zip")

        # Get coordinates
        zip_data = cached_get(f"https://api.zippopotam.us/us/{zip_code}")
        if zip_data != {}:
            # If we get {}, that means the zip code was in some way invalid
            city = zip_data["places"][0]["place name"]
            state = zip_data["places"][0]["state"]
            lat = zip_data["places"][0]["latitude"]
            long = zip_data["places"][0]["longitude"]

            points = cached_get(f"https://api.weather.gov/points/{lat},{long}")

            forecast_url = points["properties"]["forecast"]
            forecast_data = cached_get(forecast_url)
            periods = forecast_data["properties"]["periods"]

            hourly_url = points["properties"]["forecastHourly"]
            hourly_data = cached_get(hourly_url)
            hourly_periods = hourly_data["properties"]["periods"][:12]

            result = {
                "city": city,
                "state": state,
                "lat": lat,
                "long": long,
                "periods": periods,
                "hourly_periods": hourly_periods,
            }
        else:
            # zippopotamus did not find a location for the zip code
            result = {"error": "Invalid ZIP code."}

    # Return the webpage with the results
    return render_template("index.html", result=result)


# Run the program
if __name__ == "__main__":
    app.run(port=80)
