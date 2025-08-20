from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List
from datetime import datetime, date, timedelta
import json
import os
from auth import authenticate_user, create_access_token, get_current_user

app = FastAPI(title="Notes Management API", version="1.0.0")

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Note(BaseModel):
    title: str
    content: str
    date: date

class NoteCreate(BaseModel):
    title: str
    content: str
    date: date

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    date: str
    created_at: str

def get_user_notes_file(username: str) -> str:
    return f"notes_{username}.json"

def load_notes(username: str):
    notes_file = get_user_notes_file(username)
    try:
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading notes file for {username}: {e}")
        return []

def save_notes(username: str, notes_data):
    notes_file = get_user_notes_file(username)
    try:
        with open(notes_file, 'w') as f:
            json.dump(notes_data, f, indent=2, default=str)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving notes data: {str(e)}"
        )

def get_next_note_id(username: str):
    notes = load_notes(username)
    if not notes:
        return 1
    return max(note["id"] for note in notes) + 1


@app.get("/")
def root():
    return {"message": "Notes Management API"}

@app.post("/login/", response_model=Token)
def login(user_credentials: UserLogin):
    user = authenticate_user(user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/notes/", response_model=NoteResponse)
def add_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    notes = load_notes(username)
    
    note_date = note.date if note.date else date.today()
    
    new_note = {
        "id": get_next_note_id(username),
        "title": note.title,
        "content": note.content,
        "date": str(note_date),
        "created_at": datetime.now().isoformat()
    }
    
    notes.append(new_note)
    save_notes(username, notes)
    
    return NoteResponse(**new_note)

@app.get("/notes/", response_model=List[NoteResponse])
def get_notes(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    notes = load_notes(username)
    
    return [NoteResponse(**note) for note in notes]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)