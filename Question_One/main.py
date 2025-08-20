from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from student import load_students, hash_password, StudentCreate, save_students, get_current_student, StudentResponse

app = FastAPI(title="Student Portal API", version="1.0.0")

security = HTTPBasic()



@app.post("/register/", response_model=dict)
def register_student(student: StudentCreate):
    students = load_students()
    
    if student.username in students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already exists"
        )
    
    hashed_password = hash_password(student.password)
    students[student.username] = {
        "username": student.username,
        "password": hashed_password,
        "grades": student.grades
    }
    
    save_students(students)
    
    return {"message": "Student registered successfully"}

@app.post("/login/", response_model=dict)
def login_student(credentials: HTTPBasicCredentials = Depends(security)):
    student = get_current_student(credentials)
    return {"message": "Login successful", "username": student["username"]}

@app.get("/grades/", response_model=StudentResponse)
def get_grades(student: dict = Depends(get_current_student)):
    return StudentResponse(
        username=student["username"],
        grades=student["grades"]
    )

@app.get("/")
def root():
    return {"message": "Student Portal API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)