import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
from datetime import datetime

# ------ НАСТРОЙКИ БАЗЫ ДАННЫХ ------
DB_NAME = "formula1.db"  # файл базы данных

def init_db():
    """Создаёт таблицы и заполняет начальными данными из SQL-файлов, если БД пуста"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    # Проверяем, есть ли уже таблицы (например, по наличию таблицы Pilots)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Pilots'")
    if cur.fetchone() is None:
        # Выполняем database.sql
        with open("database.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        cur.executescript(sql_script)
        print("Таблицы созданы из database.sql")

        # Выполняем data_sample.sql (начальные данные)
        with open("data_sample.sql", "r", encoding="utf-8") as f:
            data_script = f.read()
        cur.executescript(data_script)
        print("Начальные данные загружены из data_sample.sql")

        conn.commit()
    else:
        print("База данных уже существует, пропускаем инициализацию")
    conn.close()

# ------ ОСНОВНОЕ ПРИЛОЖЕНИЕ ------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Справочники Формулы-1")
        self.root.geometry("1000x600")

        # ФИО, курс, группа, год на русском
        info_frame = ttk.Frame(root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="Ярошик Елизавета Владимировна, 3 курс, 2 группа, 2026 год",
                  font=("Arial", 10)).pack(side=tk.LEFT)

        # Выбор справочника
        select_frame = ttk.Frame(root)
        select_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(select_frame, text="Выберите справочник:").pack(side=tk.LEFT, padx=5)
        self.dict_var = tk.StringVar(value="pilots")
        ttk.Radiobutton(select_frame, text="Пилоты", variable=self.dict_var, value="pilots",
                        command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(select_frame, text="Результаты гонок", variable=self.dict_var, value="races",
                        command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Таблица (Treeview)
        self.tree = ttk.Treeview(root, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # Сортировка при клике на заголовок
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Кнопки действий
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Добавить", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Просмотреть", command=self.view_record).pack(side=tk.LEFT, padx=5)

        self.load_data()

    # ----- ЗАГРУЗКА ДАННЫХ В ТАБЛИЦУ -----
    def load_data(self):
        """Загружает данные выбранного справочника в Treeview"""
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.dict_var.get() == "pilots":
            self.current_dict = "pilots"
            self.tree["columns"] = ("full_name", "birth_date", "car_number", "comment")
            self.tree.heading("full_name", text="ФИО", command=lambda: self.sort_by("full_name"))
            self.tree.heading("birth_date", text="Дата рождения", command=lambda: self.sort_by("birth_date"))
            self.tree.heading("car_number", text="Номер болида", command=lambda: self.sort_by("car_number"))
            self.tree.heading("comment", text="Комментарий", command=lambda: self.sort_by("comment"))
            self.tree.column("full_name", width=200)
            self.tree.column("birth_date", width=120)
            self.tree.column("car_number", width=100)
            self.tree.column("comment", width=400)

            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT pilot_id, full_name, birth_date, car_number, comment FROM Pilots")
            rows = cur.fetchall()
            conn.close()
            # В Treeview не выводим ID, но сохраним его в отдельном словаре
            self.id_map = {}  # {item_id: pilot_id}
            for row in rows:
                item_id = self.tree.insert("", tk.END, values=(row[1], row[2], row[3], row[4]))
                self.id_map[item_id] = row[0]
        else:
            self.current_dict = "races"
            self.tree["columns"] = ("race_name", "race_date", "position", "time_seconds", "pilot_name")
            self.tree.heading("race_name", text="Гонка", command=lambda: self.sort_by("race_name"))
            self.tree.heading("race_date", text="Дата гонки", command=lambda: self.sort_by("race_date"))
            self.tree.heading("position", text="Позиция", command=lambda: self.sort_by("position"))
            self.tree.heading("time_seconds", text="Время (сек)", command=lambda: self.sort_by("time_seconds"))
            self.tree.heading("pilot_name", text="Пилот", command=lambda: self.sort_by("pilot_name"))
            for col in self.tree["columns"]:
                self.tree.column(col, width=150)

            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            # JOIN для отображения имени пилота
            cur.execute('''
                SELECT r.result_id, r.race_name, r.race_date, r.position, r.time_seconds, p.full_name
                FROM RaceResults r
                JOIN Pilots p ON r.pilot_id = p.pilot_id
            ''')
            rows = cur.fetchall()
            conn.close()
            self.id_map = {}
            for row in rows:
                item_id = self.tree.insert("", tk.END, values=(row[1], row[2], row[3], row[4], row[5]))
                self.id_map[item_id] = row[0]

    # ----- СОРТИРОВКА (честная: числа как числа, даты как даты) -----
    def sort_by(self, col):
        """Сортирует данные по колонке col (учитываем тип)"""
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            # Определяем тип колонки
            if col in ("car_number", "position", "time_seconds"):
                # числовые
                try:
                    key = float(values[self.tree["columns"].index(col)]) if values[self.tree["columns"].index(col)] else 0
                except:
                    key = 0
            elif col == "birth_date" or col == "race_date":
                # дата: строка в формате ГГГГ-ММ-ДД, сравним как строки (ISO)
                key = values[self.tree["columns"].index(col)] or ""
            else:
                # текст
                key = values[self.tree["columns"].index(col)] or ""
            data.append((key, item))
        data.sort(key=lambda x: x[0])
        # Переставить строки в Treeview
        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)

    def on_tree_click(self, event):
        """Обработчик клика по заголовку для сортировки"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)  # #1, #2...
            col_index = int(col[1:]) - 1
            col_name = self.tree["columns"][col_index]
            self.sort_by(col_name)

    # ----- ДОБАВЛЕНИЕ ЗАПИСИ -----
    def add_record(self):
        self.open_form("add")

    # ----- РЕДАКТИРОВАНИЕ -----
    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        self.open_form("edit", selected[0])

    # ----- ПРОСМОТР -----
    def view_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для просмотра")
            return
        self.open_form("view", selected[0])

    # ----- УДАЛЕНИЕ -----
    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить эту запись?"):
            record_id = self.id_map[selected[0]]
            if self.current_dict == "pilots":
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM RaceResults WHERE pilot_id=?", (record_id,))
                count = cur.fetchone()[0]
                conn.close()
                if count > 0:
                    messagebox.showerror("Ошибка", "У пилота есть результаты гонок. Удалите их сначала.")
                    return
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            try:
                if self.current_dict == "pilots":
                    cur.execute("DELETE FROM Pilots WHERE pilot_id=?", (record_id,))
                else:
                    cur.execute("DELETE FROM RaceResults WHERE result_id=?", (record_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Запись удалена")
                self.load_data()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Ошибка", "Нельзя удалить пилота, потому что есть результаты гонок.\nСначала удалите связанные результаты.")
            finally:
                conn.close()

    # ----- УНИВЕРСАЛЬНАЯ ФОРМА ВВОДА/РЕДАКТИРОВАНИЯ/ПРОСМОТРА -----
    def open_form(self, mode, item_id=None):
        """mode: 'add', 'edit', 'view'"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование" if mode == "edit" else ("Просмотр" if mode == "view" else "Добавление"))
        dialog.geometry("500x500")

        if self.current_dict == "pilots":
            # --- Поля для Пилота (создаём без state, потом заблокируем) ---
            ttk.Label(dialog, text="ФИО:").pack(pady=5)
            full_name_entry = ttk.Entry(dialog, width=50)
            full_name_entry.pack()

            ttk.Label(dialog, text="Дата рождения:").pack(pady=5)
            birth_date_entry = DateEntry(dialog, width=12, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            birth_date_entry.pack()

            ttk.Label(dialog, text="Номер болида (1-99):").pack(pady=5)
            car_number_entry = ttk.Entry(dialog, width=10)
            car_number_entry.pack()

            ttk.Label(dialog, text="Комментарий (многострочный):").pack(pady=5)
            comment_text = scrolledtext.ScrolledText(dialog, height=5, width=50)
            comment_text.pack()

            # Если редактирование или просмотр, загрузить текущие значения
            if mode in ("edit", "view"):
                record_id = self.id_map[item_id]
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT full_name, birth_date, car_number, comment FROM Pilots WHERE pilot_id=?", (record_id,))
                row = cur.fetchone()
                conn.close()
                if row:
                    full_name_entry.insert(0, row[0])
                    birth_date_entry.set_date(row[1])
                    car_number_entry.insert(0, str(row[2]) if row[2] is not None else "")
                    comment_text.insert("1.0", row[3] or "")
                    if mode == "view":
                        full_name_entry.config(state="readonly")
                        car_number_entry.config(state="readonly")
                        comment_text.config(state="disabled")
                        birth_date_entry.config(state="disabled")

            def save():
                if mode == "view":
                    dialog.destroy()
                    return
                full_name = full_name_entry.get().strip()
                birth_date = birth_date_entry.get()
                car_number = car_number_entry.get().strip()
                comment = comment_text.get("1.0", tk.END).strip()

                if not full_name:
                    messagebox.showerror("Ошибка", "ФИО обязательно")
                    return
                try:
                    car_num = int(car_number) if car_number else None
                    if car_num is not None and (car_num < 1 or car_num > 99):
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Ошибка", "Номер болида должен быть целым числом от 1 до 99")
                    return

                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                try:
                    if mode == "add":
                        cur.execute("INSERT INTO Pilots (full_name, birth_date, car_number, comment) VALUES (?,?,?,?)",
                                    (full_name, birth_date, car_num, comment))
                    else:  # edit
                        cur.execute("UPDATE Pilots SET full_name=?, birth_date=?, car_number=?, comment=? WHERE pilot_id=?",
                                    (full_name, birth_date, car_num, comment, record_id))
                    conn.commit()
                    messagebox.showinfo("Успех", "Сохранено")
                    self.load_data()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка БД", str(e))
                finally:
                    conn.close()

            if mode != "view":
                ttk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
            else:
                ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)

        else:  # races (Результаты гонок)
            # --- Поля для результата ---
            ttk.Label(dialog, text="Выберите пилота (выпадающий список с ID):").pack(pady=5)
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT pilot_id, full_name FROM Pilots")
            pilots = cur.fetchall()
            conn.close()
            pilot_ids = [p[0] for p in pilots]
            pilot_names = [p[1] for p in pilots]

            combo = ttk.Combobox(dialog, values=pilot_names, state="readonly" if mode == "view" else "readonly")
            combo.pack()
            selected_pilot_id = tk.IntVar()
            def on_combo_select(event):
                idx = combo.current()
                if idx >= 0:
                    selected_pilot_id.set(pilot_ids[idx])
            combo.bind("<<ComboboxSelected>>", on_combo_select)

            ttk.Label(dialog, text="Название гонки:").pack(pady=5)
            race_name_entry = ttk.Entry(dialog, width=50)
            race_name_entry.pack()

            ttk.Label(dialog, text="Дата гонки:").pack(pady=5)
            race_date_entry = DateEntry(dialog, width=12, date_pattern='yyyy-mm-dd')
            race_date_entry.pack()

            ttk.Label(dialog, text="Финишная позиция (целое число >0):").pack(pady=5)
            position_entry = ttk.Entry(dialog, width=10)
            position_entry.pack()

            ttk.Label(dialog, text="Время (сек, число с точкой):").pack(pady=5)
            time_entry = ttk.Entry(dialog, width=15)
            time_entry.pack()

            if mode in ("edit", "view"):
                record_id = self.id_map[item_id]
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("SELECT pilot_id, race_name, race_date, position, time_seconds FROM RaceResults WHERE result_id=?", (record_id,))
                row = cur.fetchone()
                conn.close()
                if row:
                    try:
                        idx = pilot_ids.index(row[0])
                        combo.current(idx)
                        selected_pilot_id.set(row[0])
                    except ValueError:
                        pass
                    race_name_entry.insert(0, row[1])
                    race_date_entry.set_date(row[2])
                    position_entry.insert(0, str(row[3]))
                    time_entry.insert(0, str(row[4]))
                    if mode == "view":
                        race_name_entry.config(state="readonly")
                        position_entry.config(state="readonly")
                        time_entry.config(state="readonly")
                        combo.config(state="disabled")
                        race_date_entry.config(state="disabled")

            def save_race():
                if mode == "view":
                    dialog.destroy()
                    return
                pilot_id = selected_pilot_id.get()
                if pilot_id == 0:
                    messagebox.showerror("Ошибка", "Выберите пилота")
                    return
                race_name = race_name_entry.get().strip()
                race_date = race_date_entry.get()
                try:
                    position = int(position_entry.get().strip())
                    if position <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Ошибка", "Позиция должна быть целым положительным числом")
                    return
                try:
                    time_sec = float(time_entry.get().strip())
                except ValueError:
                    messagebox.showerror("Ошибка", "Время должно быть числом (например 5678.123)")
                    return

                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                try:
                    if mode == "add":
                        cur.execute("INSERT INTO RaceResults (pilot_id, race_name, race_date, position, time_seconds) VALUES (?,?,?,?,?)",
                                    (pilot_id, race_name, race_date, position, time_sec))
                    else:
                        cur.execute("UPDATE RaceResults SET pilot_id=?, race_name=?, race_date=?, position=?, time_seconds=? WHERE result_id=?",
                                    (pilot_id, race_name, race_date, position, time_sec, record_id))
                    conn.commit()
                    messagebox.showinfo("Успех", "Сохранено")
                    self.load_data()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка БД", str(e))
                finally:
                    conn.close()

            if mode != "view":
                ttk.Button(dialog, text="Сохранить", command=save_race).pack(pady=10)
            else:
                ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()