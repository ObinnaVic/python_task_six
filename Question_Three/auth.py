from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import json
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBasic()

USERS_FILE = "users.json"

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        default_users = {
            "john": {
                "username": "john",
                "password": hash_password("john123"),
                "email": "john@example.com"
            },
            "jane": {
                "username": "jane", 
                "password": hash_password("jane123"),
                "email": "jane@example.com"
            }
        }
        save_users(default_users)
        return default_users
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users file: {e}")
        return {}

def save_users(users_data):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=2)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user data: {str(e)}"
        )

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    users = load_users()
    
    if credentials.username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    user_data = users[credentials.username]
    if not verify_password(credentials.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user_data