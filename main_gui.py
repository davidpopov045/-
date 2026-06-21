import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from models import *
from tkinter import filedialog
from data_export import DataExport

class DeliveryGui:
    def __init__(self, root: tk.Tk):
        self.orders = None
        self.tree_detail = None
        self.status_filter = None
        self.tree = None
        self.root = root
        self.root.geometry('1000x800')
        self.db = Database()
        self.exporter = DataExport(self.db)
        self.filter = None

        self.create_components()
        self.show_orders()

    def create_components(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        filter_frame = ttk.LabelFrame(main_frame, text='Фильтры', padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        status_label = ttk.Label(filter_frame, text='Статус: ')
        status_label.pack(side=tk.LEFT, padx=5)

        self.status_filter = ttk.Combobox(filter_frame,
                                          values=['Все', 'новый', 'в доставке', 'выполнен', 'отменён'])
        self.status_filter.set("Все")
        self.status_filter.pack(side=tk.LEFT, padx=5)

        apply_button = ttk.Button(filter_frame, text='Применить', command=self.apply_filter)
        apply_button.pack(side=tk.LEFT, padx=5)

        reset_button = ttk.Button(filter_frame, text='Сброс', command=self.reset_filter)
        reset_button.pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        add_button = ttk.Button(button_frame, text='Добавить заказ', command=self.add_order)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text='Редактировать заказ', command=self.edit_order)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text='Удалить заказ', command=self.delete_order)
        delete_button.pack(side=tk.LEFT, padx=5)

        separator = ttk.Separator(button_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=10)

        report_button = ttk.Button(button_frame, text='Отчет', command=self.show_report)
        report_button.pack(side=tk.LEFT, padx=5)

        import_button = ttk.Button(button_frame, text='Импорт', command=self.import_data)
        import_button.pack(side=tk.LEFT, padx=5)

        export_button = ttk.Button(button_frame, text='Экспорт', command=self.export_data)
        export_button.pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('ID', 'Клиент', 'Дата', 'Статус', 'Сумма')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.bind("<<TreeviewSelect>>", lambda x: self.on_tree_select())
        ysb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.pack()

        separator = ttk.Separator(tree_frame, orient=tk.HORIZONTAL)
        separator.pack(side=tk.TOP, pady=10)

        columns = ('ID', 'Продукт', 'Количество', 'Стоимость', 'Итого')
        self.tree_detail = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree_detail.heading("ID", text="ID")
        self.tree_detail.heading("Продукт", text="Продукт")
        self.tree_detail.heading("Количество", text="Количество")
        self.tree_detail.heading("Стоимость", text="Стоимость")
        self.tree_detail.heading("Итого", text="Итого")
        ysb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=ysb.set)
        self.tree_detail.pack()

    def show_orders(self):
        self.tree.delete(*self.tree.get_children())
        self.orders = self.db.get_all_orders(status=self.filter)
        for order in self.orders:
            date_str = order.order_date.strftime('%d-%m-%Y')
            self.tree.insert('', tk.END, values=
            (order.id, order.customer.name, date_str, order.status, order.total))

    def on_tree_select(self):
        self.tree_detail.delete(*self.tree_detail.get_children())
        selected_items = self.tree.selection()
        for item_id in selected_items:
            item_text = self.tree.item(item_id, "text")
            item_values = self.tree.item(item_id, "values")
            id_order = int(item_values[0])
            select_order = None
            for order in self.orders:
                if order.id == id_order:
                    select_order = order
                    break
            for order_item in select_order.items:
                self.tree_detail.insert('', tk.END, values=
                (order_item.id, order_item.product_name, order_item.quantity, order_item.price, order_item.get_total()))

    def apply_filter(self):
        self.filter = self.status_filter.get()
        if self.filter == 'Все':
            self.filter = None
        self.show_orders()

    def reset_filter(self):
        self.filter = None
        self.status_filter.set("Все")
        self.show_orders()

    def add_order(self):
        window = OrderItemWindow(self.root, self.db)
        self.root.wait_window(window.dialog)
        self.show_orders()

    def edit_order(self):
        pass

    def delete_order(self):
        selected_items = self.tree.selection()
        if len(selected_items) > 0:
            answer = messagebox.askyesno("Удаление", "Вы действительно желаете удалить заказ?")
            if answer:
                for item_id in selected_items:
                    item_text = self.tree.item(item_id, "text")
                    item_values = self.tree.item(item_id, "values")
                    id_order = int(item_values[0])
                    self.db.delete_order(id_order)
                    self.show_orders()

    def show_report(self):
        report = ReportWindow(self.root, self.db)

    def import_data(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Json Files", "*.json"), ("All Files", "*.*")],
            title="Import data"
        )
        if file_path:
            self.exporter.import_from_json(file_path)
            self.show_orders()


    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Json Files", "*.json"), ("All Files", "*.*")],
            title="Export data"
        )
        if file_path:
            self.exporter.export_to_json(file_path)


class OrderItemWindow:
    def __init__(self, root, database):
        self.db = database
        self.items = []

        self.dialog = tk.Toplevel(root)
        self.dialog.geometry('800x500')
        self.dialog.transient(root)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        customer_frame = ttk.Frame(main_frame)
        customer_frame.pack(fill=tk.X, pady=(0, 10))

        self.customers = self.db.get_all_customers()
        customer_label = ttk.Label(customer_frame, text='Заказчик: ')
        customer_label.pack(side=tk.LEFT, padx=5)

        customers_name = [customer.name for customer in self.customers]
        self.customer_combo = ttk.Combobox(customer_frame, values=customers_name)
        self.customer_combo.pack(side=tk.LEFT, padx=5)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        status_label = ttk.Label(status_frame, text='Статус: ')
        status_label.pack(side=tk.LEFT, padx=5)

        self.status_combo = ttk.Combobox(status_frame, values=['новый', 'в доставке', 'выполнен', 'отменён'])
        self.status_combo.pack(side=tk.LEFT, padx=5)

        items_frame = ttk.Frame(main_frame)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('ID', 'Продукт', 'Количество', 'Стоимость', 'Итого')
        self.tree_detail = ttk.Treeview(items_frame, columns=columns, show="headings")
        self.tree_detail.heading("ID", text="ID")
        self.tree_detail.heading("Продукт", text="Продукт")
        self.tree_detail.heading("Количество", text="Количество")
        self.tree_detail.heading("Стоимость", text="Стоимость")
        self.tree_detail.heading("Итого", text="Итого")
        ysb = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_detail.yview)
        self.tree_detail.configure(yscrollcommand=ysb.set)
        self.tree_detail.pack()

        item_frame = ttk.LabelFrame(main_frame, text='Введите данные о товаре', padding=5)
        item_frame.pack(fill=tk.X, pady=(0, 10))

        name_label = ttk.Label(item_frame, text='Название: ')
        name_label.pack(side=tk.LEFT, padx=5)

        self.name_entry = ttk.Entry(item_frame, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        count_label = ttk.Label(item_frame, text='Кол-во: ')
        count_label.pack(side=tk.LEFT, padx=5)

        self.count_entry = ttk.Entry(item_frame, width=20)
        self.count_entry.pack(side=tk.LEFT, padx=5)

        cost_label = ttk.Label(item_frame, text='Стоимость: ')
        cost_label.pack(side=tk.LEFT, padx=5)

        self.cost_entry = ttk.Entry(item_frame, width=20)
        self.cost_entry.pack(side=tk.LEFT, padx=5)

        add_item_button = ttk.Button(item_frame, text='Добавить', command=self.add_item)
        add_item_button.pack(side=tk.LEFT, padx=5)

        ok_frame = ttk.Frame(main_frame)
        ok_frame.pack(fill=tk.BOTH, pady=(0, 10))

        add_order_button = ttk.Button(ok_frame, text='Создать заказ', command=self.create_order)
        add_order_button.pack(side=tk.LEFT, padx=5)


    def add_item(self):
        order_item = OrderItem(0, self.name_entry.get(), int(self.count_entry.get()),
                               int(self.cost_entry.get()), 0)

        self.tree_detail.insert('', tk.END, values=
            (order_item.id, order_item.product_name, order_item.quantity, order_item.price, order_item.get_total()))
        self.items.append(order_item)
        self.name_entry.delete(0, tk.END)
        self.count_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)

    def create_order(self):
        status = self.status_combo.get()
        date_order = datetime.datetime.now()
        customer_name = self.customer_combo.get()
        customer = [c for c in self.customers if c.name == customer_name][0]
        order = Order(customer.id, date_order, status, 0)
        order.items = self.items
        order.calculate_total()
        self.db.add_order(order)
        self.dialog.destroy()


class ReportWindow:
    def __init__(self, root, database):
        self.db = database

        self.dialog = tk.Toplevel(root)
        self.dialog.geometry('800x500')
        self.dialog.transient(root)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        report1_frame = ttk.Frame(main_frame)
        report1_frame.pack(fill=tk.X, pady=(0, 10))

        report1_label = ttk.Label(report1_frame, text='Количество заказов по статусам')
        report1_label.pack(side=tk.LEFT, padx=5)

        columns = ('Статус', 'Количество')
        tree_report1 = ttk.Treeview(report1_frame, columns=columns, show="headings")
        tree_report1.heading("Статус", text="Статус")
        tree_report1.heading("Количество", text="Количество")
        ysb = ttk.Scrollbar(report1_frame, orient=tk.VERTICAL, command=tree_report1.yview)
        tree_report1.configure(yscrollcommand=ysb.set)
        tree_report1.pack()

        query1 = self.db.get_orders_by_status()
        for k, w in query1.items():
            tree_report1.insert('', tk.END, values=(k, w))

        report2_frame = ttk.Frame(main_frame)
        report2_frame.pack(fill=tk.X, pady=(0, 10))

        report2_label = ttk.Label(report2_frame, text='Топ-3 клиента по сумме заказов')
        report2_label.pack(side=tk.LEFT, padx=5)

        columns = ('Клиент', 'Сумма')
        tree_report2 = ttk.Treeview(report2_frame, columns=columns, show="headings")
        tree_report2.heading("Клиент", text="Клиент")
        tree_report2.heading("Сумма", text="Сумма")
        ysb = ttk.Scrollbar(report2_frame, orient=tk.VERTICAL, command=tree_report2.yview)
        tree_report2.configure(yscrollcommand=ysb.set)
        tree_report2.pack()

        query2 = self.db.get_top_customers()
        for t in query2:
            tree_report2.insert('', tk.END, values=(t[1], t[2]))



def main():
    root = tk.Tk()
    app = DeliveryGui(root)
    root.mainloop()


if __name__ == '__main__':
    main()
