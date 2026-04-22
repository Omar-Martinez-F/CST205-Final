from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QMessageBox
)
# Build main ui here 
# Firt ui implention should be simple dropdown,buttons ect
# To make this project more unique we should add more features to mess with audio files later

import sys
import song

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Song Generator")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title_label = QLabel("Make a Song")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter song title")
        layout.addWidget(self.title_input)

        channel_label = QLabel("Choose channels")
        layout.addWidget(channel_label)

        self.channel_box = QComboBox()
        self.channel_box.addItems(["1", "2", "3"])
        layout.addWidget(self.channel_box)

        freq_label = QLabel("Choose frequency")
        layout.addWidget(freq_label)

        self.freq_box = QComboBox()
        self.freq_box.addItems(["200", "252", "300", "360", "400"])
        layout.addWidget(self.freq_box)

        self.button = QPushButton("Create Song")
        self.button.clicked.connect(self.make_song)
        layout.addWidget(self.button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def make_song(self):
        title = self.title_input.text()
        channels = int(self.channel_box.currentText())
        freq = int(self.freq_box.currentText())

        song.new_wav(channels, title, freq)
        self.result_label.setText(title + ".wav created")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()