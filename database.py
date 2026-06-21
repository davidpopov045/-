import sqlite3
import os
import datetime
from models import *
from logger_config import logger

class Database:
    def __init__(self):
        self.db_path = 'data/delivery.db'
        if not os.path.exists(self.db_path):
            self.create_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT)
        ''')

        cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER REFERENCES customers(id) ON DELETE RESTRICT,
                order_date TEXT NOT NULL,
                status TEXT CHECK(status IN ('новый','в доставке','выполнен','отменён')),
                total REAL NOT NULL)
        ''')

        cursor.execute('''
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER REFERENCES orders(id),
                product_name TEXT,
                quantity INTEGER,
                price REAL)
        ''')

        conn.commit()
        conn.close()
        logger.info('База данных создана')

    def add_customer(self, customer):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)',
                       (customer.name, customer.phone, customer.address))
        conn.commit()
        customer.id = cursor.lastrowid
        conn.close()
        logger.info(f'Добавлен заказчик с id = {customer.id}')

    def get_customer(self, customer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id, ))
        row = cursor.fetchone()
        customer = None
        if row:
            customer = Customer(row[1], row[2], row[3], row[0])
        conn.close()
        return customer

    def get_all_customers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        rows = cursor.fetchall()
        customers = []
        for row in rows:
            customer = Customer(row[1], row[2], row[3], row[0])
            customers.append(customer)
        conn.close()
        return customers

    def delete_customer(self, customer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        conn.commit()
        conn.close()
        logger.info(f'Удален заказчик с id = {customer_id}')

    def add_order(self, order):
        conn = self.get_connection()
        cursor = conn.cursor()
        date_str = order.order_date.strftime('%d-%m-%Y')
        cursor.execute('INSERT INTO orders (customer_id, order_date, status, total) VALUES (?, ?, ?, ?)',
                       (order.customer_id, date_str, order.status, order.total))
        order.id = cursor.lastrowid
        for item in order.items:
            cursor.execute('INSERT INTO order_items (order_id, product_name, quantity, price) VALUES (?, ?, ?, ?)',
                           (order.id, item.product_name, item.quantity, item.price))
            item.id = cursor.lastrowid
            item.order_id = order.id
        conn.commit()
        conn.close()
        logger.info(f'Добавлен заказ с id = {order.id}')


    def get_all_orders(self, status=None, date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT * from orders"
        params = []
        if status is not None:
            query += ' WHERE status = ?'
            params.append(status)
        if date is not None:
            if status is not None:
                query += " AND "
            else:
                query += ' WHERE '
            query += "order_date = ?"
            date_str = date.strftime('%d-%m-%Y')
            params.append(date_str)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            order_date = datetime.datetime.strptime(row[2], '%d-%m-%Y')
            order = Order(row[1],order_date,row[3], row[4], row[0])
            order.customer = self.get_customer(row[1])
            cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (row[0],))
            item_rows = cursor.fetchall()
            for item_row in item_rows:
                ord_item = OrderItem(item_row[1], item_row[2], item_row[3], item_row[4], item_row[0])
                order.items.append(ord_item)
            orders.append(order)
        conn.close()
        return orders



    def delete_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
        logger.info(f'Удален заказ с id = {order_id}')


    def get_orders_by_status(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT status, COUNT(*) as count FROM orders GROUP BY status')
        rows = cursor.fetchall()
        result = {}
        for status, count in rows:
            result[status] = count
        conn.close()
        return result


    def get_top_customers(self, limit=3):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, SUM(o.total) as total_sum 
            FROM customers c JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            ORDER BY total_sum DESC 
            LIMIT ?
        ''', (limit,))
        res = cursor.fetchall()
        conn.close()
        return res
