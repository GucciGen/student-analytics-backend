import random
from faker import Faker
from mongoengine import connect
from models import Student, Subject, Grade  # <-- Додали Grade
from auth import get_password_hash, generate_student_email, generate_random_password

# Підключаємось до бази
connect(
    host="mongodb+srv://sviaticrrocer_db_user:KhhdFOGFIq98QMIx@cluster0.ncqipo7.mongodb.net/student_analytics?retryWrites=true&w=majority"
)

# Налаштовуємо Faker
fake = Faker("uk_UA")


def seed_database():
    print("Очищуємо стару базу...")
    Student.objects().delete()
    Subject.objects().delete()
    Grade.objects().delete() 

    print("Створюємо предмети...")
    subject_names = [
        "Вища математика",
        "Програмування на Python",
        "Бази даних",
        "Веб-дизайн",
        "Мережеві технології",
    ]
    
    # Зберігаємо створені предмети у список, щоб потім давати з них оцінки
    subjects = []
    for name in subject_names:
        subj = Subject(name=name, teacher_name=fake.name()).save()
        subjects.append(subj)

    print("Формуємо групи...")
    departments = ["ТІР", "ПД", "КНД", "КІД"]
    groups = [f"{dep}-4{i}" for dep in departments for i in range(1, 5)]

    total_students = random.randint(150, 200)
    print(f"Зараховуємо {total_students} студентів...")

    # Зберігаємо створених студентів у список
    students = []
    for i in range(total_students):
        email = generate_student_email()
        raw_password = generate_random_password()
        hashed_pwd = get_password_hash(raw_password)

        student = Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            group_code=groups[i % len(groups)],
            enrollment_year=2024,
            email=email,
            hashed_password=hashed_pwd,
            role="student",
            absences=random.randint(0, 50)
        ).save()
        students.append(student)

    print("Генеруємо випадкові оцінки (Журнал)...")
    grade_types = ['exam', 'homework', 'lab']
    total_grades = 0

    # Проходимося по кожному студенту і ставимо йому випадкові оцінки
    for student in students:
        num_grades = random.randint(5, 15) 
        for _ in range(num_grades):
            Grade(
                student=student,
                subject=random.choice(subjects), # Випадковий предмет
                score=round(random.uniform(40.0, 100.0), 1),
                grade_type=random.choice(grade_types)
            ).save()
            total_grades += 1

    print(f"Базу наповнено: {total_students} студентів та {total_grades} оцінок!")


if __name__ == "__main__":
    seed_database()