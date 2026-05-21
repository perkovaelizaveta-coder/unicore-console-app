"""
storage.py — Модуль збереження та завантаження даних системи UniCore.
Відповідає за роботу з файлом unicore_data.json: читання, запис,
резервне копіювання та валідацію цілісності даних.
"""

import json
import shutil
import re
from pathlib import Path
from typing import Optional

from models import Student, Teacher, Course, Department, Group, Grade, Enrollment

DATA_FILE = Path("unicore_data.json")
BACKUP_FILE = Path("unicore_data_backup.json")



#  Головне сховище даних


class DataStore:
    """
    Центральне сховище всіх об'єктів системи UniCore.
    Завантажує дані з JSON-файлу при ініціалізації,
    зберігає після кожної зміни.
    Атрибути:
        students: Словник студентів {student_id: Student}.
        teachers: Словник викладачів {teacher_id: Teacher}.
        courses: Словник курсів {course_id: Course}.
        departments: Словник кафедр {dept_id: Department}.
        groups: Словник груп {group_id: Group}.
        grades: Словник оцінок {grade_id: Grade}.
        enrollments: Словник записів на курси {enroll_id: Enrollment}.
    """

    def __init__(self) -> None:
        """Ініціалізує сховище та завантажує дані з файлу."""
        self.students: dict[int, Student] = {}
        self.teachers: dict[int, Teacher] = {}
        self.courses: dict[int, Course] = {}
        self.departments: dict[int, Department] = {}
        self.groups: dict[int, Group] = {}
        self.grades: dict[int, Grade] = {}
        self.enrollments: dict[int, Enrollment] = {}
        self.load()

    # Завантаження

    def load(self) -> None:
        """
        Завантажує дані з unicore_data.json.
        Якщо файл відсутній — починає з порожніми колекціями.
        При завантаженні створює резервну копію попереднього стану.
        """
        if not DATA_FILE.exists():
            print("[INFO] Файл даних не знайдено. Починаємо з порожньої бази.")
            return

        # Резервна копія перед завантаженням
        shutil.copy2(DATA_FILE, BACKUP_FILE)

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw: dict = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ПОМИЛКА] Файл даних пошкоджено: {e}")
            return

        # Десеріалізація кожної колекції
        for d in raw.get("departments", []):
            obj = Department(**d)
            self.departments[obj.dept_id] = obj

        for g in raw.get("groups", []):
            obj = Group(**g)
            self.groups[obj.group_id] = obj

        for t in raw.get("teachers", []):
            # Прибираємо зайві поля dataclass (MAX_WORKLOAD)
            t.pop("MAX_WORKLOAD", None)
            obj = Teacher(**t)
            self.teachers[obj.teacher_id] = obj

        for s in raw.get("students", []):
            obj = Student(**s)
            self.students[obj.student_id] = obj

        for c in raw.get("courses", []):
            obj = Course(**c)
            self.courses[obj.course_id] = obj

        for g in raw.get("grades", []):
            g.pop("VALID_TYPES", None)
            obj = Grade(**g)
            self.grades[obj.grade_id] = obj

        for e in raw.get("enrollments", []):
            obj = Enrollment(**e)
            self.enrollments[obj.enroll_id] = obj

        self._validate_integrity()
        print(f"[OK] Дані завантажено: {len(self.students)} студентів, "
              f"{len(self.courses)} курсів, {len(self.grades)} оцінок.")

    # Збереження
    def save(self) -> None:
        """
        Зберігає всі дані у файл unicore_data.json.
        Викликається автоматично після кожної операції CUD.
        """
        def serialize_list(collection: dict) -> list:
            result = []
            for obj in collection.values():
                d = obj.to_dict()
                # Видаляємо технічні поля dataclass
                d.pop("MAX_WORKLOAD", None)
                d.pop("VALID_TYPES", None)
                result.append(d)
            return result

        data = {
            "departments": serialize_list(self.departments),
            "groups": serialize_list(self.groups),
            "teachers": serialize_list(self.teachers),
            "students": serialize_list(self.students),
            "courses": serialize_list(self.courses),
            "grades": serialize_list(self.grades),
            "enrollments": serialize_list(self.enrollments),
        }

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Валідація цілісності

    def _validate_integrity(self) -> None:
        """
        Перевіряє цілісність зовнішніх ключів після завантаження.
        Виводить попередження для некоректних посилань.
        """
        warnings = []

        for s in self.students.values():
            if s.group_id not in self.groups:
                warnings.append(f"Студент {s.student_id}: group_id={s.group_id} не існує")
            if not Student.validate_email(s.email):
                warnings.append(f"Студент {s.student_id}: некоректний email '{s.email}'")

        for t in self.teachers.values():
            if t.department_id not in self.departments:
                warnings.append(f"Викладач {t.teacher_id}: dept_id={t.department_id} не існує")

        for c in self.courses.values():
            if c.department_id not in self.departments:
                warnings.append(f"Курс {c.course_id}: dept_id={c.department_id} не існує")
            if c.teacher_id and c.teacher_id not in self.teachers:
                warnings.append(f"Курс {c.course_id}: teacher_id={c.teacher_id} не існує")

        for g in self.grades.values():
            if g.student_id not in self.students:
                warnings.append(f"Оцінка {g.grade_id}: student_id={g.student_id} не існує")
            if g.course_id not in self.courses:
                warnings.append(f"Оцінка {g.grade_id}: course_id={g.course_id} не існує")

        if warnings:
            print("[ПОПЕРЕДЖЕННЯ] Виявлено проблеми цілісності даних:")
            for w in warnings:
                print(f"   {w}")
        else:
            print("[OK] Цілісність даних підтверджено.")

    # Генератори ID

    def next_id(self, collection: dict) -> int:
        """Генерує наступний унікальний ID для колекції."""
        return max(collection.keys(), default=0) + 1

    # Перерахунок GPA студента

    def recalculate_gpa(self, student_id: int) -> None:
        """
        Перераховує середній бал (GPA) студента на основі всіх його оцінок.
        Аргументи:
            student_id: ID студента для перерахунку GPA.
        """
        student = self.students.get(student_id)
        if not student:
            return
        scores = [g.score for g in self.grades.values()
                  if g.student_id == student_id]
        student.gpa = round(sum(scores) / len(scores), 2) if scores else 0.0
        self.save()
