from mongoengine import connect
from models import Student
from auth import get_password_hash

# Підключаємося до твоєї хмарної бази
connect(host="mongodb+srv://sviaticrrocer_db_user:KhhdFOGFIq98QMIx@cluster0.ncqipo7.mongodb.net/student_analytics?retryWrites=true&w=majority")

def create_super_admin():
    email = "admin@gmail.com"
    password = "admin"
    
    print("Шукаємо адміністратора в базі...")
    # Шукаємо, чи існує вже такий email
    admin_user = Student.objects(email=email).first()
    
    if admin_user:
        # Якщо хтось випадково змінив йому пароль або роль – ми це жорстко виправляємо
        admin_user.update(
            set__hashed_password=get_password_hash(password),
            set__role="admin"
        )
        print(f"✅ Адміністратор {email} вже існував. Права та пароль успішно відновлено!")
    else:
        # Якщо його видалили – створюємо заново
        Student(
            first_name="Головний",
            last_name="Адміністратор",
            group_code="Адміністрація", 
            enrollment_year=2024,
            email=email,
            hashed_password=get_password_hash(password),
            role="admin"
        ).save()
        print(f"✅ Супер-адміністратор {email} успішно створений з нуля!")

if __name__ == "__main__":
    create_super_admin()