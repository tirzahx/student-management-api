from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import json

os.environ["GOOGLE_API_KEY"] = "GOOGLE_API_KEY"
os.environ["TAVILY_API_KEY"] = "TAVILY_API_KEY"

api_key = os.environ["GOOGLE_API_KEY"]

app = FastAPI()

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class Student(BaseModel):
    id: int | None = None
    name: str
    age: int
    gender: Gender
    email: str

students = [
    {'id': 1, 'name': 'Saim', 'age': 30, 'gender': 'male', 'email': 'saim@example.com'},
    {'id': 2, 'name': 'Hamza', 'age': 24, 'gender': 'male', 'email': 'hamza@example.com'},
    {'id': 3, 'name': 'Alishba', 'age': 27, 'gender': 'female', 'email': 'alishba@example.com'}
]

def add_student(input_str: str):
    """Adds a student. Input should be a JSON string with 'name', 'age', 'gender', and 'email' keys."""
    try:
        student_data = json.loads(input_str)
        name = student_data.get("name")
        age = student_data.get("age")
        gender = student_data.get("gender")
        email = student_data.get("email")

        if not all([name, age, gender, email]):
            return {"error": "Missing required fields (name, age, gender, email)."}

        if email_exists(email):
            return {"error": "Email must be unique."}

        student = {"id": next_id(), "name": name, "age": age, "gender": gender, "email": email}
        students.append(student)
        return f"Added {name} successfully."
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input format."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def update_student_data(input_str: str):
    """Updates a student by id. Input should be a JSON string with 'id' and optional 'name', 'age', 'gender', or 'email' keys."""
    try:
        update_data = json.loads(input_str)
        student_id = update_data.get("id")
        if student_id is None:
            return {"error": "Missing required 'id' field."}

        for s in students:
            if s["id"] == student_id:
                if "email" in update_data and email_exists(update_data["email"], exclude_id=student_id):
                    return {"error": "Email must be unique."}
                s.update({k: v for k, v in update_data.items() if k != "id"})
                return f"Updated student {student_id} successfully."
        return f"User {student_id} not found."
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input format."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def delete_student_data(input_str: str):
    """Deletes a student by id. Input should be a JSON string with 'id' key."""
    try:
        delete_data = json.loads(input_str)
        student_id = delete_data.get("id")
        if student_id is None:
            return {"error": "Missing required 'id' field."}

        for i, s in enumerate(students):
            if s["id"] == student_id:
                students.pop(i)
                return f"Deleted student {student_id} successfully."
        return f"Student {student_id} not found."
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input format."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def get_student(input_str: str):
    """Gets details of a student by id. Input should be a JSON string with 'id' key."""
    try:
        get_data = json.loads(input_str)
        student_id = get_data.get("id")
        if student_id is None:
            return {"error": "Missing required 'id' field."}

        for s in students:
            if s["id"] == student_id:
                return s
        return f"Student {student_id} not found."
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input format."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def list_students(input_str: str = None):
    """Lists all students. No input required."""
    return students

@app.get("/students")
def read_students():
    return students

@app.get("/students/{id}")
def read_student(id: int):
    for s in students:
        if s["id"] == id:
            return s
    raise HTTPException(status_code=404, detail=f"Student {id} not found.")

def next_id():
    if not students:
        return 1
    max_id = max(s['id'] for s in students)
    return max_id + 1

def email_exists(email: str, exclude_id: int | None = None):
    for s in students:
        if s["email"].lower() == email.lower():
            if exclude_id is None or s["id"] != exclude_id:
                return True
    return False

@app.post("/students")
def create_student(student: Student):
    return add_student(json.dumps(student.model_dump()))

@app.put("/students/{id}")
def update_student(id: int, student: Student):
    update_data = student.model_dump()
    update_data["id"] = id
    return update_student_data(json.dumps(update_data))

@app.delete("/students/{id}")
def delete_student(id: int):
    return delete_student_data(json.dumps({"id": id}))

tools = [
    Tool(name="Add Student", func=add_student, description="Adds a student. Input should be a JSON string with 'name', 'age', 'gender', and 'email' keys."),
    Tool(name="Update Student", func=update_student_data, description="Updates a student by id. Input should be a JSON string with 'id' and optional 'name', 'age', 'gender', or 'email' keys."),
    Tool(name="Delete Student", func=delete_student_data, description="Deletes a student by id. Input should be a JSON string with 'id' key."),
    Tool(name="Get Student", func=get_student, description="Gets details of a student by id. Input should be a JSON string with 'id' key."),
    Tool(name="List Students", func=list_students, description="Lists all students."),
]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=api_key
)
agent_executor = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

class AgentPrompt(BaseModel):
    prompt: str

@app.post("/agent/command")
def run_agent_command(request: AgentPrompt):
    result = agent_executor.invoke({"input": request.prompt})
    return {"result": result["output"]}

test_prompt = "Add student Sara Ali, 27, female, saraali@gmail.com"

response = agent_executor.invoke({
    "input": test_prompt
})

print("Agent output:", response["output"])
print("Students list:", students)