import numpy as np
import os
import wave

SAMPLE_RATE = 44100


def create_pcm(frequency, duration, waveform="sine"):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    if waveform == "sine":
        tone = np.sin(2 * np.pi * frequency * t)

    elif waveform == "square":
        tone = np.sign(np.sin(2 * np.pi * frequency * t))

    elif waveform == "triangle":
        tone = 2 * np.abs(2 * ((frequency * t) % 1) - 1) - 1

    elif waveform == "sawtooth":
        tone = 2 * ((frequency * t) % 1) - 1

    else:
        tone = np.sin(2 * np.pi * frequency * t)

    tone *= 32767 * 0.3
    return tone.astype(np.int16)


def new_wav(channels, filename, duration, waveform, *frequencies):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    sounds_dir = os.path.join(base_dir, "assets", "sounds")
    os.makedirs(sounds_dir, exist_ok=True)

    file_path = os.path.join(sounds_dir, f"{filename}.wav")

    pcm_data = []
    for freq in frequencies:
        pcm_data.append(create_pcm(float(freq), duration, waveform))

    full = np.concatenate(pcm_data)

    if channels == 2:
        full = np.repeat(full[:, np.newaxis], 2, axis=1).flatten()

    with wave.open(file_path, "w") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(full.tobytes())

    return file_path