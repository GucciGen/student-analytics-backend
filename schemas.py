from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- СХЕМИ ДЛЯ СТУДЕНТІВ ---

#Схема для створення студента
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    group_code: str
    enrollment_year: int = 2024

#Схема для відповіді на запит про студента
class StudentResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    group_code: str
    enrollment_year: int
    email: str

# --- СХЕМИ ДЛЯ ПРЕДМЕТІВ ---
class SubjectCreate(BaseModel):
    name: str
    teacher_name: Optional[str] = None

class SubjectResponse(BaseModel):
    id: str
    name: str
    teacher_name: Optional[str]

# --- СХЕМИ ДЛЯ ОЦІНОК ---
class GradeCreate(BaseModel):
    student_id: str
    subject_id: str
    score: float
    grade_type: str

class GradeResponse(BaseModel):
    id: str
    student_id: str
    subject_id: str
    score: float
    grade_type: str
    date: datetime