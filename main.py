from fastapi import FastAPI, HTTPException
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

@app.get("/students/", response_model=list[Student])
def read_students():
    return students

@app.get("/students/{id}", response_model=Student)
def read_student(id: int):
    for student in students:
        if id == student['id']:
            return student
    raise HTTPException(status_code=404, detail="Student not found")

def next_id():
    if not students:
        return 1
    max_id = max(s['id'] for s in students)
    return max_id + 1

@app.post("/students/", response_model=Student, status_code=201)
def create_student(student: Student):
    student_obj = student.model_dump(exclude_none=True)
    student_obj['id'] = next_id()
    students.append(student_obj)
    students.sort(key=lambda s: s["id"])
    return student_obj
