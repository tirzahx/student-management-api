from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    id: int | None = None
    name: str
    age: int
    gender: str
    email: str