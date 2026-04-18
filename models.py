from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ReferenceField, CASCADE
import datetime

# Колекція Студентів
class Student(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    group_code = StringField(required=True)
    enrollment_year = IntField(default=2024)
    email = StringField(unique=True) 
    hashed_password = StringField()
    role = StringField(default="student")
    absences = IntField(default=0)

# Колекція Предметів
class Subject(Document):
    name = StringField(required=True, unique=True)
    teacher_name = StringField()

# Колекція Оцінок (Журнал)
class Grade(Document):
    student = ReferenceField(Student, reverse_delete_rule=CASCADE, required=True)
    subject = ReferenceField(Subject, reverse_delete_rule=CASCADE, required=True)
    score = FloatField(required=True)
    grade_type = StringField(choices=('exam', 'homework', 'lab'), required=True)
    date = DateTimeField(default=datetime.datetime.now)

# Колекція Користувачів (Викладачі/Адміни)
class User(Document):
    email = StringField(required=True, unique=True)
    hashed_password = StringField(required=True)
    role = StringField(choices=('admin', 'teacher'), default='teacher')