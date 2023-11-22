# KFUPM Reserve
## cs50x 2022 final project
## Discrition:
Since there is a high demand for classrooms by student groups in my university (KFUPM), it is exhausting to check every classroom with your own eyes which will cost too much time.  A web reserving app with flask and sql will facilitate the process for students especially in high demand periods such as midterms and finals periods.
- Services avilable only by registration.
- Reservation times depend on other reservations and local time in saudi if the date is today.

### Video Demo
https://youtu.be/V3DX5J83ZTs
### Features
- Lookup and reserve rooms
- Cancel reservations
- Reschedule reservations
- History page
### Usage
- Register in IEX cloud to get an api key.
- Then run in VSCode command-line
- export API_KEY=(your api token)
- cd (location of app.py)
- flask run
### Used technology
- Python flask
- Sqlite3
- Css
- Html
- Javascript
- Bootstrap
### Features
- Register
    - By inserting 9 digits kfupm id, email and password
- Login
    - By inserting kfupm id and password
- Logout
    - By clicking "logout" on the right top of the page
- Find classrooms
    - Chose a date, building and room then the website will look up for you
    - Then, it will present avialable start/end timings
- Cancel reservations
    - A table of your all valid reservations will be displayed
    - By clicking "cancel" button the reservation will be gone.
- Reschudeuale reservations
    - A table of your all valid reservations will be displayed
    - By clicking "rescuduale" you will be redirected to reserve page where you select timings that fits you
- History
    - A table of your all activities with the website will be shown.

### Files
- app.py: The main backend file that controls website interaction.
- project.db: The database used for this web application with four tables
    - users table that contains users' information
    - rooms table that contains reservations information
    - history table that contains types of activity,dates and reservations places.
    - potentials table that contains information related to reservations that could be rescheduled by the user like reservation id, user id, start and end time.
- apology.html: Contians gif image that appears with errors
- home.html: Homepage of the website
- layout.html: The layout page of the whole app
- register.html: Register page
- login.html: Login page
- find.html: The page where the user selects proper place to reserve a classroom.
- found.html: The page where the user selects proper timings that are available.
- cancel.html: The page where reservations and "cancel" button appear
- reschedule.html: The page where reservations and "reschedule" button appear
- history.html: The page where activity history appear
- styles.css: Style file for some elements in layout.html
- README.md: Project documentaion
- Screenshots are avilable in project/static/screenshots