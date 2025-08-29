from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    id: int | None = None
    name: str
    age: int
    gender: str
    email: str

students = [
    {'id': 1, 'name': 'Saim', 'age': 30, 'gender': 'male', 'email': 'saim@example.com'},
    {'id': 2, 'name': 'Hamza', 'age': 24, 'gender': 'male', 'email': 'hamza@example.com'},
    {'id': 3, 'name': 'Alishba', 'age': 27, 'gender': 'female', 'email': 'alishba@example.com'}
]
