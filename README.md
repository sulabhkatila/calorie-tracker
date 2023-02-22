# Calorie-Tracker
#### Video Demo:  https://youtu.be/TPevRuiPAuk
#### Description:

A simple application to help keep track of the calorie intake of the users. The application provides the user with the ability to add food items that they have consumed, calculate their daily caloric needs based on their gender, height, weight, and activity level, and finally, to track the total calorie intake for the day.
To run the project, first run "export API_KEY=<APIKEY>". The APIKEY is the API key provided by USDA (https://fdc.nal.usda.gov/api-guide.html).

#####Project Structure
The project consists of the following files:

######Templates Folder
The templates folder contains all the HTML templates that the project uses. The following templates are present:

add.html: for adding any food item. It has a form to enter the name of the food and the amount in grams.
apology.html: to be shown in case of a 404 error, 400 error, or other errors.
calculator.html: for calculating the calorie intake of the user. It has a form for the user to input their gender, height, weight, and activity level to calculate the calories.
calculated.html: shows the required calorie intake for the user as per the input in calculator.html.
goal.html: for the user to input their desired daily caloric intake goal.
history.html: to show all the tracked food items for the user.
index.html: shows the caloric goal, the tracked foods for the day, and the remaining calorie for the day.
login.html: has login fields, logs the user in if the user is already registered and if the password is correct.
register.html: registers the user.
search.html: to search the caloric details for any food item.
searched.html: displays the name of the food item and the caloric details of the food item.
layout.html: basic layout for the pages.

######calorie.db
This database file contains two tables, users and calorie_all.

users stores the id, username, hash of the password, and the caloric goal.
calorie_all stores the details of the tracked food for all the users.


######helpers.py
The helpers.py file contains all the helper functions that app.py requires. The following helper functions are present:

apology(message, code=400): Renders the message as an apology to the user.
login_required(f): Decorates routes to require login.
get_food_id(food_name): Get the food id of the food.
lookup(name): Get the details of the food item.

######app.py
The app.py file contains all the logic of the program. This is the main file that runs the application. The following routes are present in the file:

/: Shows what the user has eaten throughout the day.
/add: Allows the user to add food items that they have consumed.
/apology: Shows an apology in case of an error.
/calculator: Allows the user to calculate their daily caloric needs based on their gender, height, weight, and activity level.
/calculated: Shows the required calorie intake for the user as per the input in calculator.html.
/goal: Allows the user to input their desired daily caloric intake goal.
/history: Shows all the tracked food items for the user.
/login: Allows the user to log in if they are already registered and if the password

