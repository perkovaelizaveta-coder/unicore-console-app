"""Модуль menu.py — це рівень інтерфейсу користувача (User Interface layer)
вашої системи. Якщо models.py — це дані, а storage.py — це пам'ять,
то menu.py — це спосіб взаємодії з цими даними."""

from datetime import date

from typing import Optional

import re

from storage import DataStore

from models import Student, Teacher, Course, Department, Group, Grade, Enrollment

import reports


#  Допоміжні функції вводу


def _input_int(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """
    Зчитує ціле число з валідацією діапазону.
    Аргументи:
        prompt: Текст підказки.
        min_val: Мінімальне допустиме значення.
        max_val: Максимальне допустиме значення.
    Повертає:
        Введене ціле число.
    """
    while True:

        try:

            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"[!] Значення має бути не менше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"[!] Значення має бути не більше {max_val}.")
                continue
            return val
        except ValueError:
            print("[!] Введіть ціле число.")


def _input_float(prompt: str, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Зчитує дійсне число з валідацією діапазону.
    Аргументи:
        prompt: Текст підказки.
        min_val: Мінімальне допустиме значення.
        max_val: Максимальне допустиме значення.
    Повертає:
        Введене дійсне число.
    """
    while True:
        try:
            val = float(input(prompt))
            if not (min_val <= val <= max_val):
                print(f"[!] Значення має бути від {min_val} до {max_val}.")
                continue
            return val
        except ValueError:
            print("[!] Введіть число (наприклад: 85.5).")


def _input_email(prompt: str) -> str:
    """
    Зчитує email з перевіркою формату.
    Аргументи:
        prompt: Текст підказки.
    Повертає:
        Валідна email-адреса.
    """
    while True:
        email = input(prompt).strip()
        if Student.validate_email(email):
            return email
        print("[!] Некоректний формат email. Приклад: name@ukma.edu.ua")


def _input_date(prompt: str) -> str:
    """
    Зчитує дату у форматі РРРР-ММ-ДД.
    Аргументи:
        prompt: Текст підказки.
    Повертає:
        Рядок дати у форматі РРРР-ММ-ДД.
    """
    while True:
        d = input(prompt).strip()
        try:
            date.fromisoformat(d)
            return d
        except ValueError:
            print("[!] Формат дати: РРРР-ММ-ДД (наприклад: 2003-05-14).")


def _pause() -> None:
    """Зупиняє виконання до натискання Enter."""
    input("[Enter] — продовжити...")


def _clear_header(title: str) -> None:
    """Виводить заголовок підменю."""
    print(f"{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)


#  1. Управління студентами


def menu_students(db: DataStore) -> None:
    """Підменю управління студентами."""
    while True:
        _clear_header("1. Управління студентами")
        print("  1.1  Додати нового студента")
        print("  1.2  Переглянути профіль студента")
        print("  1.3  Знайти студента за прізвищем")
        print("  1.4  Оновити дані студента")
        print("  1.5  Відрахувати студента")
        print("  1.6  Список студентів групи")
        print("  0    Назад")

        choice = input("> Оберіть дію: ").strip()

        if choice == "1":
            _add_student(db)
        elif choice == "2":
            _view_student(db)
        elif choice == "3":
            _search_student_by_name(db)
        elif choice == "4":
            _update_student(db)
        elif choice == "5":
            _delete_student(db)
        elif choice == "6":
            _list_group_students(db)
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


def _add_student(db: DataStore) -> None:
    """Додає нового студента до системи."""
    print("--- Додавання нового студента ---")
    try:
        first_name = input("Ім'я: ").strip()
        last_name = input("Прізвище: ").strip()
        if not first_name or not last_name:
            print("[ПОМИЛКА] Ім'я та прізвище не можуть бути порожніми.")
            return

        birth_date = _input_date("Дата народження (РРРР-ММ-ДД): ")
        email = _input_email("Email: ")

        # Перевірка унікальності email
        if any(s.email == email for s in db.students.values()):
            print(f"[ПОМИЛКА] Студент з email '{email}' вже існує.")
            return

        phone = input("Телефон: ").strip()

        # Перевірка існування групи
        print("Доступні групи:")
        for g in db.groups.values():
            print(f"  {g}")
        group_id = _input_int("ID групи: ", min_val=1)
        if group_id not in db.groups:
            print(f"[ПОМИЛКА] Групу з ID={group_id} не знайдено.")
            return

        status = ""
        while status not in ("budget", "contract"):
            status = input("Статус (budget/contract): ").strip().lower()
            if status not in ("budget", "contract"):
                print("[!] Введіть 'budget' або 'contract'.")

        enrollment_year = _input_int("Рік вступу: ", min_val=2000, max_val=2100)

        sid = db.next_id(db.students)
        student = Student(sid, first_name, last_name, birth_date, email,
                          phone, group_id, status, enrollment_year, 0.0)
        db.students[sid] = student
        db.save()
        print(f"[OK] Студента успішно додано. ID: {sid}")
        print("[OK] Дані збережено у unicore_data.json")

    except KeyboardInterrupt:
        print("[Скасовано]")


def _view_student(db: DataStore) -> None:
    """Виводить профіль студента за ID."""
    sid = _input_int("ID студента: ", min_val=1)
    student = db.students.get(sid)
    if not student:
        print(f"[ПОМИЛКА] Студента з ID={sid} не знайдено.")
        return

    group = db.groups.get(student.group_id)
    grades = [g for g in db.grades.values() if g.student_id == sid]

    print(f"{'─' * 40}")
    print(f"  Профіль студента #{sid}")
    print(f"{'─' * 40}")
    print(f"  ПІБ:        {student.full_name()}")
    print(f"  Дата нар.:  {student.birth_date}")
    print(f"  Email:      {student.email}")
    print(f"  Телефон:    {student.phone}")
    print(f"  Група:      {group.name if group else '?'}")
    print(f"  Статус:     {student.status}")
    print(f"  Рік вступу: {student.enrollment_year}")
    print(f"  GPA:        {student.gpa:.1f}")

    if grades:
        print(f"  Оцінки ({len(grades)}):")
        for g in grades:
            course = db.courses.get(g.course_id)
            c_name = course.title if course else f"Курс #{g.course_id}"
            status = "✓" if g.is_passed() else "✗ БОРГ"
            print(f"    - {c_name}: {g.score:.1f} ({g.ects_letter()}) {status}")
    _pause()


def _search_student_by_name(db: DataStore) -> None:
    """Шукає студентів за частиною прізвища."""
    query = input("Введіть прізвище (або частину): ").strip().lower()
    results = [s for s in db.students.values()
               if query in s.last_name.lower()]

    if not results:
        print("[INFO] Студентів не знайдено.")
        return

    print(f"Знайдено {len(results)} студент(ів):")
    for s in results:
        group = db.groups.get(s.group_id)
        print(f"  {s} | Група: {group.name if group else '?'}")
    _pause()


def _update_student(db: DataStore) -> None:
    """Оновлює дані студента (статус, групу або email)."""
    sid = _input_int("ID студента: ", min_val=1)
    student = db.students.get(sid)
    if not student:
        print(f"[ПОМИЛКА] Студента з ID={sid} не знайдено.")
        return

    print(f"Редагування: {student.full_name()}")
    print("  1 — Змінити статус")
    print("  2 — Змінити групу")
    print("  3 — Змінити email")
    print("  4 — Змінити телефон")

    field = input("> Що змінити: ").strip()

    if field == "1":
        new_status = ""
        while new_status not in ("budget", "contract"):
            new_status = input("Новий статус (budget/contract): ").strip().lower()
        student.status = new_status
    elif field == "2":
        new_gid = _input_int("Новий ID групи: ", min_val=1)
        if new_gid not in db.groups:
            print(f"[ПОМИЛКА] Групу з ID={new_gid} не знайдено.")
            return
        student.group_id = new_gid
    elif field == "3":
        new_email = _input_email("Новий email: ")
        if any(s.email == new_email and s.student_id != sid for s in db.students.values()):
            print("[ПОМИЛКА] Цей email вже використовується.")
            return
        student.email = new_email
    elif field == "4":
        student.phone = input("Новий телефон: ").strip()
    else:
        print("[!] Невірний вибір.")
        return

    db.save()
    print(f"[OK] Дані студента #{sid} оновлено.")


def _delete_student(db: DataStore) -> None:
    """Відраховує студента (видаляє з системи)."""
    sid = _input_int("ID студента для відрахування: ", min_val=1)
    student = db.students.get(sid)
    if not student:
        print(f"[ПОМИЛКА] Студента з ID={sid} не знайдено.")
        return

    confirm = input(f"Відрахувати '{student.full_name()}'? (так/ні): ").strip().lower()
    if confirm != "так":
        print("[Скасовано]")
        return

    del db.students[sid]
    # Видаляємо пов'язані оцінки та записи
    db.grades = {k: v for k, v in db.grades.items() if v.student_id != sid}
    db.enrollments = {k: v for k, v in db.enrollments.items() if v.student_id != sid}
    db.save()
    print(f"[OK] Студента #{sid} відраховано.")


def _list_group_students(db: DataStore) -> None:
    """Виводить список студентів групи."""
    print("Доступні групи:")
    for g in db.groups.values():
        print(f"  {g}")
    gid = _input_int("ID групи: ", min_val=1)
    group = db.groups.get(gid)
    if not group:
        print(f"[ПОМИЛКА] Групу з ID={gid} не знайдено.")
        return

    students = [s for s in db.students.values() if s.group_id == gid]
    print(f"Студенти групи {group.name} ({len(students)} осіб):")
    print(f"{'ПІБ':<22} {'GPA':<7} {'Статус'}")
    print("-" * 40)
    for s in sorted(students, key=lambda x: x.gpa, reverse=True):
        print(f"{s.full_name():<22} {s.gpa:<7.1f} {s.status}")
    _pause()


#  2. Управління викладачами


def menu_teachers(db: DataStore) -> None:
    """Підменю управління викладачами."""
    while True:
        _clear_header("2. Управління викладачами")
        print("  2.1  Додати нового викладача")
        print("  2.2  Переглянути профіль викладача")
        print("  2.3  Оновити дані викладача")
        print("  2.4  Переглянути навантаження")
        print("  2.5  Звільнити викладача")
        print("  0    Назад")

        choice = input("> Оберіть дію: ").strip()

        if choice == "1":
            _add_teacher(db)
        elif choice == "2":
            _view_teacher(db)
        elif choice == "3":
            _update_teacher(db)
        elif choice == "4":
            _view_teacher_workload(db)
        elif choice == "5":
            _delete_teacher(db)
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


def _add_teacher(db: DataStore) -> None:
    """Додає нового викладача на кафедру."""
    print("--- Додавання нового викладача ---")
    try:
        first_name = input("Ім'я: ").strip()
        last_name = input("Прізвище: ").strip()
        email = _input_email("Email: ")

        if any(t.email == email for t in db.teachers.values()):
            print(f"[ПОМИЛКА] Викладач з email '{email}' вже існує.")
            return

        print("Доступні кафедри:")
        for d in db.departments.values():
            print(f"  {d}")
        dept_id = _input_int("ID кафедри: ", min_val=1)
        if dept_id not in db.departments:
            print(f"[ПОМИЛКА] Кафедру з ID={dept_id} не знайдено.")
            return

        academic_title = input("Вчене звання (доцент/професор/асистент/тощо): ").strip()
        hire_date = _input_date("Дата прийому (РРРР-ММ-ДД): ")
        workload = _input_int("Поточне навантаження (год): ", min_val=0)

        if workload > 800:
            print(f"[ПОПЕРЕДЖЕННЯ] Навантаження {workload} год перевищує норму (800 год).")

        tid = db.next_id(db.teachers)
        teacher = Teacher(tid, first_name, last_name, email, dept_id,
                          academic_title, hire_date, workload)
        db.teachers[tid] = teacher
        db.save()
        print(f"[OK] Викладача успішно додано. ID: {tid}")

    except KeyboardInterrupt:
        print("[Скасовано]")


def _view_teacher(db: DataStore) -> None:
    """Виводить профіль викладача."""
    tid = _input_int("ID викладача: ", min_val=1)
    teacher = db.teachers.get(tid)
    if not teacher:
        print(f"[ПОМИЛКА] Викладача з ID={tid} не знайдено.")
        return

    dept = db.departments.get(teacher.department_id)
    courses = [c for c in db.courses.values() if c.teacher_id == tid]

    print(f"{'─' * 40}")
    print(f"  Профіль викладача #{tid}")
    print(f"{'─' * 40}")
    print(f"  ПІБ:       {teacher.full_name()}")
    print(f"  Email:     {teacher.email}")
    print(f"  Кафедра:   {dept.name if dept else '?'}")
    print(f"  Звання:    {teacher.academic_title}")
    print(f"  Прийнятий: {teacher.hire_date}")
    print(f"  Навантаження: {teacher.workload_hours} год"
          f"{' ПЕРЕВАНТАЖЕННЯ' if teacher.is_overloaded() else ''}")

    if courses:
        print(f"  Курси ({len(courses)}):")
        for c in courses:
            print(f"    - {c.title} (сем. {c.semester}, {c.enrolled_count}/{c.max_students})")
    _pause()


def _update_teacher(db: DataStore) -> None:
    """Оновлює кафедру або звання викладача."""
    tid = _input_int("ID викладача: ", min_val=1)
    teacher = db.teachers.get(tid)
    if not teacher:
        print(f"[ПОМИЛКА] Викладача з ID={tid} не знайдено.")
        return

    print(f"Редагування: {teacher.full_name()}")
    print("  1 — Змінити кафедру")
    print("  2 — Змінити вчене звання")
    print("  3 — Оновити навантаження")

    field = input("> Що змінити: ").strip()

    if field == "1":
        print("Доступні кафедри:")
        for d in db.departments.values():
            print(f"  {d}")
        new_dept = _input_int("Новий ID кафедри: ", min_val=1)
        if new_dept not in db.departments:
            print("[ПОМИЛКА] Кафедру не знайдено.")
            return
        teacher.department_id = new_dept
    elif field == "2":
        teacher.academic_title = input("Нове звання: ").strip()
    elif field == "3":
        new_load = _input_int("Нове навантаження (год): ", min_val=0)
        if new_load > 800:
            print(f"[ПОПЕРЕДЖЕННЯ] Навантаження {new_load} год > норми 800 год!")
        teacher.workload_hours = new_load
    else:
        print("[!] Невірний вибір.")
        return

    db.save()
    print(f"[OK] Дані викладача #{tid} оновлено.")


def _view_teacher_workload(db: DataStore) -> None:
    """Виводить навантаження конкретного викладача."""
    tid = _input_int("ID викладача: ", min_val=1)
    teacher = db.teachers.get(tid)
    if not teacher:
        print(f"[ПОМИЛКА] Викладача з ID={tid} не знайдено.")
        return

    courses = [c for c in db.courses.values() if c.teacher_id == tid]
    total_credits = sum(c.credits for c in courses)

    print(f"  {teacher.full_name()} — навантаження: {teacher.workload_hours} год")
    print(f"  Ведуть курсів: {len(courses)} (разом {total_credits} кредитів)")
    if teacher.is_overloaded():
        print(f"  ПЕРЕВАНТАЖЕННЯ! Перевищення норми: {teacher.workload_hours - 800} год")
    _pause()


def _delete_teacher(db: DataStore) -> None:
    """Звільняє викладача із системи."""
    tid = _input_int("ID викладача для звільнення: ", min_val=1)
    teacher = db.teachers.get(tid)
    if not teacher:
        print(f"[ПОМИЛКА] Викладача з ID={tid} не знайдено.")
        return

    # Перевіряємо, чи немає активних курсів
    active_courses = [c for c in db.courses.values() if c.teacher_id == tid]
    if active_courses:
        print(f"[ПОПЕРЕДЖЕННЯ] Викладач веде {len(active_courses)} курс(ів). "
              f"Спочатку переведіть курси іншому викладачу.")
        for c in active_courses:
            print(f"  - {c.title}")
        return

    confirm = input(f"Звільнити '{teacher.full_name()}'? (так/ні): ").strip().lower()
    if confirm != "так":
        print("[Скасовано]")
        return

    del db.teachers[tid]
    db.save()
    print(f"[OK] Викладача #{tid} звільнено.")


#  3. Управління курсами


def menu_courses(db: DataStore) -> None:
    """Підменю управління курсами."""
    while True:
        _clear_header("3. Управління курсами")
        print("  3.1  Додати новий курс")
        print("  3.2  Переглянути деталі курсу")
        print("  3.3  Записати студента на курс")
        print("  3.4  Виставити оцінку студенту")
        print("  3.5  Список студентів курсу (з оцінками)")
        print("  3.6  Редагувати курс")
        print("  3.7  Видалити курс")
        print("  0    Назад")

        choice = input("> Оберіть дію: ").strip()

        if choice == "1":
            _add_course(db)
        elif choice == "2":
            _view_course(db)
        elif choice == "3":
            _enroll_student(db)
        elif choice == "4":
            _add_grade(db)
        elif choice == "5":
            _list_course_students(db)
        elif choice == "6":
            _update_course(db)
        elif choice == "7":
            _delete_course(db)
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


def _add_course(db: DataStore) -> None:
    """Створює новий навчальний курс."""
    print("--- Додавання нового курсу ---")
    try:
        title = input("Назва курсу: ").strip()
        if not title:
            print("[ПОМИЛКА] Назва не може бути порожньою.")
            return

        print("Доступні кафедри:")
        for d in db.departments.values():
            print(f"  {d}")
        dept_id = _input_int("ID кафедри: ", min_val=1)
        if dept_id not in db.departments:
            print("[ПОМИЛКА] Кафедру не знайдено.")
            return

        print("Доступні викладачі:")
        for t in db.teachers.values():
            print(f"  {t}")
        teacher_input = input("ID викладача (Enter — пропустити): ").strip()
        teacher_id = int(teacher_input) if teacher_input else None
        if teacher_id and teacher_id not in db.teachers:
            print("[ПОМИЛКА] Викладача не знайдено.")
            return

        credits = _input_int("Кількість кредитів ЄКТС: ", min_val=1, max_val=10)
        max_students = _input_int("Максимальна кількість студентів: ", min_val=1)
        semester = _input_int("Семестр (1 або 2): ", min_val=1, max_val=2)
        year = _input_int("Навчальний рік: ", min_val=2020, max_val=2100)
        is_elective_input = input("Вибірковий курс? (так/ні): ").strip().lower()
        is_elective = is_elective_input == "так"

        cid = db.next_id(db.courses)
        course = Course(cid, title, dept_id, teacher_id, credits,
                        max_students, semester, year, is_elective, 0)
        db.courses[cid] = course
        db.save()
        print(f"[OK] Курс успішно створено. ID: {cid}")

    except KeyboardInterrupt:
        print("[Скасовано]")


def _view_course(db: DataStore) -> None:
    """Виводить деталі курсу."""
    cid = _input_int("ID курсу: ", min_val=1)
    course = db.courses.get(cid)
    if not course:
        print(f"[ПОМИЛКА] Курс з ID={cid} не знайдено.")
        return

    teacher = db.teachers.get(course.teacher_id) if course.teacher_id else None
    dept = db.departments.get(course.department_id)

    print(f"{'─' * 40}")
    print(f"  Курс #{cid}: {course.title}")
    print(f"{'─' * 40}")
    print(f"  Кафедра:    {dept.name if dept else '?'}")
    print(f"  Викладач:   {teacher.full_name() if teacher else 'не призначено'}")
    print(f"  Кредити:    {course.credits}")
    print(f"  Семестр:    {course.semester} | Рік: {course.year}")
    print(f"  Студентів:  {course.enrolled_count}/{course.max_students}")
    print(f"  Вибірковий: {'Так' if course.is_elective else 'Ні'}")
    _pause()


def _enroll_student(db: DataStore) -> None:
    """
    Реєструє студента на курс з перевіркою:
    - існування курсу та студента;
    - наявності вільних місць;
    - відсутності повторної реєстрації.
    """
    print("--- Реєстрація студента на курс ---")
    sid = _input_int("ID студента: ", min_val=1)
    student = db.students.get(sid)
    if not student:
        print(f"[ПОМИЛКА] Студента з ID={sid} не знайдено.")
        return
    print(f"[CHECK] Студент знайдений: {student.full_name()} .......... OK")

    cid = _input_int("ID курсу: ", min_val=1)
    course = db.courses.get(cid)
    if not course:
        print("[ПОМИЛКА] Курс не знайдено.")
        return
    print(f"[CHECK] Курс знайдений: {course.title} .......... OK")

    # Перевірка повторної реєстрації
    already_enrolled = any(
        e.student_id == sid and e.course_id == cid and e.status == "active"
        for e in db.enrollments.values()
    )
    if already_enrolled:
        print("[ПОМИЛКА] Вже зареєстровано.")
        return
    print("[CHECK] Не записана раніше .......... OK")

    # Перевірка вільних місць
    if not course.has_free_spots():
        print(f"[ПОМИЛКА] Немає вільних місць ({course.enrolled_count}/{course.max_students}).")
        return
    print(f"[CHECK] Вільні місця: {course.enrolled_count}/{course.max_students} .......... OK")

    eid = db.next_id(db.enrollments)
    enrollment = Enrollment(eid, sid, cid, str(date.today()), "active")
    db.enrollments[eid] = enrollment
    course.enrolled_count += 1
    db.save()

    print(f"[OK] {student.full_name()} успішно записано на курс '{course.title}'")
    print(f"[OK] Вільних місць залишилось: {course.free_spots()}/{course.max_students}")


def _add_grade(db: DataStore) -> None:
    """Виставляє або оновлює оцінку студенту за курс."""
    print("--- Виставлення оцінки ---")
    sid = _input_int("ID студента: ", min_val=1)
    if sid not in db.students:
        print("[ПОМИЛКА] Студента не знайдено.")
        return

    cid = _input_int("ID курсу: ", min_val=1)
    if cid not in db.courses:
        print("[ПОМИЛКА] Курс не знайдено.")
        return

    grade_type = ""
    while grade_type not in ("exam", "coursework", "test"):
        grade_type = input("Тип оцінки (exam/coursework/test): ").strip().lower()

    score = _input_float("Оцінка (0.0–100.0): ", 0.0, 100.0)

    # Перевіряємо, чи вже є оцінка такого типу
    existing = next(
        (g for g in db.grades.values()
         if g.student_id == sid and g.course_id == cid and g.grade_type == grade_type),
        None
    )

    if existing:
        print(f"[INFO] Попередня оцінка: {existing.score:.1f}. Виправляємо...")
        existing.score = score
        existing.grade_date = str(date.today())
    else:
        # Визначаємо викладача курсу
        course = db.courses.get(cid)
        teacher_id = course.teacher_id if course and course.teacher_id else 1

        gid = db.next_id(db.grades)
        grade = Grade(gid, sid, cid, score, str(date.today()), grade_type, teacher_id)
        db.grades[gid] = grade

    # Перераховуємо GPA
    db.recalculate_gpa(sid)
    student = db.students.get(sid)
    print(f"[OK] Оцінку виставлено. Новий GPA студента: {student.gpa:.1f}")


def _list_course_students(db: DataStore) -> None:
    """Виводить список студентів курсу з їхніми оцінками."""
    cid = _input_int("ID курсу: ", min_val=1)
    course = db.courses.get(cid)
    if not course:
        print(f"[ПОМИЛКА] Курс з ID={cid} не знайдено.")
        return

    enrollments = [e for e in db.enrollments.values()
                   if e.course_id == cid and e.status == "active"]

    print(f"Студенти курсу '{course.title}' ({len(enrollments)} осіб):")
    print(f"{'ПІБ':<22} {'Оцінка':<8} {'ЄКТС':<5} {'Статус'}")
    print("-" * 45)

    for e in enrollments:
        student = db.students.get(e.student_id)
        if not student:
            continue
        grade = next((g for g in db.grades.values()
                      if g.student_id == e.student_id and g.course_id == cid), None)
        if grade:
            status = "✓" if grade.is_passed() else "✗ БОРГ"
            print(f"{student.full_name():<22} {grade.score:<8.1f} {grade.ects_letter():<5} {status}")
        else:
            print(f"{student.full_name():<22} {'—':<8} {'—':<5} Ще без оцінки")
    _pause()


def _update_course(db: DataStore) -> None:
    """Редагує параметри курсу: назву, ліміт, семестр, викладача."""
    cid = _input_int("ID курсу: ", min_val=1)
    course = db.courses.get(cid)
    if not course:
        print(f"[ПОМИЛКА] Курс з ID={cid} не знайдено.")
        return

    print(f"Редагування: {course.title}")
    print("  1 — Назва")
    print("  2 — Максимум студентів")
    print("  3 — Семестр")
    print("  4 — Викладач")

    field = input("> Що змінити: ").strip()

    if field == "1":
        course.title = input("Нова назва: ").strip()
    elif field == "2":
        course.max_students = _input_int("Новий ліміт: ", min_val=course.enrolled_count)
    elif field == "3":
        course.semester = _input_int("Семестр (1/2): ", min_val=1, max_val=2)
    elif field == "4":
        tid = _input_int("Новий ID викладача: ", min_val=1)
        if tid not in db.teachers:
            print("[ПОМИЛКА] Викладача не знайдено.")
            return
        course.teacher_id = tid
    else:
        print("[!] Невірний вибір.")
        return

    db.save()
    print(f"[OK] Курс #{cid} оновлено.")


def _delete_course(db: DataStore) -> None:
    """Видаляє курс якщо на нього немає записаних студентів."""
    cid = _input_int("ID курсу: ", min_val=1)
    course = db.courses.get(cid)
    if not course:
        print(f"[ПОМИЛКА] Курс з ID={cid} не знайдено.")
        return

    if course.enrolled_count > 0:
        print(f"[ПОМИЛКА] Не можна видалити курс із записаними студентами "
              f"({course.enrolled_count} осіб).")
        return

    confirm = input(f"Видалити '{course.title}'? (так/ні): ").strip().lower()
    if confirm != "так":
        print("[Скасовано]")
        return

    del db.courses[cid]
    db.save()
    print(f"[OK] Курс #{cid} видалено.")


#  4. Управління кафедрами та групами


def menu_departments_groups(db: DataStore) -> None:
    """Підменю управління кафедрами та групами."""
    while True:
        _clear_header("4. Управління кафедрами та групами")
        print("  4.1  Додати нову кафедру")
        print("  4.2  Переглянути кафедру")
        print("  4.3  Змінити завідувача кафедри")
        print("  4.4  Додати нову групу")
        print("  4.5  Переглянути групу (студенти, статистика)")
        print("  0    Назад")

        choice = input("> Оберіть дію: ").strip()

        if choice == "1":
            _add_department(db)
        elif choice == "2":
            _view_department(db)
        elif choice == "3":
            _update_dept_head(db)
        elif choice == "4":
            _add_group(db)
        elif choice == "5":
            _view_group(db)
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


def _add_department(db: DataStore) -> None:
    """Додає нову кафедру."""
    name = input("Назва кафедри: ").strip()
    building = input("Корпус: ").strip()
    phone = input("Телефон: ").strip()
    email = _input_email("Email: ")

    did = db.next_id(db.departments)
    dept = Department(did, name, None, building, phone, email)
    db.departments[did] = dept
    db.save()
    print(f"[OK] Кафедру додано. ID: {did}")


def _view_department(db: DataStore) -> None:
    """Виводить деталі кафедри: викладачів та курси."""
    print("Кафедри:")
    for d in db.departments.values():
        print(f"  {d}")
    did = _input_int("ID кафедри: ", min_val=1)
    dept = db.departments.get(did)
    if not dept:
        print("[ПОМИЛКА] Кафедру не знайдено.")
        return

    head = db.teachers.get(dept.head_teacher_id) if dept.head_teacher_id else None
    teachers = [t for t in db.teachers.values() if t.department_id == did]
    courses = [c for c in db.courses.values() if c.department_id == did]
    groups = [g for g in db.groups.values() if g.department_id == did]

    print(f"{'─' * 40}")
    print(f"  Кафедра: {dept.name}")
    print(f"{'─' * 40}")
    print(f"  Корпус:      {dept.building}")
    print(f"  Тел.:        {dept.phone}")
    print(f"  Email:       {dept.email}")
    print(f"  Завідувач:   {head.full_name() if head else 'не призначено'}")
    print(f"  Викладачів:  {len(teachers)}")
    print(f"  Груп:        {len(groups)}")
    print(f"  Курсів:      {len(courses)}")

    if teachers:
        print("\n  Викладачі:")
        for t in teachers:
            print(f"    - {t}")
    _pause()


def _update_dept_head(db: DataStore) -> None:
    """Змінює завідувача кафедри."""
    did = _input_int("ID кафедри: ", min_val=1)
    dept = db.departments.get(did)
    if not dept:
        print("[ПОМИЛКА] Кафедру не знайдено.")
        return

    print("\nВикладачі кафедри:")
    for t in db.teachers.values():
        if t.department_id == did:
            print(f"  {t}")
    tid = _input_int("ID нового завідувача: ", min_val=1)
    if tid not in db.teachers:
        print("[ПОМИЛКА] Викладача не знайдено.")
        return

    dept.head_teacher_id = tid
    db.save()
    teacher = db.teachers[tid]
    print(f"[OK] Завідувача кафедри '{dept.name}' змінено на {teacher.full_name()}.")


def _add_group(db: DataStore) -> None:
    """Додає нову навчальну групу."""
    name = input("Назва групи (наприклад ПЛ1АМ): ").strip()
    print("\nКафедри:")
    for d in db.departments.values():
        print(f"  {d}")
    dept_id = _input_int("ID кафедри: ", min_val=1)
    if dept_id not in db.departments:
        print("[ПОМИЛКА] Кафедру не знайдено.")
        return
    year_of_study = _input_int("Курс навчання (1-4): ", min_val=1, max_val=4)
    specialty = input("Спеціальність: ").strip()

    gid = db.next_id(db.groups)
    group = Group(gid, name, dept_id, year_of_study, specialty)
    db.groups[gid] = group
    db.save()
    print(f"[OK] Групу '{name}' додано. ID: {gid}")


def _view_group(db: DataStore) -> None:
    """Виводить деталі групи зі статистикою."""
    print("Групи:")
    for g in db.groups.values():
        print(f"  {g}")
    gid = _input_int("ID групи: ", min_val=1)
    group = db.groups.get(gid)
    if not group:
        print("[ПОМИЛКА] Групу не знайдено.")
        return

    students = [s for s in db.students.values() if s.group_id == gid]
    dept = db.departments.get(group.department_id)
    avg_gpa = sum(s.gpa for s in students) / len(students) if students else 0

    print(f"  Група: {group.name} | {group.specialty} | {group.year_of_study} курс")
    print(f"  Кафедра: {dept.name if dept else '?'}")
    print(f"  Студентів: {len(students)} | Середній GPA: {avg_gpa:.1f}")
    _pause()


#  5. Звіти та аналітика


def menu_reports(db: DataStore) -> None:
    """Підменю звітів та аналітики."""
    while True:
        _clear_header("5. Звіти та аналітика")
        print("  5.1  Рейтинговий список для стипендії")
        print("  5.2  Список боржників групи")
        print("  5.3  Навантаження кафедри")
        print("  5.4  Статистика курсу")
        print("  5.5  Успішність групи")
        print("  5.6  Відмінники потоку (GPA ≥ 90)")
        print("  0    Назад")

        choice = input("> Оберіть звіт: ").strip()

        if choice == "1":
            gid = _input_int("ID групи: ", min_val=1)
            reports.report_scholarship_ranking(db, gid)
            _pause()
        elif choice == "2":
            gid = _input_int("ID групи: ", min_val=1)
            sem_input = input("Семестр (Enter — всі): ").strip()
            sem = int(sem_input) if sem_input else None
            reports.report_debtors(db, gid, sem)
            _pause()
        elif choice == "3":
            did = _input_int("ID кафедри: ", min_val=1)
            reports.report_department_workload(db, did)
            _pause()
        elif choice == "4":
            cid = _input_int("ID курсу: ", min_val=1)
            reports.report_course_stats(db, cid)
            _pause()
        elif choice == "5":
            gid = _input_int("ID групи: ", min_val=1)
            reports.report_group_performance(db, gid)
            _pause()
        elif choice == "6":
            reports.report_excellent_students(db)
            _pause()
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


#  6. Пошук та фільтрація


def menu_search(db: DataStore) -> None:
    """Підменю пошуку та фільтрації."""
    while True:
        _clear_header("6. Пошук та фільтрація")
        print("  6.1  Пошук студента (за прізвищем)")
        print("  6.2  Пошук курсу (за назвою / викладачем)")
        print("  6.3  Пошук викладача (за прізвищем / кафедрою)")
        print("  6.4  Фільтр студентів (група + статус + борг)")
        print("  6.5  Курси з вільними місцями")
        print("  0    Назад")

        choice = input("> Оберіть дію: ").strip()

        if choice == "1":
            _search_student_by_name(db)
        elif choice == "2":
            _search_courses(db)
        elif choice == "3":
            _search_teachers(db)
        elif choice == "4":
            _filter_students(db)
        elif choice == "5":
            _courses_with_spots(db)
        elif choice == "0":
            break
        else:
            print("[!] Невірний вибір.")


def _search_courses(db: DataStore) -> None:
    """Шукає курси за назвою або ім'ям викладача."""
    query = input("Введіть назву курсу або прізвище викладача: ").strip().lower()
    results = []
    for c in db.courses.values():
        if query in c.title.lower():
            results.append(c)
            continue
        if c.teacher_id:
            t = db.teachers.get(c.teacher_id)
            if t and query in t.last_name.lower():
                results.append(c)

    if not results:
        print("[INFO] Нічого не знайдено.")
        return

    print(f"Знайдено курсів: {len(results)}")
    for c in results:
        t = db.teachers.get(c.teacher_id) if c.teacher_id else None
        print(f"  {c} | Викладач: {t.full_name() if t else '—'}")
    _pause()


def _search_teachers(db: DataStore) -> None:
    """Шукає викладачів за прізвищем або ID кафедри."""
    print("  1 — За прізвищем")
    print("  2 — За кафедрою")
    mode = input("> ").strip()

    if mode == "1":
        query = input("Прізвище: ").strip().lower()
        results = [t for t in db.teachers.values() if query in t.last_name.lower()]
    elif mode == "2":
        did = _input_int("ID кафедри: ", min_val=1)
        results = [t for t in db.teachers.values() if t.department_id == did]
    else:
        print("[!] Невірний вибір.")
        return

    if not results:
        print("[INFO] Нічого не знайдено.")
        return

    print(f"Знайдено: {len(results)}")
    for t in results:
        dept = db.departments.get(t.department_id)
        print(f"  {t} | Кафедра: {dept.name if dept else '?'}")
    _pause()


def _filter_students(db: DataStore) -> None:
    """Фільтрує студентів за групою, статусом та наявністю боргу."""
    group_input = input("ID групи (Enter — всі): ").strip()
    gid = int(group_input) if group_input else None

    status_input = input("Статус (budget/contract/Enter — всі): ").strip().lower()
    status = status_input if status_input in ("budget", "contract") else None

    debt_input = input("Лише боржники? (так/ні/Enter — всі): ").strip().lower()

    results = list(db.students.values())

    if gid:
        results = [s for s in results if s.group_id == gid]
    if status:
        results = [s for s in results if s.status == status]
    if debt_input == "так":
        results = [s for s in results
                   if any(g.score < 60 for g in db.grades.values()
                          if g.student_id == s.student_id)]

    print(f"\nЗнайдено студентів: {len(results)}")
    for s in sorted(results, key=lambda x: x.gpa, reverse=True):
        print(f"  {s}")
    _pause()


def _courses_with_spots(db: DataStore) -> None:
    """Виводить курси з вільними місцями, відсортовані за кількістю місць."""
    available = sorted(
        [c for c in db.courses.values() if c.has_free_spots()],
        key=lambda c: c.free_spots(),
        reverse=True
    )

    print(f"Курсів з вільними місцями: {len(available)}")
    print(f"{'Назва':<35} {'Вільно':<8} {'Сем.'}")
    print("-" * 50)
    for c in available:
        print(f"{c.title:<35} {c.free_spots():<8} {c.semester}")
    _pause()
