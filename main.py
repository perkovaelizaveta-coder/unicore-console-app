"""
main.py — Точка входу системи UniCore.
Запускає головне меню та керує життєвим циклом програми.
цей файл виконує роль точки входу (entry point) —
він ініціалізує всі компоненти та запускає життєвий цикл програми.
"""

"""1. Імпорт модулів та архітектурні зв'язки
На самому початку файл імпортує необхідні складові:"""

from storage import DataStore

from seed_data import seed

import menu

BANNER = """
╔══════════════════════════════════════════════╗
║                                              ║
║                   UniCore                    ║
║    University Core Management System         ║
║                                              ║
║    Перькова Єлизавета, Ляховська Дарина      ║
║    Група 2 | НаУКМА                          ║
║                                              ║
╚══════════════════════════════════════════════╝
"""


# 2. Функція main_menu(db: DataStore) — Диспетчер системи
# Це головний цикл управління. Вона приймає об'єкт db (екземпляр DataStore), який є спільним для всієї програми.
def main_menu(db: DataStore) -> None:
    """Головне меню системи UniCore.
    Реалізує ієрархічну навігацію між підменю.
    Аргументи:
        db: Ініціалізований екземпляр сховища даних.
 """
    # Нескінченний цикл while True: Програма не завершується після однієї дії.
    # Вона постійно повертає вас до головного вибору, доки ви явно не оберете вихід.
    while True:
        print("" + "=" * 50)
        print("  UniCore v1.0 — Головне меню")
        print("=" * 50)
        print("  1.  Управління студентами")
        print("  2.  Управління викладачами")
        print("  3.  Управління курсами")
        print("  4.  Управління кафедрами та групами")
        print("  5.  Звіти та аналітика")
        print("  6.  Пошук та фільтрація")
        print("-" * 50)
        print("  0.  Зберегти дані та вийти")
        print("=" * 50)

        choice = input("> Оберіть пункт меню: ").strip()

        if choice == "1":
            menu.menu_students(db)
        elif choice == "2":
            menu.menu_teachers(db)
        elif choice == "3":
            menu.menu_courses(db)
        elif choice == "4":
            menu.menu_departments_groups(db)
        elif choice == "5":
            menu.menu_reports(db)
        elif choice == "6":
            menu.menu_search(db)


        elif choice == "0":
            db.save()
            print("[OK] Дані збережено у unicore_data.json")
            print("До побачення!")
            break
        else:
            print("[!] Невірний вибір. Введіть число від 0 до 6.")


# 3. Блок if __name__ == "__main__": — Точка запуску

if __name__ == "__main__":
    print(BANNER)
    db = DataStore()

    seed(db)  # Завантажуємо демо-дані якщо база порожня

    main_menu(db)
