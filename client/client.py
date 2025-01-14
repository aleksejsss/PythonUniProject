import sys
import socketio
import requests
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLineEdit, QLabel, QComboBox, QCheckBox, QRadioButton, QSpinBox, QSlider, QTabWidget, QTableWidget, QTableWidgetItem, QFormLayout, QStatusBar, QFrame
from PyQt6.QtGui import QImage, QPixmap

from PyQt6.QtGui import QDesktopServices
from PyQt5.QtCore import QFile, QTextStream

sio = socketio.Client()

user_data = None  # To store user data globally

def load_stylesheet(file_path):
    """Load the QSS stylesheet from a file."""
    file = QFile(file_path)
    if not file.open(QFile.ReadOnly | QFile.Text):
        print(f"Failed to open file: {file_path}")
        return ""
    stream = QTextStream(file)
    return stream.readAll()

class LoginWindow(QWidget):
    def __init__(self, on_authorized, on_guest):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 540, 760)

        self.layout = QVBoxLayout()

        self.label = QLabel("Choose how to continue:", self)
        self.layout.addWidget(self.label)

        self.auth_button = QPushButton("Continue with Spotify", self)
        self.auth_button.clicked.connect(on_authorized)
        self.layout.addWidget(self.auth_button)

        self.guest_button = QPushButton("Continue as Guest", self)
        self.guest_button.clicked.connect(on_guest)
        self.layout.addWidget(self.guest_button)

        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    user_data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 600, 500)

        self.label = QLabel("Awaiting user data...", self)
        self.setGeometry(100, 100, 1020, 760)

        self.client_sid = None

        self.initialize_socket()

        self.login_window = LoginWindow(self.request_authorization, self.continue_as_guest)
        self.login_window.show()

        self.user_data_signal.connect(self.update_ui)
        
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        top_bar = QWidget()
        top_bar.setObjectName("top_bar")
        top_bar_layout = QHBoxLayout()
        top_bar.setLayout(top_bar_layout)
        
        main_layout.addWidget(top_bar)
        
        content_bar = QHBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        main_content = QWidget()
        main_content.setObjectName("main_content")
        main_content_layout = QVBoxLayout()
        main_content.setLayout(main_content_layout)
        scroll_area.setWidget(main_content)
        content_bar.addWidget(scroll_area)

        top_artists = QLabel('Tavi mīļākie mūzīkas izpildītāji:')
        top_artists.setObjectName('h1')
        main_content_layout.addWidget(top_artists)
        
        artist_scroll_area = QScrollArea()
        artist_scroll_area.setWidgetResizable(True)
        self.artist_container_widget = QWidget()
        button_layout1 = QHBoxLayout()
        for i in range(1, 51):
            temp_box = QWidget()
            temp_box_layout = QVBoxLayout()
            temp_box.setObjectName('temp_box')
            
            temp_frame = QFrame()
            temp_frame.setObjectName('frame')
            temp_box_layout.addWidget(temp_frame)
            
            artist_title = QLabel(f"Artist {i}")
            artist_title.setObjectName('h2')
            temp_box_layout.addWidget(artist_title)
            
            artist_generes = QLabel('genere genere')
            artist_generes.setObjectName('h3')
            temp_box_layout.addWidget(artist_generes)
            
            temp_box.setLayout(temp_box_layout)
            button_layout1.addWidget(temp_box)
            
        self.artist_container_widget.setLayout(button_layout1)
        self.artist_container_widget.setObjectName('artist_container_widget')
        artist_scroll_area.setWidget(self.artist_container_widget)
        main_content_layout.addWidget(artist_scroll_area)

        top_tracks = QLabel('Tavi mīļākie treki:')
        top_tracks.setObjectName('h1')
        main_content_layout.addWidget(top_tracks)
        
        track_scroll_area = QScrollArea()
        track_scroll_area.setWidgetResizable(True)
        self.track_container_widget = QWidget()
        button_layout2 = QHBoxLayout()
        for i in range(1, 51):
            temp_box = QWidget()
            temp_box_layout = QVBoxLayout()
            temp_box.setObjectName('temp_box')
            
            temp_frame = QFrame()
            temp_frame.setObjectName('frame')
            temp_box_layout.addWidget(temp_frame)
            
            artist_title = QLabel(f"Track {i}")
            artist_title.setObjectName('h2')
            temp_box_layout.addWidget(artist_title)
            
            artist_generes = QLabel('Album')
            artist_generes.setObjectName('h3')
            temp_box_layout.addWidget(artist_generes)
            
            temp_box.setLayout(temp_box_layout)
            button_layout2.addWidget(temp_box)
            
        self.track_container_widget.setLayout(button_layout2)
        track_scroll_area.setWidget(self.track_container_widget)
        main_content_layout.addWidget(track_scroll_area)
        
        main_layout.addLayout(content_bar)

        central_widget.setLayout(main_layout)


    def initialize_socket(self):

        @sio.event
        def connect():
            print("Connected to the server")

        @sio.event
        def connect_error(data):
            print(f"Connection failed: {data}")

        @sio.on('connect_success')
        def on_connect_success(data):
            self.client_sid = data['assigned_sid']
            print(f"Server response: {data['message']} (SID: {self.client_sid})")

        @sio.event
        def disconnect():
            print('Disconnected from the server')

        @sio.on('authorization_link')
        def authorize(data):
            print("Received authorization link")
            print(f"Auth URL: {data['auth_url']}")
            QDesktopServices.openUrl(QUrl(data['auth_url']))

        @sio.on('welcome_back')
        def initial_load(data):
            global user_data
            user_data = data
            print("Welcome back data received")
            self.user_data_signal.emit(user_data)

        sio.connect('http://localhost:5020')

    def request_authorization(self):
        if sio.connected:
            message_data = {
                'client_sid': self.client_sid
            }
            sio.emit('request_authorization', message_data)
        else:
            print("Not connected to the server.")

    def continue_as_guest(self):
        print("Continuing as guest (No authorization)")
        self.login_window.close()
        self.show()

    def update_ui(self, user_data):
        print('Updating ui')
        new_track_layout = QHBoxLayout()
        new_artist_layout = QHBoxLayout()
        track_data = user_data['track_data']
        
        artist_data = user_data['artist_data']
        
        for artist in artist_data['items']:
            temp_box = QWidget()
            temp_box_layout = QVBoxLayout()
            temp_box.setObjectName('temp_box')
            if artist['images']:
                response = requests.get(artist['images'][1]['url'])
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    pixmap = pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                temp_frame = QLabel()
                temp_frame.setPixmap(pixmap)
            else:
                temp_frame = QFrame()
            
            temp_frame.setObjectName('frame')
            temp_box_layout.addWidget(temp_frame)
            
            artist_title = QLabel(artist['name'])
            artist_title.setObjectName('h2')
            temp_box_layout.addWidget(artist_title)
            
            if artist['genres']:
                artist_generes = QLabel(artist['genres'][0])
                artist_generes.setObjectName('h3')
                temp_box_layout.addWidget(artist_generes)
            
            temp_box.setLayout(temp_box_layout)
            new_artist_layout.addWidget(temp_box)
            
        old_layout = self.artist_container_widget.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self.artist_container_widget.setLayout(new_artist_layout)
        
        for track in track_data['items']:
            temp_box = QWidget()
            temp_box_layout = QVBoxLayout()
            temp_box.setObjectName('temp_box')
            if track['album']['images']:
                response = requests.get(track['album']['images'][1]['url'])
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    pixmap = pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                temp_frame = QLabel()
                temp_frame.setPixmap(pixmap)
            else:
                temp_frame = QFrame()
            
            temp_frame.setObjectName('frame')
            temp_box_layout.addWidget(temp_frame)
            
            artist_title = QLabel(track['name'])
            artist_title.setObjectName('h2')
            temp_box_layout.addWidget(artist_title)
            
            artist_generes = QLabel(track['album']['name'])
            artist_generes.setObjectName('h3')
            temp_box_layout.addWidget(artist_generes)
            
            temp_box.setLayout(temp_box_layout)
            new_track_layout.addWidget(temp_box)
            
        old_layout = self.track_container_widget.layout()
        if old_layout:
        # Remove the old layout from the container
            QWidget().setLayout(old_layout)  # This removes the layout
            
        self.track_container_widget.setLayout(new_track_layout)
        
        self.login_window.close()
        self.show()
        


    def set_profile_image(self, image_url):
        """Set profile image in the UI."""
        image = QImage()
        if image.load(image_url):
            pixmap = QPixmap(image)
            self.profile_image.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        sio.disconnect()
        event.accept()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    stylesheet = load_stylesheet("styles.qss")
    if stylesheet:
        app.setStyleSheet(stylesheet)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
