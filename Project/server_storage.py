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

    def __init__(self):
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

        # Создаем базу + таблицы
        self.engine = create_engine('sqlite:///server_base.db3', echo=False)
        self.metadata.create_all(self.engine)
        mapper(self.Users, all_users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.ConnectionHistory, connection_history_table)

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
            self.session.commit()
        else:  # Новый пользователь
            user = self.Users(name, datetime.datetime.now())
            self.session.add(user)
            self.session.commit()

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


if __name__ == '__main__':
    db = ServerStorage()
    db.user_login('login', '192.168.0.1', 2525)
    db.user_login('login1', '192.168.0.2', 7777)
    print(db.users_list())
    print(db.active_users_list())
    db.user_logout('login1')
    print(db.active_users_list())
    print(db.login_history('login1'))
