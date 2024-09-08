from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

MONGO_URL = "mongodb://mongodb_central:27017"
DATABASE_NAME = "office_management"
COLLECTION_NAME = "employees"

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


class Employee(BaseModel):
    id: Optional[str]
    name: str
    position: str
    department: str
    salary: float


class UpdateEmployee(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    projects: Optional[list] = None


@app.get("/employees", response_model=List[Employee])
def get_employees():
    employees = list(collection.find())
    for emp in employees:
        emp["id"] = str(emp["_id"])
        del emp["_id"]
    return employees


@app.get("/employee/{employee_id}", response_model=Employee)
def get_employee(employee_id: str):
    employee = collection.find_one({"_id": ObjectId(employee_id)})
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee["id"] = str(employee["_id"])
    del employee["_id"]
    return employee


@app.post("/employee/new_joiner", response_model=Employee)
def add_employee(employee: Employee):
    existing_employee = collection.find_one({"name": employee.name})
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee with this name already exists")
    employee_data = employee.dict()
    result = collection.insert_one(employee_data)
    employee_data["id"] = str(result.inserted_id)
    return employee_data


@app.put("/employee/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, update_data: UpdateEmployee):
    employee = collection.find_one({"_id": ObjectId(employee_id)})
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = {k: v for k, v in update_data.dict().items() if v is not None}
    collection.update_one({"_id": ObjectId(employee_id)}, {"$set": update_data})

    updated_employee = collection.find_one({"_id": ObjectId(employee_id)})
    updated_employee["id"] = str(updated_employee["_id"])
    del updated_employee["_id"]
    return updated_employee


@app.delete("/employee/{employee_id}/resignation", response_model=dict)
def delete_employee(employee_id: str):
    employee = collection.find_one({"_id": ObjectId(employee_id)})
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    collection.delete_one({"_id": ObjectId(employee_id)})
    return {"message": "Employee deleted successfully"}


@app.put("/employee/{employee_id}/promotion", response_model=dict)
def update_promotion(employee_id: str, new_position: str, new_salary: float):
    employee = collection.find_one({"_id": ObjectId(employee_id)})
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = {
        "position": new_position,
        "salary": new_salary
    }

    collection.update_one({"_id": ObjectId(employee_id)}, {"$set": update_data})
    return {"message": "Employee promotion updated successfully"}