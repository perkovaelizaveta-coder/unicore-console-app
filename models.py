"""
models.py — Модуль моделей даних системи UniCore.
Містить класи-сутності для управління університетськими даними.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re


#  Базовий клас


class BaseEntity:
    """Базовий клас для всіх сутностей системи."""

    def to_dict(self) -> dict:
        """Серіалізує об'єкт у словник для збереження в JSON."""
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict):
        """Десеріалізує об'єкт із словника JSON."""
        return cls(**data)


#  Department (Кафедра)


@dataclass
class Department(BaseEntity):
    """
    Модель кафедри університету.
    Атрибути:
        dept_id: Унікальний ідентифікатор кафедри.
        name: Назва кафедри.
        head_teacher_id: ID завідувача (зовнішній ключ → Teacher).
        building: Корпус університету.
        phone: Телефон кафедри.
        email: Email кафедри.
    """
    dept_id: int
    name: str
    head_teacher_id: Optional[int] = None
    building: str = ""
    phone: str = ""
    email: str = ""

    def __str__(self) -> str:
        return f"[{self.dept_id}] {self.name} (корп. {self.building})"


#  Group (Навчальна група)


@dataclass
class Group(BaseEntity):
    """
    Модель навчальної групи.
    Атрибути:
        group_id: Унікальний ідентифікатор групи.
        name: Назва групи (наприклад 'ПЛ1АМ').
        department_id: ID кафедри (зовнішній ключ → Department).
        year_of_study: Курс навчання (1–4).
        specialty: Спеціальність.
    """
    group_id: int
    name: str
    department_id: int
    year_of_study: int
    specialty: str = ""

    def __str__(self) -> str:
        return f"[{self.group_id}] {self.name} ({self.year_of_study} курс, {self.specialty})"


#  Student (Студент)


@dataclass
class Student(BaseEntity):
    """
    Модель студента університету.
    Атрибути:
        student_id: Унікальний ідентифікатор студента.
        first_name: Ім'я.
        last_name: Прізвище.
        birth_date: Дата народження (РРРР-ММ-ДД).
        email: Електронна пошта (унікальна).
        phone: Номер телефону.
        group_id: ID групи (зовнішній ключ → Group).
        status: Статус навчання: 'budget' або 'contract'.
        enrollment_year: Рік вступу.
        gpa: Середній бал (0.0–100.0, обчислюється автоматично).
    """
    student_id: int
    first_name: str
    last_name: str
    birth_date: str
    email: str
    phone: str
    group_id: int
    status: str
    enrollment_year: int
    gpa: float = 0.0

    def full_name(self) -> str:
        """Повертає повне ім'я студента."""
        return f"{self.last_name} {self.first_name}"

    def __str__(self) -> str:
        return (f"[{self.student_id}] {self.full_name()} | "
                f"Група: {self.group_id} | Статус: {self.status} | GPA: {self.gpa:.1f}")

    @staticmethod
    def validate_email(email: str) -> bool:
        """Перевіряє формат електронної пошти."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_status(status: str) -> bool:
        """Перевіряє допустимість статусу студента."""
        return status in ('budget', 'contract')


#  Teacher (Викладач)


@dataclass
class Teacher(BaseEntity):
    """
    Модель викладача університету.
    Атрибути:
        teacher_id: Унікальний ідентифікатор викладача.
        first_name: Ім'я.
        last_name: Прізвище.
        email: Електронна пошта.
        department_id: ID кафедри (зовнішній ключ → Department).
        academic_title: Вчене звання.
        hire_date: Дата прийому на роботу.
        workload_hours: Поточне навантаження (год/семестр).
    """
    teacher_id: int
    first_name: str
    last_name: str
    email: str
    department_id: int
    academic_title: str = ""
    hire_date: str = ""
    workload_hours: int = 0

    MAX_WORKLOAD: int = field(default=800, init=False, repr=False)

    def full_name(self) -> str:
        """Повертає повне ім'я викладача."""
        return f"{self.last_name} {self.first_name}"

    def is_overloaded(self) -> bool:
        """Перевіряє, чи перевищує викладач норму навантаження."""
        return self.workload_hours > 800

    def __str__(self) -> str:
        warn = " ПЕРЕВАНТАЖЕННЯ" if self.is_overloaded() else ""
        return (f"[{self.teacher_id}] {self.full_name()} | "
                f"{self.academic_title} | Навантаження: {self.workload_hours} год{warn}")


#  Course (Курс)


@dataclass
class Course(BaseEntity):
    """
    Модель навчального курсу.
    Атрибути:
        course_id: Унікальний ідентифікатор курсу.
        title: Назва курсу.
        department_id: ID кафедри-власника.
        teacher_id: ID викладача (може бути None).
        credits: Кількість кредитів ЄКТС.
        max_students: Максимальна кількість студентів.
        semester: Семестр (1 або 2).
        year: Навчальний рік.
        is_elective: Чи є курс вибірковим.
        enrolled_count: Поточна кількість записаних студентів.
    """
    course_id: int
    title: str
    department_id: int
    teacher_id: Optional[int]
    credits: int
    max_students: int
    semester: int
    year: int
    is_elective: bool = False
    enrolled_count: int = 0

    def has_free_spots(self) -> bool:
        """Перевіряє наявність вільних місць на курсі."""
        return self.enrolled_count < self.max_students

    def free_spots(self) -> int:
        """Повертає кількість вільних місць."""
        return self.max_students - self.enrolled_count

    def __str__(self) -> str:
        elective = " [вибірк.]" if self.is_elective else ""
        return (f"[{self.course_id}] {self.title}{elective} | "
                f"Сем. {self.semester} | Кредити: {self.credits} | "
                f"Місця: {self.enrolled_count}/{self.max_students}")


#  Grade (Оцінка)


@dataclass
class Grade(BaseEntity):
    """
    Модель оцінки студента за курс.
    Атрибути:
        grade_id: Унікальний ідентифікатор оцінки.
        student_id: ID студента.
        course_id: ID курсу.
        score: Оцінка (0.0–100.0 за шкалою ЄКТС).
        grade_date: Дата виставлення.
        grade_type: Тип: 'exam', 'coursework', 'test'.
        teacher_id: ID викладача, що виставив оцінку.
    """
    grade_id: int
    student_id: int
    course_id: int
    score: float
    grade_date: str
    grade_type: str
    teacher_id: int

    VALID_TYPES: tuple = field(default=('exam', 'coursework', 'test'), init=False, repr=False)

    def ects_letter(self) -> str:
        """Конвертує числову оцінку в літеру ЄКТС."""
        if self.score >= 90:
            return "A"
        elif self.score >= 82:
            return "B"
        elif self.score >= 74:
            return "C"
        elif self.score >= 64:
            return "D"
        elif self.score >= 60:
            return "E"
        else:
            return "F"

    def is_passed(self) -> bool:
        """Перевіряє, чи є оцінка зарахованою"""
        return self.score >= 60.0

    def __str__(self) -> str:
        status = "✓" if self.is_passed() else "✗ БОРГ"
        return (f"[{self.grade_id}] Студент {self.student_id} | "
                f"Курс {self.course_id} | {self.score:.1f} ({self.ects_letter()}) | "
                f"{self.grade_type} | {status}")


#  Enrollment (Запис на курс)


@dataclass
class Enrollment(BaseEntity):
    """
    Модель запису студента на курс.
    Атрибути:
        enroll_id: Унікальний ідентифікатор запису.
        student_id: ID студента.
        course_id: ID курсу.
        enrolled_date: Дата реєстрації.
        status: Статус запису: 'active' або 'dropped'.
    """
    enroll_id: int
    student_id: int
    course_id: int
    enrolled_date: str
    status: str = "active"  # 'active' | 'dropped'

    def __str__(self) -> str:
        return (f"[{self.enroll_id}] Студент {self.student_id} → "
                f"Курс {self.course_id} | {self.enrolled_date} | {self.status}")
