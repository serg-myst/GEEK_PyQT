import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt
import os
from server_storage import ServerStorage


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.initUI()
        self.db = db
        self.create_active_users()

    def initUI(self):
        # Создаем кнопки в главном меню окна
        # Кнопка "Выход"
        self.exit = QAction(QIcon("exit.png"), 'Выход', self)
        self.exit.setShortcut('Ctrl+Q')
        self.exit.setStatusTip('Выход')
        self.exit.triggered.connect(qApp.quit)

        # Кнопка обновить таблицу активных пользователей
        self.refresh = QAction(QIcon("refresh.png"), 'Выход', self)
        self.refresh.setShortcut('Ctrl+R')
        self.refresh.setStatusTip('Обновить')
        self.refresh.triggered.connect(self.create_active_users)

        # Кнопка истории клиентов
        self.show_history = QAction('История клиентов', self)
        self.show_history.triggered.connect(self.create_history_table)

        # Кнопка настройки сервера
        self.show_server_parameters = QAction('Настройки сервера', self)
        self.show_server_parameters.triggered.connect(self.show_parameters)

        # Кнопка показать всех пользователей
        self.show_all_users = QAction('Показать всех пользователей', self)
        self.show_all_users.triggered.connect(self.create_all_users_table)

        self.statusBar()

        # Размеры окна + Заголовок
        self.setFixedSize(800, 600)
        self.setWindowTitle('Обработка работы сервера')

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exit)
        self.toolbar.addAction(self.refresh)
        self.toolbar.addAction(self.show_history)
        self.toolbar.addAction(self.show_server_parameters)
        self.toolbar.addAction(self.show_all_users)

        self.active_clients = QTableView(self)
        self.active_clients.move(10, 55)
        self.active_clients.setFixedSize(780, 400)

        self.show()

    # Добавил еще и список всех пользователей
    def create_all_users_table(self):
        database = self.db
        window = AllUsersWindow(self)
        users_list = database.users_list()
        list_table = QStandardItemModel(window)  # табличная часть
        list_table.setHorizontalHeaderLabels(['Пользователь', 'Время последнего подключения'])
        for user in users_list:
            user_login = QStandardItem(user.login)
            user_login.setEditable(False)
            last_connection = QStandardItem(str(user.last_connection))
            last_connection.setEditable(False)
            list_table.appendRow([user_login, last_connection])
        window.table_list.setModel(list_table)
        window.table_list.resizeColumnsToContents()
        window.exec_()

    # Выведем историю
    def create_history_table(self):
        database = self.db
        window = UsersHistoryWindow(self)
        users_list = database.login_history()
        list_table = QStandardItemModel(window)  # табличная часть
        list_table.setHorizontalHeaderLabels(['Пользователь', 'Время последнего подключения'])
        for user in users_list:
            user_login = QStandardItem(user.login)
            user_login.setEditable(False)
            ip = QStandardItem(user.ip)
            ip.setEditable(False)
            port = QStandardItem(str(user.port))
            port.setEditable(False)
            login_time = QStandardItem(str(user.login_time))
            login_time.setEditable(False)
            list_table.appendRow([user_login, ip, port, login_time])
        window.table_list.setModel(list_table)
        window.table_list.resizeColumnsToContents()
        window.exec_()

    # Заполнение таблицы активных пользователей
    def create_active_users(self):
        database = self.db
        users_list = database.active_users_list()
        list_table = QStandardItemModel(self)  # табличная часть
        list_table.setHorizontalHeaderLabels(['Клиент', 'IP', 'Порт', 'Время подключения'])
        for user in users_list:
            user_login = QStandardItem(user.login)
            user_login.setEditable(False)
            ip = QStandardItem(user.ip)
            ip.setEditable(False)
            port = QStandardItem(str(user.port))
            port.setEditable(False)
            login_time = QStandardItem(str(user.login_time))
            login_time.setEditable(False)
            list_table.appendRow([user_login, ip, port, login_time])
        self.active_clients.setModel(list_table)
        self.active_clients.resizeColumnsToContents()

    # Открываем окно с настройками сервера
    def show_parameters(self):
        window = ConfigWindow(self)
        window.exec_()


class AllUsersWindow(QDialog):
    def __init__(self, parent=None):
        super(AllUsersWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Список всех пользователей')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # Лист с собственно историей
        self.table_list = QTableView(self)
        self.table_list.move(10, 10)
        self.table_list.setFixedSize(580, 620)

        self.show()


class UsersHistoryWindow(QDialog):
    def __init__(self, parent=None):
        super(UsersHistoryWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('История пользователей')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # Лист с собственно историей
        self.table_list = QTableView(self)
        self.table_list.move(10, 10)
        self.table_list.setFixedSize(580, 620)

        self.show()


# Формируем окно с настройками сервера
class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Настройки окна
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        # Надпись о файле базы данных:
        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Строка с путём базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути.
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        # Функция обработчик открытия окна выбора папки
        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # Метка с именем поля файла базы данных
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # Поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        # Метка с номером порта
        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        # Метка с напоминанием о пустом поле.
        self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        # Кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


def main(db):
    app = QApplication(sys.argv)
    main_window = MainWindow(db)
    main_window.statusBar().showMessage('Панель управления...')
    main_window.create_active_users()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # create_all_users_table()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.statusBar().showMessage('тестирование...')
    main_window.create_active_users()

    '''
    test_list = QStandardItemModel(main_window)  # табличная часть
    test_list.setHorizontalHeaderLabels(['Клиент', 'IP', 'Порт', 'Время подключения'])
    test_list.appendRow([QStandardItem('test'), QStandardItem('192.168.0.1'), QStandardItem('7777'),
                         QStandardItem('16:15:00')])
    main_window.active_clients.setModel(test_list)
    main_window.active_clients.resizeColumnsToContents()
    '''

    sys.exit(app.exec_())
