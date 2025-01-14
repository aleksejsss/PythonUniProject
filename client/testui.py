import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLineEdit, QLabel, QComboBox, QCheckBox, QRadioButton, QSpinBox, QSlider, QTabWidget, QTableWidget, QTableWidgetItem, QFormLayout, QStatusBar, QFrame
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt6.QtCore import Qt, QSize, QTimer, QDateTime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QGridLayout Example")
        self.setGeometry(100, 100, 1020, 760)
        
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
        artist_container_widget = QWidget()
        button_layout = QHBoxLayout()
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
            button_layout.addWidget(temp_box)
            
        artist_container_widget.setLayout(button_layout)
        artist_scroll_area.setWidget(artist_container_widget)
        main_content_layout.addWidget(artist_scroll_area)

        top_tracks = QLabel('Tavi mīļākie treki:')
        top_tracks.setObjectName('h1')
        main_content_layout.addWidget(top_tracks)
        
        track_scroll_area = QScrollArea()
        track_scroll_area.setWidgetResizable(True)
        track_container_widget = QWidget()
        button_layout = QHBoxLayout()
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
            button_layout.addWidget(temp_box)
            
        track_container_widget.setLayout(button_layout)
        track_scroll_area.setWidget(track_container_widget)
        main_content_layout.addWidget(track_scroll_area)
        
        main_layout.addLayout(content_bar)

        central_widget.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        with open("teststyles.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        print("Stylesheet file 'teststyles.qss' not found.")
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
