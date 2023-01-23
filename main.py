import base64
import hashlib
import json
import os
import re

import psutil
import win32api
import win32con
import wmi
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD2
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QApplication
from screeninfo import get_monitors
from winreg import *


# Добавление нового пользователя с пустым паролем от имени администратора
def add_new_user():
    new_user.show()


# Збір інформації про ПК
def info_about_pc():
    file = open('pc_info.txt', 'w')
    length = 17
    info_str = ''

    # Ім'я користувача
    user_name = win32api.GetUserName()
    info_str += ('user_name'.ljust(length) + f': {user_name}\n')

    # Ім'я комп'ютера
    pc_name = win32api.GetComputerName()
    info_str += ('pc_name'.ljust(length) + f': {pc_name}\n')

    # Шлях до папки з ОС Windows
    window_directory = win32api.GetWindowsDirectory()
    info_str += ('window_directory'.ljust(length) + f': {window_directory}\n')

    # Шлях до папки з системними файлами ОС Windows
    system_directory = win32api.GetSystemDirectory()
    info_str += ('system_directory'.ljust(length) + f': {system_directory}\n')

    # Кількість кнопок миші
    mouse_buttons = win32con.SM_CMOUSEBUTTONS
    info_str += ('mouse_buttons'.ljust(length) + f': {mouse_buttons}\n')

    # Висота екрану
    screen_height = get_monitors()[0].height
    info_str += ('screen_height'.ljust(length) + f': {screen_height}\n')

    # Набір дискових пристроїв
    disk_info = ''
    for i in psutil.disk_partitions():
        disk_info += i.device + ' ' + str(psutil.disk_usage(i.device).total) + '; '

    info_str += ('disk_info'.ljust(length) + f': {disk_info}\n')

    # Серійний номер
    for item in wmi.WMI().CIM_PhysicalMedia():
        serial_number = str(item).split('\"')[1].split()[0]
        info_str += ('serial_number'.ljust(length) + f': {serial_number}\n')

    # Хешування інформації
    info_str = hashlib.sha512(info_str.encode()).hexdigest()
    file.write(info_str)
    file.close()
    return info_str


# Перевірка доступу
def isAccess(name, signature):
    key = OpenKey(HKEY_CURRENT_USER, r'Software\Shkepast', 0, KEY_ALL_ACCESS)
    key = QueryValueEx(key, name)[0]
    if key == signature:
        return True
    else:
        return False


class Application(QMainWindow):
    def __init__(self):
        super().__init__()

        self.UsersList = None
        self.is_correct = None
        self.welcome_label = QLabel(self)
        self.welcome_label.setGeometry(10, 5, 1200, 50)
        self.welcome_label.setStyleSheet("border: 1px solid black")
        self.welcome_label.setFont(QFont('Arial', 18))
        self.welcome_label.setVisible(False)

        self.label_info = QLabel(self)
        self.label_info.setGeometry(10, 60, 740, 50)
        self.label_info.setStyleSheet("border: 1px solid black")
        self.label_info.setFont(QFont('Arial', 18))
        self.label_info.setText('Info about Users:')
        self.label_info.setVisible(False)

        self.label_choose = QLabel(self)
        self.label_choose.setGeometry(760, 60, 200, 50)
        self.label_choose.setStyleSheet("border: 1px solid black")
        self.label_choose.setFont(QFont('Arial', 14))
        self.label_choose.setText('Choose to change:')
        self.label_choose.setVisible(False)

        self.login = QLineEdit(self)
        self.login.setGeometry(90, 20, 220, 40)
        self.login.setPlaceholderText('login...')
        self.login.textChanged.connect(self.update_is_correct)
        self.login.setVisible(False)

        self.password = QLineEdit(self)
        self.password.setGeometry(90, 70, 220, 40)
        self.password.setPlaceholderText('password...')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setVisible(False)

        self.password_confirm = QLineEdit(self)
        self.password_confirm.setGeometry(90, 120, 220, 40)
        self.password_confirm.setPlaceholderText('confirm password...')
        self.password_confirm.setEchoMode(QLineEdit.Password)
        self.password_confirm.setVisible(False)

        self.sign_in_button = QPushButton('Sign In', self)
        self.sign_in_button.setGeometry(90, 170, 100, 40)
        self.sign_in_button.clicked.connect(self.sign_in_user)
        self.sign_in_button.setVisible(False)

        self.sign_up_button = QPushButton('Sign Up', self)
        self.sign_up_button.setGeometry(210, 170, 100, 40)
        self.sign_up_button.clicked.connect(self.sign_up_user)
        self.sign_up_button.setVisible(False)

        self.log_out_button = QPushButton('Log out', self)
        self.log_out_button.setGeometry(1100, 620, 100, 40)
        self.log_out_button.setStyleSheet('background-color: red')
        self.log_out_button.clicked.connect(self.log_out_user)

        self.info_about_APP_button = QPushButton('Info about APP', self)
        self.info_about_APP_button.setGeometry(970, 570, 240, 40)
        self.info_about_APP_button.clicked.connect(self.info_about_APP)

        self.change_password_button = QPushButton('Change Password', self)
        self.change_password_button.setGeometry(970, 620, 120, 40)
        self.change_password_button.clicked.connect(self.init_change_password_ui)

        self.save_new_password_button = QPushButton('Save', self)
        self.save_new_password_button.setGeometry(210, 170, 100, 40)
        self.save_new_password_button.clicked.connect(self.save_new_password)
        self.save_new_password_button.setStyleSheet('background-color: green')
        self.save_new_password_button.setVisible(False)

        self.cancel_changed_button = QPushButton('Cancel', self)
        self.cancel_changed_button.setGeometry(90, 170, 100, 40)
        self.cancel_changed_button.clicked.connect(self.cancel_changed)
        self.cancel_changed_button.setStyleSheet('background-color: red')
        self.cancel_changed_button.setVisible(False)

        self.old_password = QLineEdit(self)
        self.old_password.setGeometry(90, 20, 220, 40)
        self.old_password.setPlaceholderText('old password...')
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setVisible(False)

        self.new_password = QLineEdit(self)
        self.new_password.setGeometry(90, 70, 220, 40)
        self.new_password.setPlaceholderText('new password...')
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setVisible(False)

        self.new_password_confirm = QLineEdit(self)
        self.new_password_confirm.setGeometry(90, 120, 220, 40)
        self.new_password_confirm.setPlaceholderText('confirm new password...')
        self.new_password_confirm.setEchoMode(QLineEdit.Password)
        self.new_password_confirm.setVisible(False)

        self.user_list_widget = QListWidget(self)
        self.user_list_widget.setGeometry(760, 110, 200, 550)
        self.user_list_widget.setStyleSheet("border: 1px solid black")
        self.user_list_widget.setVisible(False)

        self.user_list_widget_view = QListWidget(self)
        self.user_list_widget_view.setGeometry(10, 110, 740, 550)
        self.user_list_widget_view.setStyleSheet("border: 1px solid black")
        self.user_list_widget_view.setVisible(False)

        self.change_current_login_button = QPushButton('Change login', self)
        self.change_current_login_button.setGeometry(970, 110, 240, 40)
        self.change_current_login_button.clicked.connect(self.change_current_login)

        self.change_current_password_button = QPushButton('Change password', self)
        self.change_current_password_button.setGeometry(970, 160, 240, 40)
        self.change_current_password_button.clicked.connect(self.change_current_password)

        self.change_current_is_blocked_button = QPushButton('Change is_blocked', self)
        self.change_current_is_blocked_button.setGeometry(970, 210, 240, 40)
        self.change_current_is_blocked_button.clicked.connect(self.change_current_is_blocked)

        self.change_current_pass_rest_button = QPushButton('Change pass_rest', self)
        self.change_current_pass_rest_button.setGeometry(970, 260, 240, 40)
        self.change_current_pass_rest_button.clicked.connect(self.change_current_pass_rest)

        self.add_new_user_button = QPushButton('Add new user', self)
        self.add_new_user_button.setGeometry(970, 310, 240, 40)
        self.add_new_user_button.clicked.connect(add_new_user)

        self.msg = QMessageBox()

        self.password_length = 6
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        self.decrypted_data = None
        self.key_value = None
        self.setWindowTitle("Access")
        self.setGeometry(760, 415, 400, 150)

        self.key = QLineEdit(self)
        self.key.setGeometry(90, 30, 220, 40)
        self.key.setPlaceholderText('Access key...')

        self.get_access_button = QPushButton('Get access', self)
        self.get_access_button.setGeometry(90, 80, 220, 40)
        self.get_access_button.clicked.connect(self.getAccess)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        self.current_item = None
        self.user_list_widget.clicked.connect(self.choose_item)

    def getAccess(self):
        self.key_value = self.key.text()
        with open('UsersList.cpr', 'r')as file:
            file_data = file
            encrypted_data = ''
            for _ in file_data:
                encrypted_data += _
        try:
            self.UsersList = json.loads(decrypt(self.key_value, encrypted_data))
            with open('UsersList.json', 'w') as file:
                file.write(decrypt(self.key_value, encrypted_data))
                file.close()
            self.init_sign_up_ui()
            self.update_list_widget()

        except Exception as ex:
            print(ex)
            warnMsg = QMessageBox()
            warnMsg.setText('Incorrect Key')
            warnMsg.setWindowTitle('Warning')
            warnMsg.setIcon(QMessageBox.Warning)
            warnMsg.exec_()

    # Інформація про застосунок
    def info_about_APP(self):
        self.show_msg('Даний застосунок розробив:\n'
                      'Студент гр БС-93, Шкепаст М. В.\n'
                      'Завдання (Варіант 21):\n'
                      '21.Наявність латинських букв, символів кирилиці, цифр і знаків арифметичних операцій.')

    #  Обновление списка пользователей
    def update_list_widget(self):
        self.user_list_widget.clear()
        self.user_list_widget_view.clear()
        for user in self.UsersList[1:]:
            self.user_list_widget.addItem(user['login'])
            self.user_list_widget_view.addItem(json.dumps(user, indent=4))

    # Выбор объекта по логину
    def choose_item(self):
        self.current_item = self.user_list_widget.currentItem().text()

    # Обновление значения is_correct
    def update_is_correct(self):
        self.is_correct = 0

    # Инициализация окна регистрации/входа
    def init_sign_up_ui(self):
        self.setWindowTitle("Sign up")
        self.setGeometry(760, 415, 400, 250)
        self.login.setVisible(True)
        self.password.setVisible(True)
        self.sign_in_button.setVisible(True)
        self.sign_up_button.setVisible(True)
        self.login.setText('')
        self.password.setText('')

        self.key.setVisible(False)
        self.get_access_button.setVisible(False)
        self.welcome_label.setVisible(False)
        self.log_out_button.setVisible(False)
        self.password_confirm.setVisible(False)
        self.old_password.setVisible(False)
        self.new_password.setVisible(False)
        self.new_password_confirm.setVisible(False)
        self.save_new_password_button.setVisible(False)
        self.cancel_changed_button.setVisible(False)
        self.change_password_button.setVisible(False)
        self.user_list_widget.setVisible(False)
        self.change_current_login_button.setVisible(False)
        self.change_current_password_button.setVisible(False)
        self.change_current_is_blocked_button.setVisible(False)
        self.change_current_pass_rest_button.setVisible(False)
        self.add_new_user_button.setVisible(False)
        self.user_list_widget_view.setVisible(False)
        self.label_info.setVisible(False)
        self.label_choose.setVisible(False)
        self.info_about_APP_button.setVisible(False)

        self.show()

    # Инициализация главного окна приложения
    def init_main_ui(self):
        self.setWindowTitle("Main")
        self.setGeometry(350, 200, 1220, 680)
        self.login.setVisible(False)
        self.password_confirm.setVisible(False)
        self.password.setVisible(False)
        self.sign_in_button.setVisible(False)
        self.sign_up_button.setVisible(False)
        self.old_password.setVisible(False)
        self.new_password.setVisible(False)
        self.new_password_confirm.setVisible(False)
        self.save_new_password_button.setVisible(False)
        self.cancel_changed_button.setVisible(False)

        self.welcome_label.setVisible(True)
        self.log_out_button.setVisible(True)
        self.change_password_button.setVisible(True)
        self.user_list_widget.setVisible(True)
        self.change_current_login_button.setVisible(True)
        self.change_current_password_button.setVisible(True)
        self.change_current_is_blocked_button.setVisible(True)
        self.change_current_pass_rest_button.setVisible(True)
        self.add_new_user_button.setVisible(True)
        self.user_list_widget_view.setVisible(True)
        self.info_about_APP_button.setVisible(True)
        self.welcome_label.setText(f'Welcome to {self.login.text()}\'s account!')
        self.admin_enabled(self.login.text())

        self.show()

    # Инициализация окна смены пароля для обычного пользователя
    def init_change_password_ui(self):
        self.setWindowTitle(f"Change password for {self.login.text()}")
        self.setGeometry(760, 415, 400, 250)
        self.login.setVisible(False)
        self.password.setVisible(False)
        self.sign_in_button.setVisible(False)
        self.sign_up_button.setVisible(False)
        self.welcome_label.setVisible(False)
        self.log_out_button.setVisible(False)
        self.password_confirm.setVisible(False)
        self.change_password_button.setVisible(False)
        self.user_list_widget.setVisible(False)
        self.change_current_login_button.setVisible(False)
        self.change_current_password_button.setVisible(False)
        self.change_current_is_blocked_button.setVisible(False)
        self.change_current_pass_rest_button.setVisible(False)
        self.add_new_user_button.setVisible(False)
        self.user_list_widget_view.setVisible(False)
        self.label_info.setVisible(False)
        self.label_choose.setVisible(False)
        self.info_about_APP_button.setVisible(False)

        self.old_password.setVisible(True)
        self.new_password.setVisible(True)
        self.new_password_confirm.setVisible(True)
        self.save_new_password_button.setVisible(True)
        self.cancel_changed_button.setVisible(True)

        self.show()

    # Сохранение нового пароля для обычного пользователя
    def save_new_password(self):
        if str(self.old_password.text()) == self.find_by_login(self.login.text())['password']:
            if self.old_password.text() != self.new_password.text():
                if self.new_password.text() == self.new_password_confirm.text():
                    if self.find_by_login(self.login.text())['password_restriction']:
                        if self.is_password_correct(self.new_password.text()):
                            self.find_by_login(self.login.text())['password'] = self.new_password.text()
                            self.show_msg(f'{self.login.text()}\'s password has been successfully changed')
                            self.cancel_changed()
                        else:
                            self.show_msg('Invalid value!\n'
                                          'The password must contain:\n'
                                          '* latin letters\n'
                                          '* cyrillic characters\n'
                                          '* numbers\n'
                                          '* signs of arithmetic operations.(-+*/%)')
                    else:
                        self.find_by_login(self.login.text())['password'] = self.new_password.text()
                        self.show_msg(f'{self.login.text()}\'s password has been successfully changed')
                        self.cancel_changed()
                else:
                    self.show_msg('The new passwords do not match')
            else:
                self.show_msg('The new password is the same as the previous one')
        else:
            self.show_msg('The old password is wrong')

    # Отмена смены пароля
    def cancel_changed(self):
        self.old_password.setText('')
        self.new_password.setText('')
        self.new_password_confirm.setText('')
        self.init_main_ui()

    # Вход в уже существующий аккаунт
    def sign_in_user(self):

        if self.find_by_login(self.login.text()):
            if not self.find_by_login(self.login.text())['is_blocked']:
                if self.password.text() == self.find_by_login(self.login.text())['password']:
                    self.init_main_ui()
                else:
                    self.is_correct += 1
                    if self.is_correct >= 3:
                        self.find_by_login(self.login.text())['is_blocked'] = True
                    self.show_msg(f'Incorrect login or password\n'
                                  f'Attempts left: {3 - self.is_correct}')
            else:
                self.show_msg('The user with this login is blocked')
        else:
            self.show_msg('No user with this login is registered!')

    # Регистрация нового пользователя
    def sign_up_user(self):
        if not self.find_by_login(self.login.text()):
            if len(self.login.text()) >= 3:
                if self.password_confirm.isVisible():

                    if self.password.text() == self.password_confirm.text():
                        self.init_main_ui()
                        self.UsersList.append({'login': self.login.text(),
                                               'password': self.password.text(),
                                               'is_blocked': False,
                                               'password_restriction': False})

                        self.show_msg('A new user is successfully registered')
                        self.login.setText('')
                        self.password.setText('')
                        self.password_confirm.setText('')
                    else:
                        self.show_msg('Confirm your password')

                else:
                    self.password_confirm.setVisible(True)
            else:
                self.show_msg('Minimum login length 3 characters')
        else:
            self.show_msg('A user with this login already exists')
            self.password_confirm.setVisible(False)

    # Выход из главного окна в окно регистрации/входа
    def log_out_user(self):
        self.init_sign_up_ui()

    # Сохранение данных в файл
    def save_file(self):
        with open('UsersList.json', 'w') as file:
            json.dump(self.UsersList, file, indent=4)

    # Функция вызыващая уведомления
    def show_msg(self, text):
        self.msg.setWindowTitle(" ")
        self.msg.setText(text)
        self.msg.exec_()

    # Проверка пароля
    def is_password_correct(self, password):
        if bool(re.search("[+*%/-]", password) and re.search("\d", password) and re.search("[a-zA-Z]", password)
                and re.search("[а-яА-Я]", password) and len(password) >= self.password_length):
            return True
        else:
            return False

    # Поиск пользователя по имени аккаунта
    def find_by_login(self, login):
        for i in range(len(self.UsersList)):
            if login == self.UsersList[i]['login']:
                return self.UsersList[i]
        return 0

    # Запуск главного окна программы от имени администратора или обычного пользователя
    def admin_enabled(self, name):
        if name == 'ADMIN':
            self.user_list_widget.setDisabled(False)
            self.change_current_login_button.setDisabled(False)
            self.change_current_password_button.setDisabled(False)
            self.change_current_is_blocked_button.setDisabled(False)
            self.change_current_pass_rest_button.setDisabled(False)
            self.add_new_user_button.setDisabled(False)
            self.user_list_widget_view.setDisabled(False)
            self.label_info.setVisible(True)
            self.label_choose.setVisible(True)
            self.update_list_widget()

        else:
            self.user_list_widget.setDisabled(True)
            self.change_current_login_button.setDisabled(True)
            self.change_current_password_button.setDisabled(True)
            self.change_current_is_blocked_button.setDisabled(True)
            self.change_current_pass_rest_button.setDisabled(True)
            self.add_new_user_button.setDisabled(True)
            self.user_list_widget_view.setDisabled(True)
            self.label_info.setVisible(False)
            self.label_choose.setVisible(False)
            self.user_list_widget_view.clear()
            self.user_list_widget.clear()

    # Смена логина выбраного пользователя от имени администратора
    def change_current_login(self):

        if self.current_item:
            new_login.new_login.setText('')
            new_login.setWindowTitle(f'Change login for {self.current_item}')
            new_login.show()
        else:
            self.show_msg('Select a user!')

    # Смена пароля выбраного пользователя от имени администратора
    def change_current_password(self):

        if self.current_item:
            new_password.password.setText('')
            new_password.setWindowTitle(f'Change password for {self.current_item}')
            new_password.show()
        else:
            self.show_msg('Select a user!')

    # Смена блокировки аккаунта выбраного пользователя от имени администратора
    def change_current_is_blocked(self):

        if self.current_item:
            new_is_blocked.is_blocked.setText('')
            new_is_blocked.setWindowTitle(f'Change is_blocked for {self.current_item}')
            new_is_blocked.is_blocked.setPlaceholderText(
                f'Current value: {self.find_by_login(self.current_item)["is_blocked"]}')
            new_is_blocked.show()
        else:
            self.show_msg('Select a user!')

    # Смена проверки пароля выбраного пользователя от имени администратора
    def change_current_pass_rest(self):

        if self.current_item:
            new_pass_rest.pass_rest.setText('')
            new_pass_rest.setWindowTitle(f'Change pass_rest for {self.current_item}')
            new_pass_rest.pass_rest.setPlaceholderText(
                f'Current value: {self.find_by_login(self.current_item)["password_restriction"]}')
            new_pass_rest.show()
        else:
            self.show_msg('Select a user!')

    # Сохранение файла при закрытии
    def closeEvent(self, event):
        try:
            close_win.show()

        except Exception as ex:
            print(ex)


# Класс окна "Добавление нового пользователя"
class AddNewUser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.login = QLineEdit(self)
        self.login.setGeometry(90, 70, 220, 40)
        self.login.setPlaceholderText('Enter new login...')

        self.save_new_login_button = QPushButton('Save', self)
        self.save_new_login_button.setGeometry(210, 170, 100, 40)
        self.save_new_login_button.setStyleSheet('background-color: green')
        self.save_new_login_button.clicked.connect(self.save_new_login)

        self.cancel_saving_button = QPushButton('Cancel', self)
        self.cancel_saving_button.setGeometry(90, 170, 100, 40)
        self.cancel_saving_button.setStyleSheet('background-color: red')
        self.cancel_saving_button.clicked.connect(self.close)

        self.initUI()

    def initUI(self):
        self.login.setText('')
        self.setGeometry(760, 415, 400, 250)
        self.setWindowTitle(f'Creating new user')

    def save_new_login(self):
        window.UsersList.append({'login': self.login.text(),
                                 'password': '',
                                 'is_blocked': False,
                                 'password_restriction': False})
        window.update_list_widget()
        self.close()


# Класс окна "Изменение пароля для выбраного пользователя"
class AddNewPassword(QMainWindow):
    def __init__(self):
        super().__init__()
        self.password = QLineEdit(self)
        self.password.setGeometry(90, 70, 220, 40)
        self.password.setPlaceholderText('Enter new password...')

        self.save_new_password_button = QPushButton('Save', self)
        self.save_new_password_button.setGeometry(210, 170, 100, 40)
        self.save_new_password_button.setStyleSheet('background-color: green')
        self.save_new_password_button.clicked.connect(self.save_new_password)

        self.cancel_saving_button = QPushButton('Cancel', self)
        self.cancel_saving_button.setGeometry(90, 170, 100, 40)
        self.cancel_saving_button.setStyleSheet('background-color: red')
        self.cancel_saving_button.clicked.connect(self.close)

        self.initUI()

    def initUI(self):
        self.password.setText('')
        self.setGeometry(760, 415, 400, 250)
        self.setWindowTitle(f'Change password for {window.current_item}')

    def save_new_password(self):

        if window.find_by_login(window.current_item)['password_restriction']:
            if window.is_password_correct(self.password.text()):
                window.find_by_login(window.current_item)['password'] = self.password.text()

            else:
                window.show_msg('Invalid password!')
        else:
            window.find_by_login(window.current_item)['password'] = self.password.text()

        window.update_list_widget()
        self.close()


# Класс окна "Изменение логина дл выбраного пользователя"
class AddNewLogin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.new_login = QLineEdit(self)
        self.new_login.setGeometry(90, 70, 220, 40)
        self.new_login.setPlaceholderText('Enter new login...')

        self.save_new_login_button = QPushButton('Save', self)
        self.save_new_login_button.setGeometry(210, 170, 100, 40)
        self.save_new_login_button.setStyleSheet('background-color: green')
        self.save_new_login_button.clicked.connect(self.save_new_login)

        self.cancel_saving_button = QPushButton('Cancel', self)
        self.cancel_saving_button.setGeometry(90, 170, 100, 40)
        self.cancel_saving_button.setStyleSheet('background-color: red')
        self.cancel_saving_button.clicked.connect(self.close)

        self.initUI()

    def initUI(self):
        self.new_login.setText('')
        self.setGeometry(760, 415, 400, 250)
        self.setWindowTitle(f'Change login for {window.current_item}')

    def save_new_login(self):
        window.find_by_login(window.current_item)['login'] = self.new_login.text()
        window.update_list_widget()
        self.close()


# Класс окна "Изменение значения блокировки аккаунта для выбраного пользователя"
class AddNewIsBlocked(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_blocked = QLineEdit(self)
        self.is_blocked.setGeometry(90, 70, 220, 40)

        self.save_new_is_blocked_button = QPushButton('Save', self)
        self.save_new_is_blocked_button.setGeometry(210, 170, 100, 40)
        self.save_new_is_blocked_button.setStyleSheet('background-color: green')
        self.save_new_is_blocked_button.clicked.connect(self.save_new_is_blocked)

        self.cancel_saving_button = QPushButton('Cancel', self)
        self.cancel_saving_button.setGeometry(90, 170, 100, 40)
        self.cancel_saving_button.setStyleSheet('background-color: red')
        self.cancel_saving_button.clicked.connect(self.close)

        self.initUI()

    def initUI(self):
        self.is_blocked.setText('')
        self.setGeometry(760, 415, 400, 250)
        self.setWindowTitle(f'Change is_blocked for {window.current_item}')

    def save_new_is_blocked(self):

        if self.is_blocked.text() == 'True':
            window.find_by_login(window.current_item)['is_blocked'] = True

        elif self.is_blocked.text() == 'False':
            window.find_by_login(window.current_item)['is_blocked'] = False

        else:
            window.show_msg('Invalid value\nType True or False')
        window.update_list_widget()
        self.close()


# Класс окна "Изменение значения проверки пароля для выбраного пользователя"
class AddNewPassRest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.pass_rest = QLineEdit(self)
        self.pass_rest.setGeometry(90, 70, 220, 40)
        self.pass_rest.setPlaceholderText(f'Ture/False')

        self.save_new_pass_rest_button = QPushButton('Save', self)
        self.save_new_pass_rest_button.setGeometry(210, 170, 100, 40)
        self.save_new_pass_rest_button.setStyleSheet('background-color: green')
        self.save_new_pass_rest_button.clicked.connect(self.save_new_pass_rest)

        self.cancel_saving_button = QPushButton('Cancel', self)
        self.cancel_saving_button.setGeometry(90, 170, 100, 40)
        self.cancel_saving_button.setStyleSheet('background-color: red')
        self.cancel_saving_button.clicked.connect(self.close)

        self.initUI()

    def initUI(self):
        self.pass_rest.setText('')
        self.setGeometry(760, 415, 400, 250)
        self.setWindowTitle(f'Change pass_rest for {window.current_item}')

    def save_new_pass_rest(self):
        if self.pass_rest.text() == 'True':
            window.find_by_login(window.current_item)['password_restriction'] = True

        elif self.pass_rest.text() == 'False':
            window.find_by_login(window.current_item)['password_restriction'] = False

        else:
            window.show_msg('Invalid value.\nType True or False')
        window.update_list_widget()
        self.close()


class EncryptFile(QMainWindow):
    def __init__(self):
        super().__init__()
        self.decrypted_data = None
        self.key_value = None
        self.setWindowTitle("Encrypt")
        self.setGeometry(760, 415, 400, 150)

        self.key = QLineEdit(self)
        self.key.setGeometry(90, 30, 220, 40)
        self.key.setPlaceholderText('Access key...')

        self.get_encrypt_button = QPushButton('Encrypt', self)
        self.get_encrypt_button.setGeometry(90, 80, 220, 40)
        self.get_encrypt_button.clicked.connect(self.encrypt_file)

    def encrypt_file(self):
        key = self.key.text()
        data = encrypt(key, json.dumps(window.UsersList, indent=4))
        with open('UsersList.cpr', 'w') as file:
            file.write(data)
            file.close()
        os.remove('UsersList.json')
        self.close()


def encrypt(keyStr, text):
    private_key = MD2.new(keyStr.encode()).digest()
    rem = len(text) % 16
    padded = str.encode(text) + (b'\0' * (16 - rem)) if rem > 0 else str.encode(text)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CFB, iv, segment_size=128)
    enc = cipher.encrypt(padded)[:len(text)]
    return base64.b64encode(iv + enc).decode()


def decrypt(keyStr, text):
    private_key = MD2.new(keyStr.encode()).digest()
    text = base64.b64decode(text)
    iv, value = text[:16], text[16:]
    rem = len(value) % 16
    padded = value + (b'\0' * (16 - rem)) if rem > 0 else value
    cipher = AES.new(private_key, AES.MODE_CFB, iv, segment_size=128)
    return (cipher.decrypt(padded)[:len(value)]).decode()


def main():
    global new_login, new_password, new_is_blocked, new_pass_rest, new_user, window, close_win
    signature = info_about_pc()
    try:
        if isAccess(win32api.GetUserName(), signature):
            app = QApplication([])

            app.setStyle('Fusion')
            window = Application()
            new_login = AddNewLogin()
            new_password = AddNewPassword()
            new_is_blocked = AddNewIsBlocked()
            new_pass_rest = AddNewPassRest()
            new_user = AddNewUser()
            close_win = EncryptFile()
            window.show()
            app.exec_()
        else:
            print("You don't have permission")
            _ = input('Press Enter for close...')

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
