"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice teamwork and compete in inter-school basketball games",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Build swimming skills and train for swim meets",
        "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and creative design",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stagecraft, and put on theater productions",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["charlotte@mergington.edu", "ethan@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["oliver@mergington.edu", "amelia@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore science projects",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["jackson@mergington.edu", "harper@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
