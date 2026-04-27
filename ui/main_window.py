from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QHBoxLayout
    QPushButton, QComboBox, QLineEdit, QHBoxLayout
)

# from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QPainter, QColor
import random
import sys
import os
from audio import song

# This is a super simple Visualizer it has no real action based on the .wav files what it does it creates bars at random ticks from random import
# For now this should help the GUI look better in the future  we could try to make it react to real music but we would need to change a few things
class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.bars = [0] * 20
    
    def undate_bars(self):
        self.bars = [random.randint(10,100) for _ in self.bars]
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("blue"))

        width = self.width() / len(self.bars)

        for i , height in enumerate(self.bars):
            painter.drawRect(int(i*width), self.height() - height, int(width-2),height)



# This is a super simple Visualizer it has no real action based on the .wav files what it does it creates bars at random ticks from random import
# For now this should help the GUI look better in the future  we could try to make it react to real music but we would need to change a few things
class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.bars = [0] * 20
    
    def undate_bars(self):
        self.bars = [random.randint(10,100) for _ in self.bars]
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("blue"))

        width = self.width() / len(self.bars)

        for i , height in enumerate(self.bars):
            painter.drawRect(int(i*width), self.height() - height, int(width-2),height)




# This is a super simple Visualizer it has no real action based on the .wav files what it does it creates bars at random ticks from random import
# For now this should help the GUI look better in the future  we could try to make it react to real music but we would need to change a few things
class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.bars = [0] * 20
    
    def undate_bars(self):
        self.bars = [random.randint(10,100) for _ in self.bars]
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("blue"))

        width = self.width() / len(self.bars)

        for i , height in enumerate(self.bars):
            painter.drawRect(int(i*width), self.height() - height, int(width-2),height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.note_seq = []

        # self.player = QSoundEffect()
        # self.player.setVolume(0.5)

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

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

        delete_label = QLabel("Delete file")
        layout.addWidget(delete_label)

        self.delete_input = QLineEdit()
        self.delete_input.setPlaceholderText("Enter name of file to delete")
        layout.addWidget(self.delete_input)

        self.del_button = QPushButton("Delete song (Cannot be undone!)")
        self.del_button.clicked.connect(self.delete_song)
        layout.addWidget(self.del_button)

        channel_label = QLabel("Choose channels")
        layout.addWidget(channel_label)

        self.channel_box = QComboBox()
        self.channel_box.addItems(["1", "2", "3"])
        layout.addWidget(self.channel_box)

        bpm_label = QLabel("Edit BPM (*visual only, no functionality yet!*)")
        layout.addWidget(bpm_label)

        self.bpm_box = QComboBox()
        self.bpm_box.addItems(["80", "120", "150", "200", "Enter Custom Amount"])
        layout.addWidget(self.bpm_box)

        freq_label = QLabel("Choose frequency")
        layout.addWidget(freq_label)

        self.freq_box = QComboBox()
        self.freq_box.addItems(["0", "200", "252", "300", "360", "400"])
        layout.addWidget(self.freq_box)

        
        self.add_note_btn = QPushButton("Add Note")
        self.add_note_btn.clicked.connect(self.add_note)
        layout.addWidget(self.add_note_btn)
        self.sequence_label = QLabel("Sequence: []")
        layout.addWidget(self.sequence_label)

        self.del_note_btn = QPushButton("Remove last note")
        self.del_note_btn.clicked.connect(self.del_note)
        layout.addWidget(self.del_note_btn)

        self.button = QPushButton("Create Song")
        self.button.clicked.connect(self.make_song)
        layout.addWidget(self.button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.visualizer = Visualizer()
        self.visualizer.setMinimumHeight(150)
        layout.addWidget(self.visualizer)
        self.timer = QTimer()
        self.timer.timeout.connect(self.visualizer.undate_bars)

    def make_song(self):
        title = self.title_input.text().strip()
        if not title:
            self.result_label.setText("Please enter a title")
            return

        if not self.note_seq:
            self.result_label.setText("Add at least one note")
            return
        
        channels = int(self.channel_box.currentText())
        # freq = int(self.freq_box.currentText())

        file_path = song.new_wav(channels, title, *self.note_seq)

        self.play_audio(file_path)
        self.result_label.setText(f"Playing {title}.wav (saved in assets/sounds)")

    def play_audio(self,file_path):
        url = QUrl.fromLocalFile(os.path.abspath(file_path))
        self.player.setSource(url)
        self.player.play()
        self.timer.start(100)
        self.player.playbackStateChanged.connect(self.handle_state)
    
    def handle_state(self, state):
        if state == QMediaPlayer.StoppedState:
            self.timer.stop()

    def add_note(self):
        freq = int(self.freq_box.currentText())
        self.note_seq.append(freq)
        self.sequence_label.setText(f"Sequence: {self.note_seq}")
    
    def delete_song(self):
        file_delete = self.delete_input.text().strip()
        os.remove(f'assets/sounds/{file_delete}.wav')

    def del_note(self):
        if self.note_seq:
            self.note_seq.pop()
            self.sequence_label.setText(f"Sequence: {self.note_seq}")
            self.result_label.setText("Last tone removed")
        else:
            self.result_label.setText("No tones to delete")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())