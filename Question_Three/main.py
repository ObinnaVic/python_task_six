from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import json
import os
from auth import get_current_user

app = FastAPI(title="Job Application Tracker API", version="1.0.0")

APPLICATIONS_FILE = "applications.json"

class JobApplication(BaseModel):
    job_title: str
    company: str
    date_applied: date
    status: str

class JobApplicationCreate(BaseModel):
    job_title: str
    company: str
    date_applied: date
    status: str = "applied"

class JobApplicationResponse(BaseModel):
    id: int
    username: str
    job_title: str
    company: str
    date_applied: date
    status: str
    created_at: str

def load_applications():
    try:
        if os.path.exists(APPLICATIONS_FILE):
            with open(APPLICATIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading applications file: {e}")
        return []

def save_applications(applications_data):
    try:
        with open(APPLICATIONS_FILE, 'w') as f:
            json.dump(applications_data, f, indent=2, default=str)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving applications data: {str(e)}"
        )

def get_next_application_id():
    applications = load_applications()
    if not applications:
        return 1
    return max(app["id"] for app in applications) + 1

def get_user_applications(username: str):
    applications = load_applications()
    return [app for app in applications if app["username"] == username]

@app.get("/")
def root():
    return {"message": "Job Application Tracker API"}

@app.post("/applications/", response_model=JobApplicationResponse)
def add_application(
    application: JobApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    applications = load_applications()
    
    new_application = {
        "id": get_next_application_id(),
        "username": current_user["username"],
        "job_title": application.job_title,
        "company": application.company,
        "date_applied": str(application.date_applied),
        "status": application.status,
        "created_at": datetime.now().isoformat()
    }
    
    applications.append(new_application)
    save_applications(applications)
    
    return JobApplicationResponse(**new_application)

@app.get("/applications/", response_model=List[JobApplicationResponse])
def get_applications(current_user: dict = Depends(get_current_user)):
    user_applications = get_user_applications(current_user["username"])
    
    return [JobApplicationResponse(**app) for app in user_applications]

@app.get("/applications/{application_id}", response_model=JobApplicationResponse)
def get_application_by_id(
    application_id: int,
    current_user: dict = Depends(get_current_user)
):
    applications = load_applications()
    
    application = next((app for app in applications if app["id"] == application_id), None)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application["username"] != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own applications"
        )
    
    return JobApplicationResponse(**application)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)