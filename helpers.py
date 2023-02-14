import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_food_id(food_name):
    '''
    Get the food id of the food
    '''

    api_key = os.environ.get("API_KEY")

    url = f"https://api.nal.usda.gov/fdc/v1/search?api_key={api_key}&generalSearchInput={food_name}"
    #url = f'https://api.nal.usda.gov/fdc/v1/search?api_key=4xR1xirqGjxs6zA3DPlKezl1PojgFLdUwZDQw6uX'
    response = requests.get(url)
    data = response.json()

    #if data["errors"]:
        #return None

    return data["foods"][0]["fdcId"]

def lookup(name):
    '''
    Get the details of the food item
    '''
    try:
        api_key = os.environ.get("API_KEY")
        food_id = get_food_id(name)

        url = f"https://api.nal.usda.gov/fdc/v1/food/{food_id}?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        data = response.json()

        food_name = data["description"]
        calories = None

        for food_nutrient in data["foodNutrients"]:
            if food_nutrient["nutrient"]["name"] == "Energy":
                calories = food_nutrient["amount"]
                break

        return {
            "food": food_name.capitalize(),
            "calories": calories
            }

    except (KeyError, TypeError, ValueError):
        return None
