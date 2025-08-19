from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Student Portal API", version="1.0.0")

security = HTTPBasic()
