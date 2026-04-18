from mongoengine import connect
from models import User
from auth import get_password_hash

connect(host="mongodb+srv://sviaticrrocer_db_user:KhhdFOGFIq98QMIx@cluster0.ncqipo7.mongodb.net/student_analytics?retryWrites=true&w=majority")

def create_super_admin():
    email = "admin@gmail.com"
    password = "admin"
    
    print("Шукаємо адміністратора в базі (в таблиці User)...")
    admin_user = User.objects(email=email).first()
    
    if admin_user:
        admin_user.update(
            set__hashed_password=get_password_hash(password),
            set__role="admin"
        )
        print(f"Адміністратор {email} вже існував. Права та пароль успішно відновлено!")
    else:
        User(
            email=email,
            hashed_password=get_password_hash(password),
            role="admin"
        ).save()
        print(f"Супер-адміністратор {email} успішно створений у таблиці User!")

if __name__ == "__main__":
    create_super_admin()