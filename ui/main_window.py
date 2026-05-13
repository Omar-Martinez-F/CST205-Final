"""
CST205-01
ToneCraft

This program allows a user to create new .wav audio files providing their own info such as 
song title, instrument (Sine wave or Sawtooth wave), delete function, number of channels, frequency and duration.
Also gave the user audio control with play,pause, and loop buttons, 
User can also see a audio visualizer

Omar Martinez-Fuentes, Joseph Lustre-Rendon, William (Billy)
5/16/2026

Link to repo: https://github.com/Omar-Martinez-F/CST205-Final

"""

# Imports needed for Main window GUI
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QHBoxLayout, QSlider)

# from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QPainter, QColor


import random
import sys
import os
from audio import song
import numpy as np
from scipy import signal

# This is a super simple Visualizer it has no real action based on the .wav files what it does it creates bars at random ticks from random import
# For now this should help the GUI look better in the future  we could try to make it react to real music but we would need to change a few things

# Omar
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

# Main working window
# Base created by Joseph, Omar updated/added features 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.note_seq = []
        self.current_file = None
        self.looping = False 

        # self.player = QSoundEffect()
        # self.player.setVolume(0.5)

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.setWindowTitle("Song Generator")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # layout = QVBoxLayout()

        self.resize(1100, 650)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # central_widget.setLayout(layout)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)


        title_label = QLabel("Make a Song")
        left_layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter song title")
        left_layout.addWidget(self.title_input)

        self.instrument_label = QLabel("Choose instrument")
        left_layout.addWidget(self.instrument_label)
        self.instrument_box = QComboBox()
        self.instrument_box.addItems(["<choose instrument>", "Sine Wave", "Sawtooth Wave"])
        left_layout.addWidget(self.instrument_box)
        
        #self.inst_confirm = QPushButton("Confirm instrument")
        #self.inst_confirm.clicked.connect(self.switch_inst)
        #layout.addWidget(self.inst_confirm)

        delete_label = QLabel("Delete file")
        left_layout.addWidget(delete_label)

        self.delete_input = QLineEdit()
        self.delete_input.setPlaceholderText("Enter name of file to delete")
        left_layout.addWidget(self.delete_input)

        self.del_button = QPushButton("Delete song (Cannot be undone!)")
        self.del_button.clicked.connect(self.delete_song)
        left_layout.addWidget(self.del_button)

        channel_label = QLabel("Choose channels")
        left_layout.addWidget(channel_label)

        self.channel_box = QComboBox()
        self.channel_box.addItems(["1", "2", "3"])
        left_layout.addWidget(self.channel_box)

        bpm_label = QLabel("Edit BPM (*visual only, no functionality yet!*)")
        left_layout.addWidget(bpm_label)

        self.bpm_box = QComboBox()
        self.bpm_box.addItems(["80", "120", "150", "200", "Enter Custom Amount"])
        left_layout.addWidget(self.bpm_box)

        freq_label = QLabel("Choose frequency")
        left_layout.addWidget(freq_label)

        self.freq_box = QComboBox()
        self.freq_box.addItems(["0", "200", "252", "300", "360", "400"])
        left_layout.addWidget(self.freq_box)

        
        duration_label = QLabel("Choose duration")
        left_layout.addWidget(duration_label)

        self.duration_box = QComboBox()
        self.duration_box.addItems([
                        "Quarter",
                        "Half",
                        "Whole"
        ])
        left_layout.addWidget(self.duration_box)

        self.add_note_btn = QPushButton("Add Note")
        self.add_note_btn.clicked.connect(self.add_note)
        left_layout.addWidget(self.add_note_btn)
       

        self.delete_note_btn = QPushButton("Delete Last Tone")
        self.delete_note_btn.clicked.connect(self.delete_note)
        left_layout.addWidget(self.delete_note_btn)

        self.sequence_label = QLabel("Sequence: []")
        left_layout.addWidget(self.sequence_label)

        self.button = QPushButton("Create Song")
        self.button.clicked.connect(self.make_song)
        left_layout.addWidget(self.button)

        self.result_label = QLabel("")
        right_layout.addWidget(self.result_label)
        
        right_layout.addWidget(QLabel("Player controls"))

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_current)
        right_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.player.pause)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.player.stop)
        right_layout.addWidget(self.stop_btn)

        self.loop_btn = QPushButton("Loop: OFF")
        self.loop_btn.clicked.connect(self.toggle_loop)
        right_layout.addWidget(self.loop_btn)

        right_layout.addWidget(QLabel("Volume"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        right_layout.addWidget(self.volume_slider)

        right_layout.addWidget(QLabel("Progress"))
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.sliderMoved.connect(self.seek_audio)
        right_layout.addWidget(self.progress)

        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.set_duration)
        self.player.mediaStatusChanged.connect(self.handle_loop)

        self.visualizer = Visualizer()
        self.visualizer.setMinimumHeight(150)
        right_layout.addWidget(self.visualizer)
        self.timer = QTimer()
        self.timer.timeout.connect(self.visualizer.undate_bars)

    def make_song(self):
        title = self.title_input.text().strip()
        inst = self.instrument_box.currentText()
        #freq = int(self.freq_box.currentText())
        duration = 0.5
        SAMPLES_S = 44_100
        sample = int(SAMPLES_S*duration)
        x_vals = np.arange(SAMPLES_S)
        #ang_freq = 2 * np.pi * freq
        
        if not title:
            self.result_label.setText("Please enter a title")
            return

        if not self.note_seq:
            self.result_label.setText("Add at least one note")
            return
        
        channels = int(self.channel_box.currentText())

        #  if inst == "Sine Wave":
        #      y_val = 32767 * .3 * np.sin(ang_freq * x_vals / SAMPLES_S)
        #      song.create_pcm(freq, y_val, duration=0.5)
        #  if inst == "Sawtooth Wave":
        #      y_val = 32767 * .4 * signal.sawtooth(ang_freq * x_vals / SAMPLES_S)
        #      song.create_pcm(freq, y_val, duration=0.5)

        #self.result_label.setText(f"Y-VALS IS {y_vals}")
        
        file_path = song.new_wav(channels, title, inst, *self.note_seq)

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

        
        self.timer.start(100)

    def add_note(self):
        # Testing new logic
        freq = int(self.freq_box.currentText())

        duration_map = {
            "Quarter": 0.25,
            "Half": 0.5,
            "Whole": 1.0
        }

        duration_name = self.duration_box.currentText()
        duration = duration_map[duration_name]

        self.note_seq.append((freq, duration))

        self.sequence_label.setText(f"Sequence: {self.note_seq}")
        # freq = int(self.freq_box.currentText())
        # self.note_seq.append(freq)
        # self.sequence_label.setText(f"Sequence: {self.note_seq}")
    
    def delete_song(self):
        file_delete = self.delete_input.text().strip()
        os.remove(f'assets/sounds/{file_delete}.wav')

    def delete_note(self):
        if self.note_seq:
            self.note_seq.pop()
            self.sequence_label.setText(f"Sequence: {self.note_seq}")
            self.result_label.setText("Last tone removed")
        else:
            self.result_label.setText("No tones to delete")

    # def switch_inst(self):
    #    inst = self.instrument_box.currentText()
    #    freq = int(self.freq_box.currentText())
    #    duration = 0.5
    #    SAMPLES_S = 44_100
    #    sample = int(SAMPLES_S*duration)
    #    x_vals = np.arange(SAMPLES_S)
    #    ang_freq = 2 * np.pi * freq
       
    #    if inst == "Sine Wave":
    #         #y_vals = 32767 * .3 * np.sin(ang_freq * x_vals / SAMPLES_S)
    #         self.result_label.setText("Instrument switched to Sine Wave")
    #         #song.create_pcm(freq, y_vals, duration=0.5)
    #    if inst == "Sawtooth Wave":
    #         #y_vals = 32767 * .4 * signal.sawtooth(ang_freq * x_vals / SAMPLES_S)
    #         self.result_label.setText("Instrument switched to Sawtooth Wave")
    #         #song.create_pcm(freq, y_vals, duration=0.5)

    #    if inst == "<choose instrument>":
    #         self.result_label.setText("Please select instrument")
    #         return

    # def handle_loop(self, status):
    #     from PySide6.QtMultimedia import QMediaPlayer
    #     if status == QMediaPlayer.EndOfMedia and self.looping:
    #         self.player.setPosition(0)
    #         self.player.play()     

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())