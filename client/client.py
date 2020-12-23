import sys
from datetime import datetime
from hashlib import sha256

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTabWidget, QListWidget, \
    QListWidgetItem, QDialog, QFormLayout, QLineEdit, QTextEdit, QDateTimeEdit, QErrorMessage

from server_connector import ServerConnector, SecurityError


class AuthorizationDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")

        self.id = None
        self.is_accepted = False

        self.setLayout(QVBoxLayout())

        self.id_field = QLineEdit()
        self.id_field.setPlaceholderText("ID")
        self.layout().addWidget(self.id_field)

        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Password")
        self.layout().addWidget(self.password_field)

        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.confirm)
        self.layout().addWidget(accept_button)

    @property
    def user_id(self):
        return self.id

    def confirm(self):
        try:
            self.id = int(self.id_field.text())
            self.is_accepted = True
        except ValueError:
            pass
        self.close()


class DataPanel(QTabWidget):

    def __init__(self, server: ServerConnector, message_func):
        super().__init__()

        self.server = server
        self.message_func = message_func

        self.free_breakages_widget = QListWidget()
        self.free_breakages_widget.itemDoubleClicked.connect(self.openBreakageWindow)

        self.my_breakages_widget = QListWidget()
        self.my_breakages_widget.itemDoubleClicked.connect(self.openBreakageWindow)

        self.breakages_in_work_widget = QListWidget()
        self.breakages_in_work_widget.itemDoubleClicked.connect(self.openBreakageWindow)

        self.update_data()

    def setEngineerMode(self):
        self.clear()
        self.addTab(self.free_breakages_widget, "Свободные поломки")
        self.addTab(self.my_breakages_widget, "Мои поломки")

    def setOperatorMode(self):
        self.clear()
        self.addTab(self.free_breakages_widget, "Свободные поломки")
        self.addTab(self.breakages_in_work_widget, "Поломки в работе")

    def setAdministratorMode(self):
        pass

    def update_data(self):
        self.free_breakages_widget.clear()
        self.my_breakages_widget.clear()
        self.breakages_in_work_widget.clear()
        for breakage in self.server.get_free_breakages():
            self.free_breakages_widget.addItem(BreakagesListItem(breakage))
        for breakage in self.server.get_taken_breakages():
            self.my_breakages_widget.addItem(BreakagesListItem(breakage))
        for breakage in self.server.get_breakages_in_work():
            self.breakages_in_work_widget.addItem(BreakagesListItem(breakage))

        if self.server.user_role == 'ADMIN':
            self.setAdministratorMode()
        elif self.server.user_role == 'ENGINEER':
            self.setEngineerMode()
        elif self.server.user_role == 'OPERATOR':
            self.setOperatorMode()

    def openBreakageWindow(self):
        window = BreakageWindow(self.sender().selectedItems()[0].data, self.server, self.message_func)
        window.exec()


class BreakagesListItem(QListWidgetItem):

    def __init__(self, breakage_dict):
        super().__init__()
        self.id = breakage_dict['id']
        self.data = breakage_dict
        self.setText(f"{breakage_dict['place']}\n{breakage_dict['description']}")


class BreakageWindow(QDialog):

    def __init__(self, data, server: ServerConnector, show_message_func):
        super().__init__()
        self.setWindowTitle(f"Поломка в {data['place']}")
        self.resize(300, 200)
        self.id = data['id']

        self.server = server
        self.message_func = show_message_func

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(QLabel(f"Место: {data['place']}"))
        self.layout().addWidget(QLabel(f"Время: {datetime.fromtimestamp(data['time']).strftime('%Y-%m-%d %H:%M')}"))
        self.layout().addWidget(QLabel(data['description']))

        if data in server.get_free_breakages():
            take_button = QPushButton("Взять поломку в работу")
            take_button.clicked.connect(self.take)
            self.layout().addWidget(take_button)
        else:
            fix_button = QPushButton("Поломка устранена")
            fix_button.clicked.connect(self.fix)
            self.layout().addWidget(fix_button)

    def take(self):
        if self.server.take_breakage(self.id):
            self.message_func("Поломка успешно взята в работу")
        else:
            self.message_func("Взять поломку в работу не удалось")
        self.close()

    def fix(self):
        self.server.fix_breakage(self.id)
        self.message_func("Уведомлено об успешном устранении поломки")
        self.close()


class NewBreakageDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.is_accepted = False

        self.setWindowTitle("Новая поломка")
        self.setLayout(QFormLayout())

        self.place_field = QLineEdit()
        self.layout().addRow("Место", self.place_field)

        self.time_field = QDateTimeEdit()
        self.time_field.setMaximumDateTime(datetime.now())
        self.layout().addRow("Время", self.time_field)

        self.description_field = QTextEdit()
        self.layout().addRow("Описание", self.description_field)

        accept_button = QPushButton("Ок")
        accept_button.clicked.connect(self.confirm)
        self.layout().addRow("Принять", accept_button)

    def confirm(self):
        if len(self.place) > 0 or len(self.description) > 0:
            self.is_accepted = True
        self.close()

    @property
    def place(self):
        return self.place_field.text()

    @property
    def time(self):
        return self.time_field.dateTime().toSecsSinceEpoch()

    @property
    def description(self):
        return self.description_field.toPlainText()


class MainWindow(QWidget):

    def __init__(self, server: ServerConnector):
        super().__init__()

        self.server = server
        self.server.add_view(self)

        self.setWindowTitle("Программа контроля поломок")
        self.setGeometry(700, 200, 500, 600)
        self.setLayout(QVBoxLayout())

        self.add_breakage_button = QPushButton("Добавить поломку")
        self.add_breakage_button.clicked.connect(self.addBreakage)
        self.layout().addWidget(self.add_breakage_button)

        self.breakages_panel = DataPanel(self.server, self.showStatus)
        self.server.add_view(self.breakages_panel)
        self.layout().addWidget(self.breakages_panel)

        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh)
        self.layout().addWidget(refresh_button)

        self.status_bar = QLabel()
        self.layout().addWidget(self.status_bar)

        self.server.update_data()

        self.showStatus("Готов к работе")

    def setEngineerMode(self):
        self.add_breakage_button.setVisible(False)

    def setOperatorMode(self):
        self.add_breakage_button.setVisible(True)

    def setAdministratorMode(self):
        pass

    def showStatus(self, status_message):
        self.status_bar.setText(status_message)

    def addBreakage(self):
        adding_dialog = NewBreakageDialog()
        adding_dialog.exec()
        if adding_dialog.is_accepted:
            if self.server.add_breakage(adding_dialog.place,
                                        adding_dialog.time,
                                        adding_dialog.description):
                self.showStatus(f"Поломка в {adding_dialog.place} успешно добавлена")

    def refresh(self):
        self.breakages_panel.update_data()
        self.showStatus("Обновлено")

    def update_data(self):
        if self.server.user_role == 'ADMIN':
            self.setAdministratorMode()
        elif self.server.user_role == 'ENGINEER':
            self.setEngineerMode()
        elif self.server.user_role == 'OPERATOR':
            self.setOperatorMode()


def main():
    app = QApplication(sys.argv)
    connector = ServerConnector("http://localhost", 5000)
    auth_dialog = AuthorizationDialog()
    auth_dialog.exec()
    if auth_dialog.is_accepted:
        try:
            connector.set_user(auth_dialog.user_id,
                               sha256(auth_dialog.password_field.text().encode('utf-8')).hexdigest())
        except SecurityError:
            error_box = QErrorMessage()
            error_box.showMessage("Check your credentials and try again!")
            error_box.setWindowTitle("Security error")
            error_box.exec()
            sys.exit(1)
        window = MainWindow(connector)
        window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
