class Customer:
    def __init__(self, name, phone, address, id=None):
        self.name = name
        self.phone = phone
        self.address = address
        self.id = id


class OrderItem:
    def __init__(self, order_id, product_name, quantity, price, id=None):
        self.order_id = order_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.id = id

    def get_total(self):
        return self.quantity * self.price


class Order:
    def __init__(self, customer_id, order_date, status, total, id=None):
        self.customer_id = customer_id
        self.order_date = order_date
        self.status = status
        self.total = total
        self.id = id
        self.customer = None
        self.items = []

    def calculate_total(self):
        self.total = 0
        for item in self.items:
            self.total += item.get_total()
        return self.total
