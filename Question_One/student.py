from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
import json
import os
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBasic()

class Student(BaseModel):
    username: str
    password: str
    grades: List[float] = []

class StudentCreate(BaseModel):
    username: str
    password: str
    grades: List[float] = []

class StudentResponse(BaseModel):
    username: str
    grades: List[float]

# File operations
STUDENTS_FILE = "students.json"

def load_students():
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading students file: {e}")
        return {}

def save_students(students_data):
    try:
        with open(STUDENTS_FILE, 'w') as f:
            json.dump(students_data, f, indent=2)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving student data: {str(e)}"
        )

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_student(credentials: HTTPBasicCredentials = Depends(security)):
    students = load_students()
    
    if credentials.username not in students:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    student_data = students[credentials.username]
    if not verify_password(credentials.password, student_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return student_data
