from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QHBoxLayout, QSlider
)

# from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl , QTimer, Qt
from PySide6.QtGui import QPainter, QColor


import random
import sys
import os
from audio import song
import numpy as np
from scipy import signal

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

        title_label = QLabel("Make a Song")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter song title")
        layout.addWidget(self.title_input)

        self.instrument_label = QLabel("Choose instrument")
        layout.addWidget(self.instrument_label)
        self.instrument_box = QComboBox()
        self.instrument_box.addItems(["<choose instrument>", "Sine Wave", "Sawtooth Wave"])
        layout.addWidget(self.instrument_box)
        
        self.inst_confirm = QPushButton("Confirm instrument")
        self.inst_confirm.clicked.connect(self.switch_inst)
        layout.addWidget(self.inst_confirm)

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

        layout.addWidget(QLabel("Player controls"))

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_current)
        layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.player.pause)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.player.stop)
        layout.addWidget(self.stop_btn)

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
        self.timer.timeout.connect(self.visualizer.undate_bars)

    def make_song(self):
        title = self.title_input.text().strip()
        inst = self.instrument_box.currentText()
        freq = int(self.freq_box.currentText())
        duration = 0.5
        SAMPLES_S = 44_100
        sample = int(SAMPLES_S*duration)
        x_vals = np.arange(SAMPLES_S)
        ang_freq = 2 * np.pi * freq
        
        if not title:
            self.result_label.setText("Please enter a title")
            return

        if not self.note_seq:
            self.result_label.setText("Add at least one note")
            return
        
        channels = int(self.channel_box.currentText())

        if inst == "Sine Wave":
            y_val = 32767 * .3 * np.sin(ang_freq * x_vals / SAMPLES_S)
            song.create_pcm(freq, y_val, duration=0.5)
        if inst == "Sawtooth Wave":
            y_val = 32767 * .4 * signal.sawtooth(ang_freq * x_vals / SAMPLES_S)
            song.create_pcm(freq, y_val, duration=0.5)

        #self.result_label.setText(f"Y-VALS IS {y_vals}")
        
        file_path = song.new_wav(channels, title, y_val, *self.note_seq)

        #file_path = song.new_wav(channels, title, *self.note_seq)

       
        self.current_file = file_path
        self.play_audio(file_path)
        self.result_label.setText(f"Playing {title}.wav (saved in assets/sounds)")

        self.note_seq = []
        self.sequence_label.setText("Sequence: []")

    def play_audio(self,file_path):
        url = QUrl.fromLocalFile(os.path.abspath(file_path))
        self.player.setSource(url)
        self.player.play()
        self.timer.start(100)
        self.player.playbackStateChanged.connect(self.handle_state)
    
    def handle_state(self, state):
        if state == QMediaPlayer.StoppedState:
            self.timer.stop()

    
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
            percent = int((position / duration) * 100)
            self.progress.setValue(percent)

    def set_duration(self, duration):
        self.progress.setRange(0, 100)

    def handle_loop(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia and self.looping:
            self.player.setPosition(0)
            self.player.play()

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

    def switch_inst(self):
       inst = self.instrument_box.currentText()
       freq = int(self.freq_box.currentText())
       duration = 0.5
       SAMPLES_S = 44_100
       sample = int(SAMPLES_S*duration)
       x_vals = np.arange(SAMPLES_S)
       ang_freq = 2 * np.pi * freq
       
       if inst == "Sine Wave":
            y_vals = 32767 * .3 * np.sin(ang_freq * x_vals / SAMPLES_S)
            self.result_label.setText("Instrument switched to Sine Wave")
            song.create_pcm(freq, y_vals, duration=0.5)
       if inst == "Sawtooth Wave":
            y_vals = 32767 * .4 * signal.sawtooth(ang_freq * x_vals / SAMPLES_S)
            self.result_label.setText("Instrument switched to Sawtooth Wave")
            song.create_pcm(freq, y_vals, duration=0.5)

       if inst == "<choose instrument>":
            self.result_label.setText("Please select instrument")
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())