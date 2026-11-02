import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0192837465DRIN",
    "database": "avtoservis"
}

def connect():
    return mysql.connector.connect(**DB_CONFIG)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет заказов автосервиса")
        self.root.geometry("1000x620")
        self.root.minsize(850, 520)

        title = tk.Label(root, text="Учет заказов автосервиса",
                         font=("Arial", 18, "bold"))
        title.pack(pady=10)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.client_tab = ttk.Frame(self.tabs)
        self.car_tab = ttk.Frame(self.tabs)
        self.order_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.client_tab, text="Клиенты")
        self.tabs.add(self.car_tab, text="Автомобили")
        self.tabs.add(self.order_tab, text="Заказы")

        self.build_clients()
        self.build_cars()
        self.build_orders()
        self.refresh_all()

    def run_query(self, sql, values=(), fetch=False):
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(sql, values)
            result = cur.fetchall() if fetch else None
            conn.commit()
            cur.close()
            conn.close()
            return result if fetch else True
        except Error as e:
            messagebox.showerror("Ошибка базы данных",
                                 f"{e}\n\nПроверьте настройки подключения и создание базы.")
            return None

    def make_tree(self, parent, columns, headings):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=14)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=130, anchor="center")
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        return tree

    def selected_id(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите запись в таблице.")
            return None
        return tree.item(selected[0], "values")[0]

    def build_clients(self):
        form = ttk.Frame(self.client_tab)
        form.pack(fill="x", padx=8, pady=8)
        self.client_name = tk.StringVar()
        self.client_phone = tk.StringVar()
        ttk.Label(form, text="ФИО:").grid(row=0, column=0, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.client_name, width=28).grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Телефон:").grid(row=0, column=2, padx=4)
        ttk.Entry(form, textvariable=self.client_phone, width=20).grid(row=0, column=3, padx=4)
        ttk.Button(form, text="Добавить", command=self.add_client).grid(row=0, column=4, padx=4)
        ttk.Button(form, text="Изменить выбранного", command=self.edit_client).grid(row=0, column=5, padx=4)
        ttk.Button(form, text="Удалить выбранного", command=self.delete_client).grid(row=0, column=6, padx=4)
        self.clients_tree = self.make_tree(self.client_tab,
            ("id", "name", "phone"), ("ID", "ФИО", "Телефон"))

    def add_client(self):
        name, phone = self.client_name.get().strip(), self.client_phone.get().strip()
        if not name or not phone:
            messagebox.showwarning("Проверка", "Введите ФИО и телефон.")
            return
        if self.run_query("INSERT INTO clients (full_name, phone) VALUES (%s, %s)", (name, phone)) is not None:
            self.client_name.set(""); self.client_phone.set(""); self.refresh_all()

    def edit_client(self):
        cid = self.selected_id(self.clients_tree)
        if cid is None: return
        name, phone = self.client_name.get().strip(), self.client_phone.get().strip()
        if not name or not phone:
            messagebox.showwarning("Проверка", "Введите новые ФИО и телефон в поля сверху.")
            return
        if self.run_query("UPDATE clients SET full_name=%s, phone=%s WHERE id=%s", (name, phone, cid)) is not None:
            self.refresh_all()

    def delete_client(self):
        cid = self.selected_id(self.clients_tree)
        if cid is None: return
        if messagebox.askyesno("Подтверждение", "Удалить клиента? У клиента не должно быть автомобилей."):
            if self.run_query("DELETE FROM clients WHERE id=%s", (cid,)) is not None:
                self.refresh_all()

    def build_cars(self):
        form = ttk.Frame(self.car_tab)
        form.pack(fill="x", padx=8, pady=8)
        self.car_client = tk.StringVar()
        self.car_plate = tk.StringVar()
        self.car_brand = tk.StringVar()
        self.car_model = tk.StringVar()
        ttk.Label(form, text="ID клиента:").grid(row=0, column=0, padx=3, pady=4)
        ttk.Entry(form, textvariable=self.car_client, width=9).grid(row=0, column=1, padx=3)
        ttk.Label(form, text="Гос. номер:").grid(row=0, column=2, padx=3)
        ttk.Entry(form, textvariable=self.car_plate, width=14).grid(row=0, column=3, padx=3)
        ttk.Label(form, text="Марка:").grid(row=0, column=4, padx=3)
        ttk.Entry(form, textvariable=self.car_brand, width=14).grid(row=0, column=5, padx=3)
        ttk.Label(form, text="Модель:").grid(row=0, column=6, padx=3)
        ttk.Entry(form, textvariable=self.car_model, width=14).grid(row=0, column=7, padx=3)
        ttk.Button(form, text="Добавить", command=self.add_car).grid(row=1, column=1, padx=3, pady=6)
        ttk.Button(form, text="Изменить выбранный", command=self.edit_car).grid(row=1, column=2, columnspan=2, padx=3)
        ttk.Button(form, text="Удалить выбранный", command=self.delete_car).grid(row=1, column=4, columnspan=2, padx=3)
        ttk.Label(self.car_tab, text="ID клиента можно посмотреть во вкладке «Клиенты».").pack(anchor="w", padx=12)
        self.cars_tree = self.make_tree(self.car_tab,
            ("id", "client", "plate", "brand", "model"),
            ("ID", "ID клиента", "Гос. номер", "Марка", "Модель"))

    def add_car(self):
        client, plate, brand, model = (self.car_client.get().strip(), self.car_plate.get().strip(),
                                       self.car_brand.get().strip(), self.car_model.get().strip())
        if not all((client, plate, brand, model)):
            messagebox.showwarning("Проверка", "Заполните все поля автомобиля.")
            return
        if self.run_query("INSERT INTO cars (client_id, plate, brand, model) VALUES (%s,%s,%s,%s)",
                          (client, plate, brand, model)) is not None:
            self.refresh_all()

    def edit_car(self):
        cid = self.selected_id(self.cars_tree)
        if cid is None: return
        vals = (self.car_client.get().strip(), self.car_plate.get().strip(),
                self.car_brand.get().strip(), self.car_model.get().strip())
        if not all(vals):
            messagebox.showwarning("Проверка", "Введите новые данные автомобиля в поля сверху.")
            return
        if self.run_query("UPDATE cars SET client_id=%s, plate=%s, brand=%s, model=%s WHERE id=%s",
                          (*vals, cid)) is not None:
            self.refresh_all()

    def delete_car(self):
        cid = self.selected_id(self.cars_tree)
        if cid is None: return
        if messagebox.askyesno("Подтверждение", "Удалить автомобиль?"):
            if self.run_query("DELETE FROM cars WHERE id=%s", (cid,)) is not None:
                self.refresh_all()

    def build_orders(self):
        form = ttk.Frame(self.order_tab)
        form.pack(fill="x", padx=8, pady=8)
        self.order_car = tk.StringVar()
        self.order_work = tk.StringVar()
        self.order_cost = tk.StringVar()
        self.order_status = tk.StringVar(value="Новый")
        self.search_plate = tk.StringVar()
        ttk.Label(form, text="ID авто:").grid(row=0, column=0, padx=3, pady=4)
        ttk.Entry(form, textvariable=self.order_car, width=8).grid(row=0, column=1, padx=3)
        ttk.Label(form, text="Работа:").grid(row=0, column=2, padx=3)
        ttk.Entry(form, textvariable=self.order_work, width=22).grid(row=0, column=3, padx=3)
        ttk.Label(form, text="Стоимость:").grid(row=0, column=4, padx=3)
        ttk.Entry(form, textvariable=self.order_cost, width=10).grid(row=0, column=5, padx=3)
        ttk.Label(form, text="Статус:").grid(row=0, column=6, padx=3)
        ttk.Combobox(form, textvariable=self.order_status, width=12, state="readonly",
                     values=("Новый", "В работе", "Выполнен", "Отменен")).grid(row=0, column=7, padx=3)
        ttk.Button(form, text="Создать заказ", command=self.add_order).grid(row=1, column=1, padx=3, pady=6)
        ttk.Button(form, text="Изменить выбранный", command=self.edit_order).grid(row=1, column=2, columnspan=2, padx=3)
        ttk.Button(form, text="Удалить выбранный", command=self.delete_order).grid(row=1, column=4, padx=3)

        search = ttk.Frame(self.order_tab)
        search.pack(fill="x", padx=8)
        ttk.Label(search, text="Поиск по гос. номеру:").pack(side="left", padx=4)
        ttk.Entry(search, textvariable=self.search_plate, width=18).pack(side="left", padx=4)
        ttk.Button(search, text="Найти", command=self.search_orders).pack(side="left", padx=4)
        ttk.Button(search, text="Все заказы", command=self.refresh_orders).pack(side="left", padx=4)
        ttk.Button(search, text="Отчет выполненных", command=self.completed_report).pack(side="left", padx=4)
        self.orders_tree = self.make_tree(self.order_tab,
            ("id", "plate", "work", "cost", "status", "created"),
            ("ID", "Гос. номер", "Работа", "Стоимость", "Статус", "Дата создания"))

    def add_order(self):
        car, work, cost, status = (self.order_car.get().strip(), self.order_work.get().strip(),
                                   self.order_cost.get().strip(), self.order_status.get().strip())
        if not car or not work or not cost:
            messagebox.showwarning("Проверка", "Введите ID авто, работу и стоимость.")
            return
        try:
            cost = float(cost.replace(",", "."))
            if cost < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Проверка", "Стоимость должна быть числом не меньше нуля.")
            return
        if self.run_query("INSERT INTO orders (car_id, work_description, cost, status) VALUES (%s,%s,%s,%s)",
                          (car, work, cost, status)) is not None:
            self.refresh_all()

    def edit_order(self):
        oid = self.selected_id(self.orders_tree)
        if oid is None: return
        car, work, cost, status = (self.order_car.get().strip(), self.order_work.get().strip(),
                                   self.order_cost.get().strip(), self.order_status.get().strip())
        if not car or not work or not cost:
            messagebox.showwarning("Проверка", "Введите новые данные заказа в поля сверху.")
            return
        try:
            cost = float(cost.replace(",", "."))
            if cost < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Проверка", "Стоимость должна быть числом не меньше нуля.")
            return
        if self.run_query("UPDATE orders SET car_id=%s, work_description=%s, cost=%s, status=%s WHERE id=%s",
                          (car, work, cost, status, oid)) is not None:
            self.refresh_all()

    def delete_order(self):
        oid = self.selected_id(self.orders_tree)
        if oid is None: return
        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            if self.run_query("DELETE FROM orders WHERE id=%s", (oid,)) is not None:
                self.refresh_all()

    def fill_tree(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows or []:
            tree.insert("", "end", values=row)

    def refresh_clients(self):
        rows = self.run_query("SELECT id, full_name, phone FROM clients ORDER BY id", fetch=True)
        self.fill_tree(self.clients_tree, rows)

    def refresh_cars(self):
        rows = self.run_query("SELECT id, client_id, plate, brand, model FROM cars ORDER BY id", fetch=True)
        self.fill_tree(self.cars_tree, rows)

    def refresh_orders(self):
        rows = self.run_query(
            "SELECT o.id, c.plate, o.work_description, o.cost, o.status, "
            "DATE_FORMAT(o.created_at, '%d.%m.%Y %H:%i') "
            "FROM orders o JOIN cars c ON o.car_id=c.id ORDER BY o.id DESC", fetch=True)
        self.fill_tree(self.orders_tree, rows)

    def refresh_all(self):
        self.refresh_clients()
        self.refresh_cars()
        self.refresh_orders()

    def search_orders(self):
        plate = self.search_plate.get().strip()
        if not plate:
            self.refresh_orders()
            return
        rows = self.run_query(
            "SELECT o.id, c.plate, o.work_description, o.cost, o.status, "
            "DATE_FORMAT(o.created_at, '%d.%m.%Y %H:%i') "
            "FROM orders o JOIN cars c ON o.car_id=c.id WHERE c.plate LIKE %s ORDER BY o.id DESC",
            (f"%{plate}%",), fetch=True)
        self.fill_tree(self.orders_tree, rows)

    def completed_report(self):
        rows = self.run_query(
            "SELECT o.id, c.plate, o.work_description, o.cost, o.status, "
            "DATE_FORMAT(o.created_at, '%d.%m.%Y %H:%i') "
            "FROM orders o JOIN cars c ON o.car_id=c.id WHERE o.status='Выполнен' ORDER BY o.created_at DESC",
            fetch=True)
        self.fill_tree(self.orders_tree, rows)
        total = sum(float(row[3]) for row in (rows or []))
        messagebox.showinfo("Отчет", f"Выполненных заказов: {len(rows or [])}\nОбщая стоимость: {total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
