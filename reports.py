"""
reports.py — Модуль звітів та аналітики системи UniCore.
Реалізує аналітичні вибірки: рейтинги, боржники, статистика курсів,
навантаження кафедр, успішність груп.
"""

from typing import Optional
from storage import DataStore
from models import Student



#  Допоміжні функції виведення


def _header(title: str) -> None:
    """Виводить заголовок звіту."""
    line = "=" * 60
    print(f"{line}")
    print(f"  {title}")
    print(line)


def _separator() -> None:
    """Виводить роздільник між рядками таблиці."""
    print("-" * 60)



#  Звіт 1: Рейтинговий список для стипендії


def report_scholarship_ranking(db: DataStore, group_id: int) -> None:
    """
    Формує рейтинговий список для стипендії у групі.
    Алгоритм:
        1. Відбираємо лише бюджетних студентів групи.
        2. Розраховуємо середній бал кожного (GPA).
        3. Сортуємо за спаданням GPA.
        4. Відбираємо топ-40% — вони отримують стипендію.
        5. Відмічаємо боржників (є оцінка < 60).
    Аргументи:
        db: Сховище даних.
        group_id: ID групи для формування звіту.
    """
    group = db.groups.get(group_id)
    if not group:
        print(f"[ПОМИЛКА] Група з ID={group_id} не знайдена.")
        return

    # Відбір бюджетних студентів групи
    budget_students = [
        s for s in db.students.values()
        if s.group_id == group_id and s.status == "budget"
    ]

    if not budget_students:
        print(f"[INFO] У групі '{group.name}' немає бюджетних студентів.")
        return

    # Визначення боржників (оцінка < 60)
    def has_debt(student_id: int) -> bool:
        return any(
            g.score < 60
            for g in db.grades.values()
            if g.student_id == student_id
        )

    # Сортування за спаданням GPA
    ranked = sorted(budget_students, key=lambda s: s.gpa, reverse=True)

    # Топ-40% отримують стипендію
    scholarship_count = max(1, round(len(ranked) * 0.4))
    budget_count = len(ranked)

    _header(f"Рейтинговий список для стипендії — група {group.name}")
    print(f"{'Місце':<6} {'ПІБ':<22} {'GPA':<7} {'Стипендія':<10} {'Примітка'}")
    _separator()

    for place, student in enumerate(ranked, 1):
        debt = has_debt(student.student_id)
        gets_scholarship = (place <= scholarship_count) and not debt
        scholarship_mark = "ТАК" if gets_scholarship else "НІ"
        note = "[БОРГ] ←" if debt else ""

        print(f"{place:<6} {student.full_name():<22} {student.gpa:<7.1f} "
              f"{scholarship_mark:<10} {note}")

    _separator()
    print(f"Бюджетних місць: {budget_count} | Стипендіантів визначено: {scholarship_count}")



#  Звіт 2: Список боржників групи


def report_debtors(db: DataStore, group_id: int, semester: Optional[int] = None) -> None:
    """
    Формує список студентів групи з академічною заборгованістю.
    Заборгованість — оцінка < 60 балів.
    Аргументи:
        db: Сховище даних.
        group_id: ID групи.
        semester: Фільтр за семестром (None = всі семестри).
    """
    group = db.groups.get(group_id)
    if not group:
        print(f"[ПОМИЛКА] Група з ID={group_id} не знайдена.")
        return

    group_students = {s.student_id for s in db.students.values() if s.group_id == group_id}

    # Збираємо всі борги
    debts = []
    for grade in db.grades.values():
        if grade.student_id not in group_students or grade.score >= 60:
            continue
        course = db.courses.get(grade.course_id)
        if semester and course and course.semester != semester:
            continue
        student = db.students.get(grade.student_id)
        if student and course:
            debts.append((student, course, grade))

    sem_label = f", семестр {semester}" if semester else ""
    _header(f"Список боржників — група {group.name}{sem_label}")

    if not debts:
        print("  Боржників не знайдено.")
        return

    print(f"{'ПІБ':<22} {'Курс':<30} {'Оцінка':<8} {'Тип'}")
    _separator()
    for student, course, grade in sorted(debts, key=lambda x: x[0].last_name):
        print(f"{student.full_name():<22} {course.title:<30} "
              f"{grade.score:<8.1f} {grade.grade_type}")

    _separator()
    print(f"Всього боргів: {len(debts)}")



#  Звіт 3: Навантаження кафедри


def report_department_workload(db: DataStore, dept_id: int) -> None:
    """
    Виводить навантаження всіх викладачів кафедри.
    Попереджає, якщо навантаження перевищує 800 год/семестр.
    Аргументи:
        db: Сховище даних.
        dept_id: ID кафедри.
    """
    dept = db.departments.get(dept_id)
    if not dept:
        print(f"[ПОМИЛКА] Кафедра з ID={dept_id} не знайдена.")
        return

    teachers = [t for t in db.teachers.values() if t.department_id == dept_id]

    _header(f"Навантаження кафедри: {dept.name}")

    if not teachers:
        print("  На кафедрі немає викладачів.")
        return

    print(f"{'ПІБ':<25} {'Звання':<20} {'Години':<8} {'Статус'}")
    _separator()

    total_hours = 0
    for t in sorted(teachers, key=lambda x: x.workload_hours, reverse=True):
        warn = "ПЕРЕВАНТАЖЕННЯ" if t.is_overloaded() else "OK"
        print(f"{t.full_name():<25} {t.academic_title:<20} "
              f"{t.workload_hours:<8} {warn}")
        total_hours += t.workload_hours

    _separator()
    avg = total_hours / len(teachers) if teachers else 0
    print(f"Середнє навантаження: {avg:.0f} год | Сумарно: {total_hours} год")



#  Звіт 4: Статистика курсу


def report_course_stats(db: DataStore, course_id: int) -> None:
    """
    Виводить детальну статистику курсу: кількість студентів,
    середній бал, мін/макс оцінки, розподіл за літерами ЄКТС.
    Аргументи:
        db: Сховище даних.
        course_id: ID курсу.
    """
    course = db.courses.get(course_id)
    if not course:
        print(f"[ПОМИЛКА] Курс з ID={course_id} не знайдений.")
        return

    grades = [g for g in db.grades.values() if g.course_id == course_id]
    teacher = db.teachers.get(course.teacher_id) if course.teacher_id else None

    _header(f"Статистика курсу: {course.title}")
    print(f"  Викладач: {teacher.full_name() if teacher else 'не призначено'}")
    print(f"  Семестр: {course.semester} | Рік: {course.year} | Кредити: {course.credits}")
    print(f"  Записано: {course.enrolled_count}/{course.max_students}")

    if not grades:
        print("  Оцінок ще немає.")
        return

    scores = [g.score for g in grades]
    avg = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    passed = sum(1 for s in scores if s >= 60)

    _separator()
    print(f"  Середній бал: {avg:.1f}")
    print(f"  Мінімальний: {min_score:.1f} | Максимальний: {max_score:.1f}")
    print(f"  Склали: {passed}/{len(grades)} ({passed/len(grades)*100:.0f}%)")

    # Розподіл за літерами ЄКТС
    distribution: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for g in grades:
        distribution[g.ects_letter()] += 1

    _separator()
    print("  Розподіл оцінок (ЄКТС):")
    for letter, count in distribution.items():
        bar = "" * count
        print(f"    {letter}: {bar} ({count})")



#  Звіт 5: Успішність групи


def report_group_performance(db: DataStore, group_id: int) -> None:
    """
    Зведений звіт про успішність групи:
    середній GPA, відсоток відмінників, відсоток боржників, топ-3 студенти.
    Аргументи:
        db: Сховище даних.
        group_id: ID групи.
    """
    group = db.groups.get(group_id)
    if not group:
        print(f"[ПОМИЛКА] Група з ID={group_id} не знайдена.")
        return

    students = [s for s in db.students.values() if s.group_id == group_id]

    if not students:
        print("  У групі немає студентів.")
        return

    gpas = [s.gpa for s in students if s.gpa > 0]
    avg_gpa = sum(gpas) / len(gpas) if gpas else 0

    # Відмінники: GPA >= 90
    excellent = [s for s in students if s.gpa >= 90]

    # Боржники: є хоча б одна оцінка < 60
    def has_debt(sid: int) -> bool:
        return any(g.score < 60 for g in db.grades.values() if g.student_id == sid)

    debtors = [s for s in students if has_debt(s.student_id)]

    top3 = sorted(students, key=lambda s: s.gpa, reverse=True)[:3]

    n = len(students)
    _header(f"Успішність групи: {group.name}")
    print(f"  Студентів у групі: {n}")
    print(f"  Середній GPA групи: {avg_gpa:.1f}")
    print(f"  Відмінників (GPA≥90): {len(excellent)} ({len(excellent)/n*100:.0f}%)")
    print(f"  Боржників:           {len(debtors)} ({len(debtors)/n*100:.0f}%)")

    _separator()
    print("  Топ-3 студенти:")
    for i, s in enumerate(top3, 1):
        print(f"    {i}. {s.full_name()} — GPA: {s.gpa:.1f}")



#  Звіт 6: Відмінники потоку


def report_excellent_students(db: DataStore) -> None:
    """
    Виводить список усіх студентів із GPA >= 90, відсортованих за спаданням.
    """
    excellent = sorted(
        [s for s in db.students.values() if s.gpa >= 90],
        key=lambda s: s.gpa,
        reverse=True
    )

    _header("Відмінники потоку (GPA ≥ 90)")

    if not excellent:
        print("  Відмінників не знайдено.")
        return

    print(f"{'ПІБ':<22} {'GPA':<8} {'Група':<6} {'Статус'}")
    _separator()
    for s in excellent:
        group = db.groups.get(s.group_id)
        group_name = group.name if group else "?"
        print(f"{s.full_name():<22} {s.gpa:<8.1f} {group_name:<6} {s.status}")

    print(f"Всього відмінників: {len(excellent)}")
