"""
1. Начать реализацию класса «Хранилище» для серверной стороны. Хранение необходимо осуществлять в базе данных.
В качестве СУБД использовать sqlite. Для взаимодействия с БД можно применять ORM.
Опорная схема базы данных:
На стороне сервера БД содержит следующие таблицы:
a) все пользователи:
* логин;
* информация (время последнего входа).
b) активные пользователи:
* id_клиента
* время входа;
* ip-адрес;
* port.
с) история клиента:
* id_клиента
* время входа;
* ip-адрес;
* port.
"""

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, ForeignKey, MetaData
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class ServerStorage:
    class Users:
        def __init__(self, login, last_connection):
            self.login = login
            self.last_connection = last_connection

        def __repr__(self):
            return f'<User({self.login}, {self.last_connection})>'

    class ActiveUsers:
        def __init__(self, user, ip, port):
            self.user = user
            self.ip = ip
            self.port = port
            self.login_time = datetime.datetime.now()

        def __repr__(self):
            return f'<User({self.user}, {self.ip}, {self.port}, {self.login_time})>'

    class ConnectionHistory:
        def __init__(self, user, ip, port, login_time):
            self.user = user
            self.ip = ip
            self.port = port
            self.login_time = login_time

        def __repr__(self):
            return f'<User({self.user}, {self.ip}, {self.port}, {self.login_time})>'

    # Lesson_4
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

        def __repr__(self):
            return f'<User contact({self.user}, {self.contact})>'

    # Lesson_4
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

        def __repr__(self):
            return f'<History( User {self.user}, sent {self.sent}, accepted {self.accepted})>'

    def __init__(self, path):
        # Создаем таблицы, связываем данные
        self.metadata = MetaData()

        all_users_table = Table('users', self.metadata,
                                Column('id', Integer, primary_key=True),  # типы данных берем из from sqlalchemy
                                Column('login', String, unique=True),
                                Column('last_connection', DateTime)
                                )

        active_users_table = Table('active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('users.id'), unique=True),
                                   # активный пользователь уникален
                                   Column('login_time', DateTime),
                                   Column('ip', String),
                                   Column('port', Integer)
                                   )

        connection_history_table = Table('connection_history', self.metadata,
                                         Column('id', Integer, primary_key=True),
                                         Column('user', ForeignKey('users.id')),
                                         Column('login_time', DateTime),
                                         Column('ip', String),
                                         Column('port', Integer)
                                         )

        # Lesson_4. Таблица контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('users.id')),
                         Column('contact', ForeignKey('users.id'))
                         )

        # Lesson_4. Таблица истории пользователей
        users_history = Table('History', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('user', ForeignKey('users.id')),
                              Column('sent', Integer),
                              Column('accepted', Integer)
                              )

        # Создаем базу + таблицы
        # self.engine = create_engine('sqlite:///server_base.db3', echo=False)

        # Lesson_4. Путь к базе берем из переданного параметра
        self.engine = create_engine(f'sqlite:///{path}', echo=False)

        self.metadata.create_all(self.engine)
        mapper(self.Users, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.ConnectionHistory, connection_history_table)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # При создании нового сервера очистим таблицу с активынми пользователями
        result = self.session.query(self.ActiveUsers)  # Запрос ко всей таблице (без фильтров)
        result.delete()
        self.session.commit()  # Не забываем, что при всех изменениях фиксируем транзакцию

    # Функция при входе пользователя
    # Надо обновить все таблицы. Если нет такого пользователя вообще, то добавить, записать историю входа,
    # обновить активных пользователей
    def user_login(self, name, ip, port):
        result = self.session.query(self.Users).filter_by(login=name)
        if result.count():
            user = result.first()
            user.last_connection = datetime.datetime.now()

            # Первончальное заполнение таблицы History
            # try:
            #    user_in_history = self.UsersHistory(user.id)
            #    self.session.add(user_in_history)
            #    self.session.commit()
            # except:
            #    print('')

            self.session.commit()
        else:  # Новый пользователь
            user = self.Users(name, datetime.datetime.now())
            self.session.add(user)
            self.session.commit()
            # Lesson_4
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        # Обновим данные об активных пользователях. По идее таблица должна быть пустая, мы же ее очищаем при старте
        active_user = self.ActiveUsers(user.id, ip, port)
        self.session.add(active_user)

        # Сделаем запись в историю
        history = self.ConnectionHistory(user.id, ip, port, datetime.datetime.now())
        self.session.add(history)
        self.session.commit()

    # Функция для получения списка всех пользователя, когда либо бывших в базе
    def users_list(self):
        return self.session.query(self.Users).all()  # Выведу пока все поля

    # Список всех активных пользователей
    def active_users_list(self):
        return self.session.query(self.Users.login, self.ActiveUsers.login_time, self.ActiveUsers.ip,
                                  self.ActiveUsers.port, self.ActiveUsers.login_time).join(self.Users).all()

    # Функция удаляет активных пользователей
    def user_logout(self, name):
        # Сначала получим пользователя
        result = self.session.query(self.Users).filter_by(login=name)
        if result.count():
            user = result.first()
            # А теперь удаляем из активных
            result = self.session.query(self.ActiveUsers).filter_by(user=user.id)
            result.delete()
            self.session.commit()

    # Функция выводит историю пользователя
    def login_history(self, name=None):
        query = self.session.query(self.Users.login,
                                   self.ConnectionHistory.login_time,
                                   self.ConnectionHistory.ip,
                                   self.ConnectionHistory.port
                                   ).join(self.Users)
        # Фильтр по имени пользователя, если указан
        if name:
            query = query.filter(self.Users.login == name)
        return query.all()

    # Lesson_4. Cписок контактов пользователя.
    def get_contacts(self, username):
        # Запрашиваем указанного пользователя
        user = self.session.query(self.Users).filter_by(name=username).one()

        # Запрашиваем его список контактов
        query = self.session.query(self.UsersContacts, self.Users.login). \
            filter_by(user=user.id). \
            join(self.Users, self.UsersContacts.contact == self.Users.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    # Lesson_4. Количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            self.Users.name,
            self.Users.last_connection,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.Users)
        # Возвращаем список кортежей
        return query.all()

    # Lesson_4. Функция добавляет контакт для пользователя.
    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id,
                                                                           contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # Lesson_4. Функция удаляет контакт из базы данных
    def remove_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    # Lesson_4. Функция фиксирует передачу сообщения и делает соответствующие отметки в БД
    def process_message(self, sender, recipient):
        # Получаем ID отправителя и получателя
        sender = self.session.query(self.Users).filter_by(login=sender).first().id
        recipient = self.session.query(self.Users).filter_by(login=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        # print(sender_row)
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()


if __name__ == '__main__':
    db = ServerStorage('server_base.db3')
    db.user_login('login', '192.168.0.1', 2525)
    db.user_login('login1', '192.168.0.2', 7777)
    db.user_login('login2', '192.168.0.3', 7778)
    db.user_login('login3', '192.168.0.4', 7789)
    db.user_login('login4', '192.168.0.5', 7787)
    db.user_login('login5', '192.168.0.6', 7788)
    print(db.users_list())
    print(db.active_users_list())
    db.user_logout('login1')
    print(db.active_users_list())
    print(db.login_history('login1'))

    # Lesson_4
    db.add_contact('login', 'login1')
    db.add_contact('login', 'login2')
    db.add_contact('login3', 'login')
    db.remove_contact('login', 'login2')
    db.process_message('login', 'login1')
    db.process_message('login2', 'login3')
    db.process_message('login', 'login4')
