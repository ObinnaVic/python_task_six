from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import json
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBasic()

ADMIN_ROLE = "admin"
CUSTOMER_ROLE = "customer"

USERS_FILE = "users.json"

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        default_users = {
            "admin": {
                "username": "admin",
                "role": ADMIN_ROLE
            },
            "user1": {
                "username": "user1",
                "role": CUSTOMER_ROLE
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