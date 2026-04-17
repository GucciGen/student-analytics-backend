from faker import Faker
import random
from mongoengine import connect
from models import Student, Subject, Grade
from auth import get_password_hash, generate_student_email, generate_random_password

# Підключаємось до бази
connect(host="mongodb+srv://sviaticrrocer_db_user:KhhdFOGFIq98QMIx@cluster0.ncqipo7.mongodb.net/student_analytics?retryWrites=true&w=majority")

# Налаштовуємо Faker на українську мову
fake = Faker('uk_UA')

def seed_database():
    print("Очищуємо стару базу (це може зайняти пару секунд)...")
    Student.objects().delete()
    Subject.objects().delete()
    Grade.objects().delete()

    print("Створюємо предмети...")
    subject_names = ["Вища математика", "Програмування на Python", "Бази даних", "Веб-дизайн", "Мережеві технології", "Архітектура комп'ютерів", "Кібербезпека"]
    subjects = []
    for name in subject_names:
        sub = Subject(name=name, teacher_name=fake.name())
        sub.save()
        subjects.append(sub)

    print("Формуємо групи та зараховуємо студентів...")
    departments = ["ТІР", "ПД", "КНД", "КІД"]
    
    groups = []
    for dep in departments:
        for i in range(1, 5):
            groups.append(f"{dep}-4{i}")

    students = []
    total_students_count = 0
    
    for group_name in groups:
        students_in_this_group = random.randint(20, 30)
        total_students_count += students_in_this_group
        
        # Створюємо кожного студента індивідуально
        for _ in range(students_in_this_group):
            email = generate_student_email()
            
            # Генеруємо унікальний пароль та одразу його хешуємо
            raw_password = generate_random_password()
            hashed_pwd = get_password_hash(raw_password)
            
            student = Student(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                group_code=group_name,
                enrollment_year=2024,
                email=email,
                hashed_password=hashed_pwd,
                role="student"
            )
            student.save()
            students.append(student)
            
    print(f"Успішно створено {total_students_count} студентів у {len(groups)} групах!")

    print("Виставляємо випадкові оцінки (це найдовший етап, зачекай трішки)...")
    grade_types = ['exam', 'homework', 'lab']
    total_grades_count = 0
    
    for student in students:
        for _ in range(random.randint(3, 8)):
            Grade(
                student=student,
                subject=random.choice(subjects),
                score=round(random.uniform(40.0, 100.0), 2),
                grade_type=random.choice(grade_types)
            ).save()
            total_grades_count += 1

    print(f"Базу повністю наповнено! Згенеровано {total_grades_count} оцінок.")

if __name__ == "__main__":
    seed_database()