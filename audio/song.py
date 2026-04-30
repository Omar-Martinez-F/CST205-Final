import numpy as np
import os
from scipy import signal
# To take data from
#import main_window.py

# cd audio at 44,100 hz and 16 bits per sample
SAMPLES_S = 44_100
BITS_SAMPLE = 16

# wave header constants
CHUNK_ID = b'RIFF'
FORMAT = b'WAVE'
SUBCHUNK_1_ID = b'fmt '
SUBCHUNK_2_ID = b'data'

# PCM constants
SUBCHUNK_1_SIZE = (16).to_bytes(4, byteorder='little')
AUDIO_FORMAT = (1).to_bytes(2, byteorder='little')

def create_pcm(frequency, y_vals, duration =0.5):
    sample = int(SAMPLES_S*duration)
    x_vals = np.arange(SAMPLES_S)
    ang_freq = 2 * np.pi * frequency
    #ang_freq2 = 2 * np.pi * (frequency-200)
    #y_vals = 32767 * .3 * np.sin(ang_freq * x_vals / SAMPLES_S)
    #y2_vals = 32767 * .4 * signal.sawtooth(ang_freq * x_vals / SAMPLES_S)
    #y_avg = (y_vals + y2_vals) / 2
    # Swap y2_vals & y_vals to switch between sine or sawtooth
    return np.int16(y_vals)


def new_wav(channels, filename, *frequencies):
    # seconds = len(args)
    #filename = main_window.songtitle


    base_dir = os.path.dirname(os.path.dirname(__file__))
    sounds_dir = os.path.join(base_dir, "assets", "sounds")
    file_path = os.path.join(sounds_dir, f"{filename}.wav")

    pcm_data = []
    for freq in frequencies:
        tone = create_pcm(freq,y_vals,duration = 0.5)
        pcm_data.append(tone)
    full = np.concatenate(pcm_data)
    seconds = len(full) / SAMPLES_S

    chunk_size = (int(36 + (seconds * SAMPLES_S * BITS_SAMPLE/8))).to_bytes(4, 'little')
    num_channels = (channels).to_bytes(2, byteorder='little')
    sample_rate = (SAMPLES_S).to_bytes(4, byteorder='little')
    byte_rate = (int(SAMPLES_S * channels * BITS_SAMPLE/8)).to_bytes(4, byteorder='little')
    block_align = (int(channels * BITS_SAMPLE/8)).to_bytes(2, byteorder='little')
    bits_per_sample = (BITS_SAMPLE).to_bytes(2, byteorder='little')
    subchunk_2_size = (int(seconds * SAMPLES_S * BITS_SAMPLE/8)).to_bytes(4, byteorder='little')

    # my_pcm = []

    # for freq in args:
    #     my_pcm.append(create_pcm(freq))

    # mat = np.array(my_pcm)

    with open(file_path, 'wb') as fo:
        fo.write(
            CHUNK_ID +
            chunk_size +
            FORMAT +
            SUBCHUNK_1_ID +
            SUBCHUNK_1_SIZE +
            AUDIO_FORMAT +
            num_channels +
            sample_rate +
            byte_rate +
            block_align +
            bits_per_sample +
            SUBCHUNK_2_ID +
            subchunk_2_size +
            full.tobytes()
        )
    print(f"Saved to: {file_path}")
    return file_path

if __name__ == "__main__":
    songtitle = "debug"
    channel_count = 3
    test = np.array([200, 252, 212, 400, 150, 360])
    arr = test
    new_wav(channel_count, f"{songtitle}", *arr)

