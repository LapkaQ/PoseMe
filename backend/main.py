from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import agent
# from fastapi.security.api_key import APIKeyHeader
# from config import settings

app = FastAPI()

app.include_router(agent.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)