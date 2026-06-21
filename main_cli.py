import argparse
import sys
import datetime
from database import Database
from models import *
from data_export import DataExport


def main():
    parser = argparse.ArgumentParser(description='Система Быстрая доставка')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    report_parser = subparsers.add_parser('report', help='Отчеты и аналитика')
    report_parser.add_argument('--period', choices=['day', 'week', 'month'],
                               default='month', help='Период для отчета')

    export_parser = subparsers.add_parser('export', help='Экспорт данных')
    export_parser.add_argument('--file', required=True, help='Путь к файлу для экспорта')

    import_parser = subparsers.add_parser('import', help='Импорт данных')
    import_parser.add_argument('--file', required=True, help='Путь к файлу для импорта')

    add_customer_parser = subparsers.add_parser('add_customer', help='Добавление клиента')
    add_customer_parser.add_argument('--name', required=True, help='Имя клиента')
    add_customer_parser.add_argument('--phone', required=True, help='Телефон клиента')
    add_customer_parser.add_argument('--address', required=True, help='Адрес клиента')

    show_customers_parser = subparsers.add_parser('show_customers', help='Вывод клиентов')

    delete_customer_parser = subparsers.add_parser('delete_customer', help='Удаление клиента по id')
    delete_customer_parser.add_argument('--id', required=True, help='Id клиента')

    add_order_parser = subparsers.add_parser('add_order', help='Добавление заказа')
    add_order_parser.add_argument('--customer_id', type=int, required=True, help='Id клиента')
    add_order_parser.add_argument('--status', required=True,
                                  choices=['новый','в доставке','выполнен','отменён'], help='Статус клиента')

    show_orders_parser = subparsers.add_parser('show_orders', help='Вывод заказов')
    delete_order_parser = subparsers.add_parser('delete_order', help='Удаление заказа по id')
    delete_order_parser.add_argument('--id', required=True, help='Id заказа')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    db = Database()
    exporter = DataExport(db)

    if args.command == 'report':
        print('Список отчетов')
        print('Количество заказов по статусам')
        report1 = db.get_orders_by_status()
        for k, v in report1.items():
            print(k, v)
        print('\nТоп-3 клиента по сумме заказов')
        report2 = db.get_top_customers()
        for cust in report2:
            print(cust[1], cust[2])

    elif args.command == 'export':
        filepath = args.file
        if filepath.endswith('.json'):
            exporter.export_to_json(filepath)
            print('Данные успешно экспортированы в', filepath)
        else:
            print('Система поддерживает только формат json')
            sys.exit(1)
    elif args.command == 'import':
        filepath = args.file
        if filepath.endswith('.json'):
            exporter.import_from_json(filepath)
            print('Данные успешно экспортированы в', filepath)
        else:
            print('Система поддерживает только формат json')
            sys.exit(1)
    elif args.command == 'add_customer':
        customer = Customer(args.name, args.phone, args.address)
        db.add_customer(customer)
        print(f'Успешно добавлен заказчик с id {customer.id}')
    elif args.command == 'add_order':
        order = Order(args.customer_id, datetime.datetime.now(), args.status, 0)
        db.add_order(order)
        print(f'Успешно добавлен заказ с id {order.id}')
    elif args.command == "show_customers":
        customers = db.get_all_customers()
        for customer in customers:
            print(customer.id, customer.name, customer.phone, customer.address)
    elif args.command == "show_orders":
        orders = db.get_all_orders()
        for order in orders:
            print(order.id, order.order_date, order.status, order.total, order.customer.name)
            for item in order.items:
                print('\t', item.id, item.product_name, item.quantity, item.price)
    elif args.command == 'delete_customer':
        id = args.id
        db.delete_customer(id)
    elif args.command == 'delete_order':
        id = args.id
        db.delete_order(id)


main()
