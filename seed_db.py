import random  # Повертаємо random для кількості
from faker import Faker
from mongoengine import connect
from models import Student, Subject
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

    print("Створюємо предмети...")
    subject_names = [
        "Вища математика",
        "Програмування на Python",
        "Бази даних",
        "Веб-дизайн",
        "Мережеві технології",
    ]
    for name in subject_names:
        Subject(name=name, teacher_name=fake.name()).save()

    print("Формуємо групи...")
    departments = ["ТІР", "ПД", "КНД", "КІД"]
    groups = [f"{dep}-4{i}" for dep in departments for i in range(1, 5)]

    total_students = random.randint(150, 200)
    print(f"Зараховуємо {total_students} студентів...")

    for i in range(total_students):
        email = generate_student_email()
        raw_password = generate_random_password()
        hashed_pwd = get_password_hash(raw_password)

        Student(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            group_code=groups[i % len(groups)],
            enrollment_year=2024,
            email=email,
            hashed_password=hashed_pwd,
            role="student",
        ).save()

    print(f"Базу наповнено: створено {total_students} студентів без оцінок.")


if __name__ == "__main__":
    seed_database()
