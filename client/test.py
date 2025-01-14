from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
)
import sys

class LoginWindow(QWidget):
    def __init__(self, on_continue):
        super().__init__()
        self.on_continue = on_continue

        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Welcome! Please click continue to proceed:")
        layout.addWidget(self.label)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.handle_continue)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)

    def handle_continue(self):
        self.on_continue()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        self.label = QLabel("Welcome to the main application!", self)
        self.label.setGeometry(50, 50, 300, 50)

        # Show the welcome window before displaying the main window
        self.login_window = LoginWindow(self.show_main_window)
        self.login_window.show()

    def show_main_window(self):
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
