import sys
import socketio
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel

# SocketIO client
sio = socketio.Client()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spotify Authentication App")
        self.setGeometry(100, 100, 400, 300)

        # Create a label to display messages from the server
        self.label = QLabel("Waiting for server message...", self)
        self.user_data_label = QLabel("User Data will appear here", self)

        # Create the button that will open the Spotify login page in a browser
        self.button = QPushButton("Login with Spotify", self)
        self.button.clicked.connect(self.open_spotify_login)

        # Set up layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.user_data_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect to the server
        sio.connect('http://localhost:5020')

        # Listen for the 'login_success' event
        sio.on('login_success', self.handle_login_success)

        # Listen for the 'user_data' event to update the UI with the user data
        sio.on('user_data', self.display_user_data)

    def open_spotify_login(self):
        # Open the Spotify login URL in the default web browser
        import webbrowser
        webbrowser.open('http://localhost:5020/login')

    def handle_login_success(self, data):
        # Update the label with the success message
        self.label.setText(data['message'])

    def display_user_data(self, data):
        # Update the label with the user data
        user = data['user']
        user_info = f"Name: {user['display_name']}\nEmail: {user['email']}\nID: {user['id']}"
        self.user_data_label.setText(user_info)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
