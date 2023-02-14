import os
import re

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup

# Configure applicationroject

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///calorie.db")

# Make sure API key is set

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#index
@app.route("/")
@login_required
def index():
    """Show what the user has eaten thorughout the day"""
    user_id = session["user_id"]
    food_eaten = {}

    user_calories_all = db.execute("SELECT food, grams_eaten, calorie_rate, total_calorie FROM calories_all WHERE user_id = ? AND date(datetime) = date('now')", user_id)

    for i in user_calories_all:
        food, grams = i["food"], i["grams_eaten"]
        food_eaten[food] = food_eaten.setdefault(food, 0) + grams

    # Get grams and calories of food the user has eaten that day

    total = 0
    for food, grams in food_eaten.items():
        look_up = lookup(food)
        name_food, calorie_rate_food = look_up["food"], look_up["calories"]
        total_calories = grams * calorie_rate_food / 100
        total = total + total_calories
        food_eaten[food] = (name_food, grams, calorie_rate_food, total_calories)

    # Get cash the user has available
    #
    calorie_goal = db.execute("SELECT calorie_goal FROM users WHERE id = ? ", session["user_id"])[0]['calorie_goal']
    remaining = calorie_goal - total
    return render_template("index.html",  food_eaten= food_eaten, calorie_goal=calorie_goal, remaining_calorie=remaining)


#add
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """add food items"""
    # Get method
    if request.method == "GET":
        return render_template("add.html")

    # Post method
    result = lookup(request.form.get("food").lower())
    if not result:
        return apology("invalid name for food")

    calorie_rate = result["calories"]
    food = result["food"]

    # instantiate shares variable and check the shares validity
    try:
        grams_eaten = int(request.form.get("grams"))
    except:
        return apology("Enter valid amount")
    if grams_eaten <=0:
        return apology("Enter valid amount")

    # instantiate variables
    user_id = session["user_id"]


    # update the tables
    db.execute("INSERT INTO calories_all (user_id, food, grams_eaten, calorie_rate) VALUES (?, ?, ?, ?)", user_id, food.capitalize(), grams_eaten, calorie_rate) # datetime.datetime.now()

    # Return to home page
    return redirect("/")

#history
@app.route("/history")
@login_required
def history():
    """Show history of all the food items tracked"""
    user_history = db.execute("SELECT * FROM calories_all WHERE user_id=?", session["user_id"])
    return render_template("history.html", user_history=user_history)

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#search
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """search the calories of the food item"""
    # Get method
    if request.method == "GET":
        return render_template("search.html")

    # Post method
    if not request.form.get("food"):
        return apology("Enter the name of the food")

    # Instantiating variables
    food=lookup(request.form.get("food").upper())

    # Check if the value given is valid
    if food == None:
        return apology("Invalid quote")
    name_food = food["food"]
    calories_rate_100g = (food["calories"])

    #return the template
    return render_template("searched.html", food=food, name_food=name_food, calories_rate_100g=calories_rate_100g)

#register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Post method
    if request.method == "POST":

        # check corner cases
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Invalid username and/or password")

        if request.form.get("password")!=request.form.get("confirmation"):
            return apology("Passwords don't match")

        #Passwords should:\n- be atleast 6 characters long\n-be atmost 12 characters long\n-have atleast one uppercase letter and one lowercase letter\n-have atleast one number, and one special character(#,@,$)
        if re.search(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", request.form.get("password")):
            if db.execute("SELECT * FROM users WHERE username=?", request.form.get("username")):
                return apology("Username already exists", 400)
        else:
            if len(request.form.get("password"))<6:
                return apology("Passwords must be atleast 6 characters long", 400)
            elif len(request.form.get("password"))>12:
                return apology("Passwords must be atmost 12 characters long", 400)
            else:
                return apology("Passwords must have a uppercase letter, a lowercase letter, and a special character")
        # regestering the user and instantiating a variable to later use it for session
        row=db.execute("INSERT INTO users (username, hash) VALUES (?,?)",request.form.get("username"),generate_password_hash(request.form.get("password")))

    # Get method
    else:
        return render_template("register.html")
    session["user_id"]= row

    # redirectig back to index
    return redirect("/")

#calorie goal
@app.route("/goal", methods=["GET", "POST"])
@login_required
def goal():
    """set a new calorie goal"""
    # Get method
    if request.method == "GET":
        return render_template("goal.html")

    # Post method


    # instantiate variables
    user_id = session["user_id"]


    # update the tables
    db.execute("UPDATE users SET calorie_goal = ? WHERE id = ?",request.form.get("goal"), user_id)

    # Return to home page
    return redirect("/")

#calculate calories
@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    """calculate user's calories"""
    # Get method
    if request.method == "GET":
        return render_template("calculator.html")

    # Post method
    weight_kg = float(request.form.get("weight"))
    height_cm = float(request.form.get("height"))
    age = float(request.form.get("age"))
    if request.form.get("sex") == "Woman":
        bmr = 655.1 + (9.563 * weight_kg )+ (1.850 * height_cm) - (4.676 * age)
    else:
        bmr = 66.47 + (13.75 * weight_kg )+ (5.003 * height_cm) - (4.676 * age)

    activity_lvl = float(request.form.get("activity"))

    calories = activity_lvl * bmr


    return render_template("calculated.html", calories=calories)


#remove
@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """removes specified amount of grams of the food item"""
    if request.method=="GET":
        food_today = db.execute("SELECT food FROM calories_all WHERE user_id = ? AND date(datetime) = date('now')", session["user_id"])
        return render_template("remove.html", food_today = food_today )
    if not request.form.get("food") or not request.form.get("amount"):
        return apology("Enter all the required information")

    remove_food = request.form.get("food")
    remove_amount = int(request.form.get("amount"))
    remove_calories = float(lookup(remove_food)["calories"])
    db.execute("")
    remover = db.execute("SELECT * FROM calories_all WHERE user_id = ? AND food = ? GROUP BY food", session["user_id"], remove_food)
    if not remover:
        return apology("N/A")
    if int(remover[0]["grams_eaten"])<(remove_amount):
        return apology("Invalid amount")
    db.execute("UPDATE calories_all SET grams_eaten = grams_eaten - ? WHERE id = ? AND food = ?", remove_amount, session["user_id"], remove_food)

    return redirect("/")
    


