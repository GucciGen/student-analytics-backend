import jwt
import datetime
import random
import string
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from models import User

SECRET_KEY = "diploma_super_secret_key_2026"
ALGORITHM = "HS256"

# 1. ЄДИНИЙ екземпляр шифрувальника на весь проєкт
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])

class UserRegister(BaseModel):
    email: str
    password: str

# --- ФУНКЦІЇ ДОПОМОГИ (Генератори та Хешування) ---

def get_password_hash(password: str):
    """Приймає звичайний пароль і повертає зашифрований хеш"""
    return pwd_context.hash(password)

def generate_random_password(length=8):
    """Генерує випадковий пароль із літер та цифр"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_student_email():
    """Генерує пошту формату st12345678@duikt.edu.ua"""
    random_numbers = ''.join(random.choices(string.digits, k=8))
    return f"st{random_numbers}@duikt.edu.ua"

# --- МАРШРУТИ АВТОРИЗАЦІЇ ---

@auth_router.post("/register")
async def register(user_data: UserRegister):
    if User.objects(email=user_data.email).first():
        raise HTTPException(status_code=400, detail="Цей email вже зареєстровано")
    hashed_pw = get_password_hash(user_data.password) # Використовуємо нашу функцію
    new_user = User(email=user_data.email, hashed_password=hashed_pw)
    new_user.save()
    return {"message": "Користувача успішно створено!"}

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.objects(email=form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Невірний email або пароль")
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    token = jwt.encode({"sub": user.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# --- ПЕРЕВІРКА ПРАВ ---

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Недійсний токен")
    except Exception:
        raise HTTPException(status_code=401, detail="Недійсний або прострочений токен")
        
    user = User.objects(email=email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Доступ заборонено! Тільки для деканату (admin).")
    return current_user