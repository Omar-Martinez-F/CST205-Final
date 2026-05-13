from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QSlider
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QPainter, QColor

import random
import sys
import os
import json
from audio import song


class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.bars = [0] * 20

    def update_bars(self):
        self.bars = [random.randint(10, 100) for _ in self.bars]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("blue"))
        width = self.width() / len(self.bars)

        for i, height in enumerate(self.bars):
            painter.drawRect(int(i * width), self.height() - height, int(width - 2), height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.note_seq = []
        self.current_file = None
        self.looping = False

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.setWindowTitle("Song Generator")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(QLabel("Make a Song"))

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter song title")
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Enter frequency (Hz)"))
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("Example: 440")
        layout.addWidget(self.freq_input)

        layout.addWidget(QLabel("BPM"))
        self.bpm_box = QComboBox()
        self.bpm_box.addItems(["60", "80", "100", "120", "150", "200"])
        layout.addWidget(self.bpm_box)

        layout.addWidget(QLabel("Channels"))
        self.channel_box = QComboBox()
        self.channel_box.addItems(["1", "2"])
        layout.addWidget(self.channel_box)

        layout.addWidget(QLabel("Waveform"))
        self.waveform_box = QComboBox()
        self.waveform_box.addItems(["sine", "square", "triangle", "sawtooth"])
        layout.addWidget(self.waveform_box)

        self.add_note_btn = QPushButton("Add Frequency")
        self.add_note_btn.clicked.connect(self.add_note)
        layout.addWidget(self.add_note_btn)

        self.delete_note_btn = QPushButton("Delete Last Note")
        self.delete_note_btn.clicked.connect(self.delete_note)
        layout.addWidget(self.delete_note_btn)

        self.sequence_label = QLabel("Sequence: []")
        layout.addWidget(self.sequence_label)

        self.save_pattern_btn = QPushButton("Save Pattern")
        self.save_pattern_btn.clicked.connect(self.save_pattern)
        layout.addWidget(self.save_pattern_btn)

        self.load_pattern_btn = QPushButton("Load Pattern")
        self.load_pattern_btn.clicked.connect(self.load_pattern)
        layout.addWidget(self.load_pattern_btn)

        self.create_btn = QPushButton("Create Song")
        self.create_btn.clicked.connect(self.make_song)
        layout.addWidget(self.create_btn)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        layout.addWidget(QLabel("Player Controls"))

        play_btn = QPushButton("Play")
        play_btn.clicked.connect(self.play_current)
        layout.addWidget(play_btn)

        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.player.pause)
        layout.addWidget(pause_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.player.stop)
        layout.addWidget(stop_btn)

        self.loop_btn = QPushButton("Loop: OFF")
        self.loop_btn.clicked.connect(self.toggle_loop)
        layout.addWidget(self.loop_btn)

        layout.addWidget(QLabel("Volume"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        layout.addWidget(self.volume_slider)

        layout.addWidget(QLabel("Progress"))
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.sliderMoved.connect(self.seek_audio)
        layout.addWidget(self.progress)

        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.set_duration)
        self.player.mediaStatusChanged.connect(self.handle_loop)

        self.visualizer = Visualizer()
        self.visualizer.setMinimumHeight(150)
        layout.addWidget(self.visualizer)

        self.timer = QTimer()
        self.timer.timeout.connect(self.visualizer.update_bars)

    def make_song(self):
        title = self.title_input.text().strip()

        if not title:
            self.result_label.setText("Enter a title")
            return

        if not self.note_seq:
            self.result_label.setText("Add notes first")
            return

        bpm = int(self.bpm_box.currentText())
        duration = 60 / bpm
        channels = int(self.channel_box.currentText())
        waveform = self.waveform_box.currentText()

        file_path = song.new_wav(channels, title, duration, waveform, *self.note_seq)

        self.current_file = file_path
        self.play_audio(file_path)

        self.result_label.setText(f"Playing {title}.wav ({waveform})")

        self.note_seq = []
        self.sequence_label.setText("Sequence: []")

    def play_audio(self, file_path):
        url = QUrl.fromLocalFile(os.path.abspath(file_path))
        self.player.setSource(url)
        self.player.play()
        self.timer.start(100)

    def play_current(self):
        if self.current_file:
            self.play_audio(self.current_file)

    def toggle_loop(self):
        self.looping = not self.looping
        self.loop_btn.setText(f"Loop: {'ON' if self.looping else 'OFF'}")

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)

    def seek_audio(self, position):
        duration = self.player.duration()
        if duration > 0:
            self.player.setPosition(int(duration * (position / 100)))

    def update_progress(self, position):
        duration = self.player.duration()
        if duration > 0:
            self.progress.setValue(int((position / duration) * 100))

    def set_duration(self, duration):
        self.progress.setRange(0, 100)

    def handle_loop(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia and self.looping:
            self.player.setPosition(0)
            self.player.play()

    def add_note(self):
        freq_text = self.freq_input.text().strip()

        try:
            freq = float(freq_text)
            if freq <= 0:
                self.result_label.setText("Must be > 0")
                return

            self.note_seq.append(freq)
            self.sequence_label.setText(f"Sequence: {self.note_seq}")
            self.freq_input.clear()

        except:
            self.result_label.setText("Invalid number")

    def delete_note(self):
        if self.note_seq:
            self.note_seq.pop()
            self.sequence_label.setText(f"Sequence: {self.note_seq}")

    def save_pattern(self):
        title = self.title_input.text().strip()
        if not title or not self.note_seq:
            return

        os.makedirs("saved_patterns", exist_ok=True)

        data = {
            "notes": self.note_seq,
            "bpm": self.bpm_box.currentText(),
            "channels": self.channel_box.currentText(),
            "waveform": self.waveform_box.currentText()
        }

        with open(f"saved_patterns/{title}.json", "w") as f:
            json.dump(data, f)

    def load_pattern(self):
        title = self.title_input.text().strip()

        try:
            with open(f"saved_patterns/{title}.json", "r") as f:
                data = json.load(f)

            self.note_seq = data["notes"]
            self.bpm_box.setCurrentText(data["bpm"])
            self.channel_box.setCurrentText(data["channels"])
            self.waveform_box.setCurrentText(data["waveform"])

            self.sequence_label.setText(f"Sequence: {self.note_seq}")

        except:
            self.result_label.setText("Pattern not found")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())