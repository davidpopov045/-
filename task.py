class User:
    count = 0

    def __init__(self, name, login, password, grade):
        if grade <= 0:
            raise ValueError('оценка должна быть положительным числом')
        self._name = name
        self._login = login
        self._password = password
        self._grade = grade
        if not isinstance(self, SuperUser):
            User.count += 1

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        raise ValueError('Невозможно изменить логин!')

    @property
    def password(self):
        return '*' * len(self._password)

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def grade(self):
        raise ValueError('Неизвестное свойство grade')


    @grade.setter
    def grade(self, value):
        raise ValueError('Неизвестное свойство grade')

    def show_info(self):
        print(f'Name: {self._name}, Login: {self._login}')

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self._grade == other._grade

    def __lt__(self, other):
        if not isinstance(other, User):
            return False
        return self._grade < other._grade

    def __gt__(self, other):
        if not isinstance(other, User):
            return False
        return self._grade > other._grade


class SuperUser(User):
    count = 0

    def __init__(self, name, login, password, role, grade):
        super().__init__(name, login, password, grade)
        self._role = role
        SuperUser.count += 1

    def show_info(self):
        print(f'Name: {self._name}, Login: {self._login}, Role: {self._role}')


def main():
    user1 = User('Paul McCartney', 'paul', '1234', 3)
    user2 = User('George Harrison', 'george', '5678', 2)
    user3 = User('Richard Starkey', 'ringo', '8523', 3)
    admin = SuperUser('John Lennon', 'john', '0000', 'admin', 5)

    user1.show_info()
    admin.show_info()

    users = User.count
    admins = SuperUser.count

    print(f'Всего обычных пользователей: {users}')
    print(f'Всего супер-пользователей: {admins}')

    print(user1 < user2)
    print(admin > user3)
    print(user1 == user3)

    user3.name = 'Ringo Star'
    user1.password = 'Pa$$w0rd'

    print(user3.name)
    print(user2.password)
    print(user2.login)

    try:
        user2.login = 'geo'
    except ValueError as err:
        print(err)

    try:
        print(user1.grade)
    except ValueError as err:
        print(err)

    try:
        admin.grade = 10
    except ValueError as err:
        print(err)


main()



