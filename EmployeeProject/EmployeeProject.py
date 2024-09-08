from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import requests

app = FastAPI()

MONGO_URL = "mongodb://mongodb_project:27017"
DATABASE_NAME = "project_management"
COLLECTION_NAME = "projects"

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

EMPLOYEE_CENTRAL_URL = "http://employee_central:8000"

class Project(BaseModel):
    name: str
    role: str

class EmployeeProject(BaseModel):
    id: str
    projects: List[Project] = []


@app.put("/employee/{employee_id}/promotion", response_model=dict)
def promote_employee(employee_id: str, new_position: str, new_salary: float):
    try:
        response = requests.put(f"{EMPLOYEE_CENTRAL_URL}/employee/{employee_id}/promotion",
                                params={"new_position": new_position, "new_salary": new_salary})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to promote employee in EmployeeCentral")


    return {"message": "Employee promoted successfully in both services"}


@app.post("/employee/{employee_id}/project", response_model=dict)
def add_employee_to_project(employee_id: str, project: Project):
    try:
        response = requests.get(f"{EMPLOYEE_CENTRAL_URL}/employee/{employee_id}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to fetch employee details from EmployeeCentral")

    employee_data = response.json()
    if not employee_data:
        raise HTTPException(status_code=404, detail="Employee not found in EmployeeCentral")

    employee_project = collection.find_one({"_id": employee_id})
    if not employee_project:
        employee_project = {"_id": employee_id, "projects": []}

    employee_project["projects"].append(project.dict())
    collection.update_one({"_id": employee_id}, {"$set": employee_project}, upsert=True)

    return {"message": "Project added successfully"}


@app.get("/employee/{employee_id}/projects", response_model=EmployeeProject)
def get_employee_projects(employee_id: str):
    try:
        employee_project = collection.find_one({"_id": employee_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing the database: {str(e)}")

    if not employee_project:
        raise HTTPException(status_code=404, detail="No projects found for this employee")

    projects = employee_project.get("projects", [])
    return EmployeeProject(id=employee_id, projects=projects)

