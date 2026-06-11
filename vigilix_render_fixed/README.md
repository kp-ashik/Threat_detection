# Vigilix AI - Advanced Safety Monitoring Frontend

This version updates the frontend flow and dashboard:
- New advanced login and signup design
- Signup with username, Gmail, password
- Login with username and password
- Main dashboard with connected cameras, total alerts, today's alerts and evidence captured
- Add camera page with no camera limit
- Location type: School, College, Mall, Railway Station, Road
- Monthly detection bar graph
- Live camera grid and zoom camera page
- Alert history with evidence screenshot, date, day, time and location
- Analytics page with monthly records

## Data storage
User accounts, camera details and alert records are saved in:

school_surveillance.db

Evidence screenshots are saved in:

evidence/

If another device opens the same running server using your laptop IP, the same user can login and see the same data. For login from anywhere, deploy this Flask app on a cloud server and use a cloud database.

## Run
python -m pip install -r requirements.txt
python app.py

Open:
http://127.0.0.1:5000
