import sys
import socketio
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class MainWindow(QWidget):

    server = 'http://localhost:5020/'

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Spotify Login')
        self.load_styles()
        self.init_ui()
        
        # SocketIO client setup
        self.sio = socketio.Client()
        self.sio.connect(self.server)
        self.sio.on('token_info', self.on_token_info)

    def load_styles(self):
        try:
            with open("styles.qss", "r") as f:
                styles = f.read()
            self.setStyleSheet(styles)
        except FileNotFoundError:
            print("Style sheet not found!")

    def init_ui(self):
        self.label = QLabel("Click the button to continue with Spotify", self)
        btn_spotify = QPushButton('Continue with Spotify')
        btn_spotify.clicked.connect(self.on_spotify)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(btn_spotify)
        self.setLayout(layout)

    def on_spotify(self):
        """ Open the Spotify login URL in the browser. """
        url = self.server + "login"
        QDesktopServices.openUrl(QUrl(url))
        print("Spotify button clicked")

    def on_token_info(self, token_info):
        """Handles the token info sent from the server."""
        access_token = token_info.get('access_token')
        if access_token:
            self.label.setText(f"Token received: {access_token}")
        else:
            self.label.setText("Failed to retrieve token")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
