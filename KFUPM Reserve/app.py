import os


from datetime import datetime, date,time
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

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

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Extracting the user's information

    kfupmId = request.form.get("kfupmId")

    email = request.form.get("kfupmMail")

    password = request.form.get("password")

    conf = request.form.get("confirmation")

    # Input validation

    if len(kfupmId) != 9 or not kfupmId.isdigit():
        return apology("The academic id is invalid")

    if not email:
        return apology("Fill the email field please")

    if not password:
        return apology("Password field is required")

    if not conf:
        return apology("Password confirmation is required")

    if conf != password:
        return apology("The confirmation should match the password")

    # Check weather the user is already registered
    check = db.execute("SELECT id FROM users WHERE mail = ?;",email)

    if len(check) != 0:
        return apology("The id entered is already registered")

    password = generate_password_hash(password)

    # Adding the user to the database
    db.execute("INSERT INTO users (mail,hash,stdId) VALUES (?,?,?);", email,password,kfupmId)

    id = db.execute("SELECT id FROM users WHERE stdId = ?;",kfupmId)[0]["id"]

    session["user_id"] = id

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    # Extracting inputs
    kfupmId = request.form.get("kfupmId")

    password = request.form.get("password")

    # Validation
    if not kfupmId:
        return apology("The id field must not be empty")

    if not password:
        return apology("Password field must not be empty")

    check = db.execute("SELECT stdId, hash,id FROM users WHERE stdId = ?;", kfupmId)

    # Check the id and the password exsistance
    if len(check) != 1 or not check_password_hash(check[0]["hash"], password) :
        return apology("Ivalid id and/or password")

    session["user_id"] =  check[0]["id"]

    return redirect("/")

@app.route("/logout")
def logout():

    # Clearing the session
    session.clear()

    return render_template("login.html")


@app.route("/find", methods=["GET", "POST"])
@login_required
def find():
    if request.method == "POST":

        # Exttracting information
        id = session["user_id"]

        date = request.form.get("date")

        # Input validation

        if not date:
            return apology("There is no chosen date")

        building = request.form.get("building")

        if not building:
            return apology("No building has been chosen")

        roomNum = request.form.get("room")

        if not roomNum:
            return apology("No room number was selected")


        # Finding the local time in KSA
        (hour,Date) = dateTime()

        # Collect other reservations in the same date and place
        reservations = db.execute("SELECT * FROM rooms WHERE building = ? AND date = ? AND number = ?;", int(building), date, int(roomNum))

        # A dictionary of all the avilable timings
        starts = {6:"av",7:"av",8:"av",9:"av",10:"av",11:"av"}
        ends = {7:"av",8:"av",9:"av",10:"av",11:"av",12:"av"}

        # Mark a timing as "uv" in terms of the local time in saudi
        if Date[1] == int(date.split("-")[2]):
            updateHours(starts,ends,hour)

        if len(reservations) == 0:
            return render_template("found.html",starts = starts, ends = ends,date = date,room=roomNum,building=building,resId = 0)

        # Marking timings as "uv" with respect to other reservations
        update(reservations, starts, ends)

        return render_template("found.html",starts = starts, ends = ends,date = date,room=roomNum,building=building, resId = 0)

    else:
        return render_template("find.html")

@app.route("/found", methods=["GET", "POST"])
@login_required
def found():
    if request.method == "GET":
        return render_template("found.html")

    # Collecting inputs
    start = request.form.get("start")

    end = request.form.get("end")

    # Inputs validation
    if not start or not end:
        return apology("Fields should not be empty")

    start = start[0:2].rstrip()

    end = end[0:2].rstrip()

    room = request.form.get("room")

    date = request.form.get("date")

    building = request.form.get("building")

    resId = int(request.form.get("resId"))

    id = session["user_id"]

    # The case where the user is going to reschedule where reservation id != 0
    if resId != 0:
        # Insert information to the history table
        db.execute("INSERT INTO history (number,building,date,user_id,type) VALUES (?,?,?,?,?);", room, building,date,id,"Reschedule")
        # Updating the reservation with the current data
        db.execute("UPDATE rooms SET start = ?, end = ?,change = ? WHERE resId = ?;", start, end , 0 , resId)

    else:
        db.execute("INSERT INTO rooms (number,building,start,end,user_id,date,change) VALUES (?,?,?,?,?,?,?);",
                room,building,start,end,id,date,0)
        db.execute("INSERT INTO history (number,building,date,user_id,type) VALUES (?,?,?,?,?);", room, building,date,id,"Reserve")

    return redirect("/")

@app.route("/cancel")
@login_required
def cancel():

    # Initializing variables that represent current date and local time
    (hour,Date) = dateTime()

    id = session["user_id"]

    potentials = db.execute("SELECT * FROM potentials WHERE user_id = ?;", id)

    # Extracting all of the user's reservations
    information = db.execute("SELECT * FROM rooms WHERE user_id = ?;", id)

    manage(information, potentials)

    for info in information:

        start = info["start"]

        resDate = info["date"].split("-")

        for i in range(len(resDate)):
            resDate[i] = int(resDate[i])

        var = start

        var = int(var)

        # Dicard ended reservations from appearance by the use of local time
        if hour[0] > var and resDate[0] == Date[2] and resDate[2] == Date[1] and hour[2] == "PM":

            db.execute("DELETE FROM rooms WHERE user_id = ? AND start = ? AND end = ? AND number = ? AND date = ? AND building = ?;"
                    , id, start, info["end"], info["number"], info["date"], info["building"])

            information.remove(info)

    return render_template("cancel.html",information=information)


@app.route("/delete", methods=["POST"])
@login_required
def delete():

    # Gather user's information
    id = session["user_id"]

    number = request.form.get("number")

    building = request.form.get("building")

    startend = request.form.get("start/end").split("/")

    date = request.form.get("date")

    start = startend[0]

    end = startend[1]

    # Delete the row with the gathered data
    db.execute("DELETE FROM rooms WHERE user_id = ? AND building = ? AND number = ? AND start = ? AND end = ? AND date = ?;",
            id, building, number,start,end,date)

    # Insert a new row to history table
    db.execute("INSERT INTO history (number,building,date,user_id,type) VALUES (?,?,?,?,?);",
            number, building,date,id,"Cancel")

    return redirect("/cancel")


@app.route("/history")
@login_required
def history():

    id = session["user_id"]

    information = db.execute("SELECT * FROM history WHERE user_id = ?;", id)

    return render_template("history.html", information = information)

@app.route("/reschedule")
@login_required
def reschedule():

    # Find date and local time data
    (hour,Date) = dateTime()

    id = session["user_id"]

    potentials = db.execute("SELECT * FROM potentials WHERE user_id = ?;", id)

    # Select all reservations that belongs to the user
    information = db.execute("SELECT * FROM rooms WHERE user_id = ?;", id)

    manage(information, potentials)

    for info in information:

        start = info["start"]

        end = info["end"]

        resDate = info["date"].split("-")

        for i in range(len(resDate)):
            resDate[i] = int(resDate[i])

        var = start

        # Discard ivalid reservations from selection
        if hour[0] > var and resDate[0] == Date[2] and resDate[2] == Date[1] and hour[2] == "PM":

            # Update the database
            db.execute("DELETE FROM rooms WHERE user_id = ? AND start = ? AND end = ? AND number = ? AND date = ? AND building = ?;"
                    , id, start, info["end"], info["number"], info["date"], info["building"])

            information.remove(info)

    return render_template("reschedule.html", information = information)

@app.route("/change", methods=["POST"])
@login_required
def change():

    # Extracting user's information and inputs
    id = session["user_id"]

    number = request.form.get("number")

    building = request.form.get("building")

    date = request.form.get("date")

    startend = request.form.get("start/end").split("/")

    start = startend[0]

    end = startend[1]

    # Extracting reservation id
    info = db.execute("SELECT * FROM rooms WHERE user_id = ? AND date = ? AND number = ? AND building = ? AND start = ? AND end = ?;",
            id,date,number,building,start,end)

    resId = info[0]["resId"]

    # Mark the reservation as potential reschedule
    db.execute("UPDATE rooms SET change = ? WHERE resId = ?;", 1 , resId)
    db.execute("INSERT INTO potentials (resId,start,end,user_id) VALUES (?,?,?,?);", resId, info[0]["start"],info[0]["end"],id)

    # Find local time in saudi
    (hour,Date) = dateTime()

    # Select all reservations with same building and room
    reservations = db.execute("SELECT * FROM rooms WHERE building = ? AND date = ? AND number = ? AND resId != ?;", int(building), date, int(number),resId)

    starts = {6:"av",7:"av",8:"av",9:"av",10:"av",11:"av"}

    ends = {7:"av",8:"av",9:"av",10:"av",11:"av",12:"av"}

    # Update available hours if the time is before 12 AM and teh date is today
    if Date[1] == int(date.split("-")[2]):
        updateHours(starts,ends,hour)

    if len(reservations) == 0:
        return render_template("found.html",starts = starts, ends = ends,date = date,room=number,building=building,resId = resId)

    # Update available hours with respect to other reservations
    update(reservations, starts, ends)

    return render_template("found.html",starts = starts, ends = ends,date = date,room=number,building=building, resId = resId)

def manage(information,potentials):

    for info in information:
        start = info["start"]

        end = info["end"]

        for i in potentials:

            if i["start"] == start and i["end"] == end:
                info["change"] = 0
                db.execute("DELETE FROM potentials WHERE start = ? AND end = ?;", i["start"], i["end"])


# A function that returns local time in saudi as well as today's date
def dateTime():
    Date = datetime.now().strftime("%Y-%M-%D").split("-")[2].split("/")

    Date[2] = date.today().year

    for i in range(2):
        Date[i] = int(Date[i])

    hour =  datetime.now().strftime("%I-%M-%p").split("-")

    hour[0] = int(hour[0]) + 3

    hour[1] = int(hour[1])

    return hour,Date


# A function that updates avilable hours according to local time
def updateHours(starts, ends,hour):

    if hour[0] < 12 and hour[2] == "PM":
        for i in starts.keys():
            if hour[0] > i:
                starts[i] = "uv"

        for i in ends.keys():
            if hour[0] >= i:
                ends[i] = "uv"

# A function that updates avilable hours according to other reservations
def update(reservations, starts, ends):

    for i in reservations:

            start = i["start"]

            end = i["end"]

            for j in range (6,12):
                if start <= j < end and j in starts.keys():
                    starts[j] = "uv"
            for k in range (7,13):
                if start<k <=end and k in ends.keys():
                    ends[k] = "uv"