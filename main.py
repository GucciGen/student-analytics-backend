from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from mongoengine import connect, disconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Student, Subject, Grade
from schemas import StudentCreate, StudentResponse, SubjectCreate, SubjectResponse, GradeCreate, GradeResponse
from auth import (
    auth_router, 
    oauth2_scheme, 
    require_admin, 
    get_password_hash, 
    generate_random_password, 
    generate_student_email
)

app = FastAPI(
    title="Student Analytics API",
    description="Бекенд для системи аналітики успішності студентів"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
async def startup_db_client():
    connect(host="mongodb+srv://sviaticrrocer_db_user:KhhdFOGFIq98QMIx@cluster0.ncqipo7.mongodb.net/student_analytics?retryWrites=true&w=majority")
    print("Підключено до MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    disconnect()
    print("Відключено від MongoDB")

@app.get("/api/healthcheck", tags=["System"])
async def healthcheck():
    return {"status": "ok", "message": "FastAPI працює, інфраструктура готова"}


# ==========================================
# РОБОТА ЗІ СТУДЕНТАМИ (CRUD)
# ==========================================

@app.post("/api/students", tags=["Students"])
async def create_student(student_data: StudentCreate, current_user = Depends(require_admin)):
    """
    Створення нового студента, доступно ТІЛЬКИ для "admin".
    Автоматично генерує пошту та пароль для доступу студента.
    """
    # 1. Генеруємо унікальні доступи
    new_email = generate_student_email()
    raw_password = generate_random_password()
    
    # 2. Хешуємо пароль перед збереженням! 
    # (Заміни get_password_hash на функцію, яку ти використовуєш для логіна)
    hashed_pwd = get_password_hash(raw_password)

    # 3. Створюємо запис у базі даних
    new_student = Student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        group_code=student_data.group_code,
        enrollment_year=student_data.enrollment_year,
        email=new_email,             # <--- Додаємо пошту
        hashed_password=hashed_pwd,  # <--- Додаємо зашифрований пароль
        role="student"               # <--- Встановлюємо роль
    )
    new_student.save()
    
    # 4. Повертаємо створеного студента + ЗГЕНЕРОВАНІ ДАНІ на фронтенд
    return {
        "message": "Студента успішно створено",
        "student": {
            "id": str(new_student.id),
            "first_name": new_student.first_name,
            "last_name": new_student.last_name,
            "group_code": new_student.group_code
        },
        "credentials": {
            "email": new_email,
            "password": raw_password  # Цей пароль фронтенд покаже адміну лише 1 раз!
        }
    }

@app.get("/api/students", response_model=list[StudentResponse], tags=["Students"])
async def get_all_students():
    # Отримуємо всіх студентів з бази
    students_db = Student.objects()
    
    # Форматуємо для відповіді API
    result = []
    for s in students_db:
        result.append({
            "id": str(s.id),
            "first_name": s.first_name,
            "last_name": s.last_name,
            "group_code": s.group_code,
            "enrollment_year": s.enrollment_year,
            "email": s.email
        })
    return result

@app.delete("/api/students/{student_id}", tags=["Students"])
async def delete_student(student_id: str, current_user = Depends(require_admin)):
    """
    Видалення студента. Доступно ТІЛЬКИ для користувачів з роллю 'admin'.
    """
    # Шукаємо студента за його ID
    student = Student.objects(id=student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Студента не знайдено")
        
    # Видаляємо з бази
    student.delete()
    return {"message": f"Студента з ID {student_id} успішно видалено адміністратором"}

@app.post("/api/students/bulk-upload", tags=["Students"])
async def bulk_upload_students(file: UploadFile = File(...)):
    """
    Масове завантаження студентів з CSV файлу.
    Файл обов'язково повинен мати колонки: first_name, last_name, group_code, enrollment_year
    """
    # 1. Читаємо файл, який прислав користувач, у пам'ять
    content = await file.read()
    
    try:
        # 2. Магія Pandas: читаємо CSV файл (розпізнає і кому, і крапку з комою)
        df = pd.read_csv(io.BytesIO(content), sep=None, engine='python')
        
        # 3. Перевіряємо, чи правильні назви колонок у файлі
        required_columns = {"first_name", "last_name", "group_code", "enrollment_year"}
        if not required_columns.issubset(df.columns):
            return {"error": f"Помилка! Файл має містити такі колонки: {required_columns}"}
            
        # 4. Проходимося по кожному рядку таблиці і зберігаємо в MongoDB
        added_count = 0
        for index, row in df.iterrows():
            new_student = Student(
                first_name=str(row['first_name']),
                last_name=str(row['last_name']),
                group_code=str(row['group_code']),
                enrollment_year=int(row['enrollment_year']) if pd.notna(row['enrollment_year']) else 2024
            )
            new_student.save()
            added_count += 1
            
        return {"message": f"Супер! Успішно додано {added_count} студентів до бази!"}
    
    except Exception as e:
        return {"error": f"Помилка обробки файлу: {str(e)}"}
# ==========================================
# РОБОТА З ПРЕДМЕТАМИ
# ==========================================
@app.post("/api/subjects", response_model=SubjectResponse, tags=["Subjects"])
async def create_subject(subject_data: SubjectCreate):
    new_subject = Subject(
        name=subject_data.name, 
        teacher_name=subject_data.teacher_name
    )
    new_subject.save()
    return {
        "id": str(new_subject.id), 
        "name": new_subject.name, 
        "teacher_name": new_subject.teacher_name
    }

@app.get("/api/subjects", response_model=list[SubjectResponse], tags=["Subjects"])
async def get_all_subjects():
    subjects_db = Subject.objects()
    return [{"id": str(s.id), "name": s.name, "teacher_name": s.teacher_name} for s in subjects_db]

# ==========================================
# РОБОТА З ОЦІНКАМИ (ЖУРНАЛ)
# ==========================================
@app.post("/api/grades", response_model=GradeResponse, tags=["Grades"])
async def add_grade(grade_data: GradeCreate, token: str = Depends(oauth2_scheme)):
    # 1. Перевіряємо, чи існують такий студент і такий предмет у базі
    student = Student.objects(id=grade_data.student_id).first()
    subject = Subject.objects(id=grade_data.subject_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Студента не знайдено")
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не знайдено")
        
    # 2. Зберігаємо оцінку
    new_grade = Grade(
        student=student,
        subject=subject,
        score=grade_data.score,
        grade_type=grade_data.grade_type
    )
    new_grade.save()
    
    # 3. Повертаємо результат
    return {
        "id": str(new_grade.id),
        "student_id": str(new_grade.student.id),
        "subject_id": str(new_grade.subject.id),
        "score": new_grade.score,
        "grade_type": new_grade.grade_type,
        "date": new_grade.date
    }

@app.get("/api/grades", response_model=list[GradeResponse], tags=["Grades"])
async def get_all_grades():
    # Дістаємо всі оцінки з бази
    grades_db = Grade.objects()
    
    result = []
    for g in grades_db:
        result.append({
            "id": str(g.id),
            "student_id": str(g.student.id),
            "subject_id": str(g.subject.id),
            "score": g.score,
            "grade_type": g.grade_type,
            "date": g.date
        })
    return result

# ==========================================
# АНАЛІТИКА (PANDAS)
# ==========================================
@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_dashboard_data():
    #1. Дістаємо всі оцінки з бази
    grades_db = Grade.objects()

    #Якщо оцінок немає, повертаємо порожній список
    if not grades_db:
        return {"message": "Немає даних для аналізу"}

    #2. Готуємо дані для Pandas
    data = []
    for g in grades_db:
        data.append({
            "group_code": g.student.group_code,
            "subject_name": g.subject.name,
            "score": g.score,
            "grad_type": g.grade_type
        })

    #3. Завантажуємо дані в DataFrame
    df = pd.DataFrame(data)

    #4. Робимо Аналітику:

    #4.1. Середній бал по группам
    avg_by_group = df.groupby("group_code")["score"].mean().round(2).to_dict()

    #4.2. Середній бал по предметам
    avg_by_subject =df.groupby("subject_name")["score"].mean().round(2).to_dict()

    #4.3. Загальна кількість виставлених оцінок
    total_grades =len(df)

    #5. Повертаємо результат
    return {
        "total_grades_count": total_grades,
        "avarege_score_by_group": avg_by_group,
        "average_score_by_subject": avg_by_subject
    }

@app.get("/api/analytics/risk-group", tags=["Analytics"])
async def get_risk_group():
    """
    Аналіз студентів, які знаходяться в групі ризику (середній бал нижче 60).
    Використовує Pandas для групування та фільтрації.
    """
    grades_db = Grade.objects()
    
    if not grades_db:
        return {"message": "Немає даних для аналізу"}

    # 1. Розширення даних для Pandas
    data = []
    for g in grades_db:
        data.append({
            "student_id": str(g.student.id),
            "full_name": f"{g.student.first_name} {g.student.last_name}",
            "group_code": g.student.group_code,
            "score": g.score
        })

    df = pd.DataFrame(data)

    # 2. Рахуємо середній бал для КОЖНОГО студента
    # Групуємо за трьома полями, щоб вони залишилися в результаті
    student_stats = df.groupby(["student_id", "full_name", "group_code"])["score"].mean().reset_index()
    
    # Округлюємо до 2 знаків після коми
    student_stats["score"] = student_stats["score"].round(2)
    
    # 3. МАГІЯ PANDAS: Фільтруємо "двієчників" (середній бал < 60)
    risk_df = student_stats[student_stats["score"] < 60]

    # 4. Форматуємо результат для відправки на фронтенд
    risk_list = risk_df.to_dict(orient="records")

    return {
        "risk_count": len(risk_list),
        "threshold": 60,
        "students_at_risk": risk_list
    }

@app.get("/api/analytics/export", tags=["Analytics"])
async def export_analytics_csv():
    """
    Генерує CSV-файл з усіма оцінками для деканату.
    """
    grades_db = Grade.objects()
    
    if not grades_db:
        return {"message": "Немає даних для експорту"}

    # 1. Готуємо красиві дані українською мовою для таблиці
    data = []
    for g in grades_db:
        data.append({
            "Студент": f"{g.student.first_name} {g.student.last_name}",
            "Група": g.student.group_code,
            "Предмет": g.subject.name,
            "Оцінка": g.score,
            "Тип роботи": g.grade_type,
            "Дата виставлення": g.date.strftime("%Y-%m-%d %H:%M")
        })

    # 2. Завантажуємо в Pandas
    df = pd.DataFrame(data)

    # 3. Створюємо віртуальний файл у пам'яті комп'ютера (щоб не засмічувати жорсткий диск)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding='utf-8-sig', sep=';') # utf-8-sig потрібен, щоб Excel нормально читав українські літери

    # 4. Віддаємо файл як відповідь (щоб браузер почав завантаження)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=student_analytics_report.csv"
    
    return response