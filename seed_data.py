"""
seed_data.py — Демо-дані для початкового заповнення системи UniCore.
Містить 3 кафедри, 5 груп, 20 студентів, 8 викладачів, 10 курсів та ~40 оцінок.
"""

from storage import DataStore
from models import Department, Group, Teacher, Student, Course, Grade, Enrollment


def seed(db: DataStore) -> None:
    """
    Заповнює базу даних демо-даними якщо вона порожня.
    Аргументи:
        db: Екземпляр DataStore для заповнення.
    """
    if db.students or db.teachers or db.courses:
        return  # Дані вже є — не перезаписуємо

    print("[SEED] Завантаження демо-даних...")

    # Кафедри
    depts = [
        Department(1, "Кафедра інформатики", None, "1", "+380441234567", "cs@ukma.edu.ua"),
        Department(2, "Кафедра математики", None, "2", "+380441234568", "math@ukma.edu.ua"),
        Department(3, "Кафедра фізики", None, "3", "+380441234569", "phys@ukma.edu.ua"),
    ]
    for d in depts:
        db.departments[d.dept_id] = d

    # Групи
    groups = [
        Group(1, "ПЛ1АМ", 1, 1, "Програмна інженерія"),
        Group(2, "ПЛ2АМ", 1, 2, "Програмна інженерія"),
        Group(3, "МА1АМ", 2, 1, "Математика"),
        Group(4, "МА2АМ", 2, 2, "Математика"),
        Group(5, "ФЗ1АМ", 3, 1, "Фізика"),
    ]
    for g in groups:
        db.groups[g.group_id] = g

    # Викладачі
    teachers = [
        Teacher(1, "Іван", "Петренко", "i.petrenko@ukma.edu.ua", 1, "доцент", "2015-09-01", 480),
        Teacher(2, "Олена", "Сидоренко", "o.sydorenko@ukma.edu.ua", 1, "професор", "2010-09-01", 720),
        Teacher(3, "Микола", "Коваль", "m.koval@ukma.edu.ua", 2, "доцент", "2018-09-01", 560),
        Teacher(4, "Тетяна", "Бойко", "t.boyko@ukma.edu.ua", 2, "старший викладач", "2020-09-01", 320),
        Teacher(5, "Андрій", "Мороз", "a.moroz@ukma.edu.ua", 3, "доцент", "2016-09-01", 840),
        Teacher(6, "Ірина", "Лисенко", "i.lysenko@ukma.edu.ua", 1, "асистент", "2022-09-01", 200),
        Teacher(7, "Василь", "Ткаченко", "v.tkachenko@ukma.edu.ua", 2, "професор", "2008-09-01", 680),
        Teacher(8, "Юлія", "Гриценко", "yu.hrytsenko@ukma.edu.ua", 3, "доцент", "2019-09-01", 400),
    ]
    for t in teachers:
        db.teachers[t.teacher_id] = t

    # Встановлюємо завідувачів кафедр
    db.departments[1].head_teacher_id = 2
    db.departments[2].head_teacher_id = 7
    db.departments[3].head_teacher_id = 5

    # Студенти
    students = [
        Student(1,  "Олена",    "Коваленко", "2003-05-14", "o.kovalenko@ukma.edu.ua", "+380671111111", 1, "budget",   2021, 0.0),
        Student(2,  "Андрій",   "Бойко",     "2003-03-22", "a.boyko@ukma.edu.ua",     "+380672222222", 1, "budget",   2021, 0.0),
        Student(3,  "Юлія",     "Ткаченко",  "2002-11-05", "yu.tkachenko@ukma.edu.ua","+380673333333", 1, "budget",   2021, 0.0),
        Student(4,  "Дмитро",   "Мороз",     "2003-07-18", "d.moroz@ukma.edu.ua",     "+380674444444", 1, "budget",   2021, 0.0),
        Student(5,  "Катерина", "Лисенко",   "2003-09-30", "k.lysenko@ukma.edu.ua",   "+380675555555", 1, "contract", 2021, 0.0),
        Student(6,  "Сергій",   "Іваненко",  "2004-01-12", "s.ivanenko@ukma.edu.ua",  "+380676666666", 2, "budget",   2022, 0.0),
        Student(7,  "Марія",    "Павленко",  "2004-04-25", "m.pavlenko@ukma.edu.ua",  "+380677777777", 2, "budget",   2022, 0.0),
        Student(8,  "Олексій",  "Савченко",  "2004-08-03", "o.savchenko@ukma.edu.ua", "+380678888888", 2, "contract", 2022, 0.0),
        Student(9,  "Наталія",  "Гриценко",  "2003-12-17", "n.hrytsenko@ukma.edu.ua", "+380679999999", 3, "budget",   2021, 0.0),
        Student(10, "Роман",    "Шевченко",  "2004-02-28", "r.shevchenko@ukma.edu.ua","+380670101010", 3, "budget",   2022, 0.0),
        Student(11, "Ірина",    "Кравченко", "2003-06-09", "i.kravchenko@ukma.edu.ua","+380670202020", 3, "contract", 2021, 0.0),
        Student(12, "Петро",    "Яценко",    "2004-10-21", "p.yatsenko@ukma.edu.ua",  "+380670303030", 4, "budget",   2022, 0.0),
        Student(13, "Оксана",   "Мельник",   "2003-08-15", "o.melnyk@ukma.edu.ua",    "+380670404040", 4, "budget",   2021, 0.0),
        Student(14, "Тарас",    "Гончар",    "2004-03-07", "t.honchar@ukma.edu.ua",   "+380670505050", 4, "contract", 2022, 0.0),
        Student(15, "Валентина","Руденко",   "2003-01-19", "v.rudenko@ukma.edu.ua",   "+380670606060", 5, "budget",   2021, 0.0),
        Student(16, "Микола",   "Черненко",  "2004-05-11", "m.chernenko@ukma.edu.ua", "+380670707070", 5, "budget",   2022, 0.0),
        Student(17, "Аліна",    "Пономаренко","2003-09-23","a.ponomarenko@ukma.edu.ua","+380670808080",5, "contract", 2021, 0.0),
        Student(18, "Богдан",   "Литвиненко","2004-07-16", "b.lytvynenko@ukma.edu.ua","+380670909090", 1, "budget",   2021, 0.0),
        Student(19, "Дарина",   "Назаренко", "2003-11-28", "d.nazarenko@ukma.edu.ua", "+380670010010", 2, "budget",   2022, 0.0),
        Student(20, "Євген",    "Марченко",  "2004-04-04", "ye.marchenko@ukma.edu.ua","+380670020020", 3, "contract", 2022, 0.0),
    ]
    for s in students:
        db.students[s.student_id] = s

    # Курси
    courses = [
        Course(1,  "Алгоритми та структури даних", 1, 1, 4, 30, 1, 2025, False, 0),
        Course(2,  "Бази даних",                   1, 2, 4, 25, 2, 2025, False, 0),
        Course(3,  "Вища математика",               2, 3, 5, 40, 1, 2025, False, 0),
        Course(4,  "Лінійна алгебра",               2, 7, 4, 35, 2, 2025, False, 0),
        Course(5,  "Загальна фізика",               3, 5, 4, 30, 1, 2025, False, 0),
        Course(6,  "Веб-розробка",                  1, 6, 3, 20, 2, 2025, True,  0),
        Course(7,  "Машинне навчання",               1, 2, 3, 15, 2, 2025, True,  0),
        Course(8,  "Теорія ймовірностей",           2, 4, 3, 30, 1, 2025, False, 0),
        Course(9,  "Квантова фізика",               3, 8, 3, 20, 2, 2025, True,  0),
        Course(10, "Об'єктно-орієнтоване програмування", 1, 1, 4, 30, 1, 2025, False, 0),
    ]
    for c in courses:
        db.courses[c.course_id] = c

    # Записи на курси
    # Студенти 1-5 (група 1) записані на курси 1, 2, 10
    enroll_id = 1
    enroll_data = [
        (1,1),(2,1),(3,1),(4,1),(5,1),   # група 1 → курс 1
        (1,2),(2,2),(3,2),(4,2),(5,2),   # група 1 → курс 2
        (1,10),(2,10),(3,10),             # частина групи 1 → курс 10
        (6,3),(7,3),(8,3),               # група 2 → курс 3
        (9,4),(10,4),(11,4),             # група 3 → курс 4
        (12,8),(13,8),(14,8),            # група 4 → курс 8
        (15,5),(16,5),(17,5),            # група 5 → курс 5
        (1,6),(6,6),(9,6),              # вибірковий курс 6
        (2,7),(10,7),                   # вибірковий курс 7
    ]
    for sid, cid in enroll_data:
        enroll = Enrollment(enroll_id, sid, cid, "2025-09-01", "active")
        db.enrollments[enroll_id] = enroll
        db.courses[cid].enrolled_count += 1
        enroll_id += 1

    # Оцінки
    grade_id = 1
    grade_data = [
        # (student_id, course_id, score, date, type, teacher_id)
        (1, 1, 92.5, "2025-12-20", "exam", 1),
        (2, 1, 90.1, "2025-12-20", "exam", 1),
        (3, 1, 87.4, "2025-12-20", "exam", 1),
        (4, 1, 84.0, "2025-12-20", "exam", 1),
        (5, 1, 55.0, "2025-12-20", "exam", 1),  # борг!

        (1, 2, 95.0, "2025-12-22", "exam", 2),
        (2, 2, 88.0, "2025-12-22", "exam", 2),
        (3, 2, 91.0, "2025-12-22", "exam", 2),
        (4, 2, 76.0, "2025-12-22", "exam", 2),
        (5, 2, 45.0, "2025-12-22", "exam", 2),  # борг!

        (1, 10, 89.0, "2025-12-18", "exam", 1),
        (2, 10, 93.0, "2025-12-18", "exam", 1),
        (3, 10, 85.5, "2025-12-18", "exam", 1),

        (6, 3, 78.0, "2025-12-21", "exam", 3),
        (7, 3, 91.5, "2025-12-21", "exam", 3),
        (8, 3, 63.0, "2025-12-21", "exam", 3),

        (9,  4, 88.0, "2025-12-19", "exam", 7),
        (10, 4, 72.0, "2025-12-19", "exam", 7),
        (11, 4, 56.0, "2025-12-19", "exam", 7),  # борг!

        (12, 8, 94.0, "2025-12-23", "exam", 4),
        (13, 8, 82.0, "2025-12-23", "exam", 4),
        (14, 8, 70.0, "2025-12-23", "exam", 4),

        (15, 5, 88.5, "2025-12-17", "exam", 5),
        (16, 5, 75.0, "2025-12-17", "exam", 5),
        (17, 5, 91.0, "2025-12-17", "exam", 5),

        (1,  6, 96.0, "2025-12-24", "coursework", 6),
        (6,  6, 81.0, "2025-12-24", "coursework", 6),
        (9,  6, 74.0, "2025-12-24", "coursework", 6),

        (2,  7, 89.0, "2025-12-25", "coursework", 2),
        (10, 7, 83.0, "2025-12-25", "coursework", 2),

        # Додаткові оцінки для різноманіття
        (18, 1, 66.0, "2025-12-20", "exam", 1),
        (19, 3, 77.0, "2025-12-21", "exam", 3),
        (20, 4, 59.0, "2025-12-19", "exam", 7),  # борг!
    ]
    for sid, cid, score, date, gtype, tid in grade_data:
        g = Grade(grade_id, sid, cid, score, date, gtype, tid)
        db.grades[grade_id] = g
        grade_id += 1

    # Перераховуємо GPA для всіх студентів
    for sid in db.students:
        db.recalculate_gpa(sid)

    # Записуємо в файл
    db.save()
    print(f"[SEED] Завантажено: {len(db.departments)} кафедри, "
          f"{len(db.groups)} груп, {len(db.teachers)} викладачів, "
          f"{len(db.students)} студентів, {len(db.courses)} курсів, "
          f"{len(db.grades)} оцінок.")
