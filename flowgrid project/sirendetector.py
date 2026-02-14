import numpy as np
import pyaudio
import time
from scipy.fft import fft

CHUNK = 4096
RATE = 44100

# Siren frequency range (wider)
SIREN_MIN_FREQ = 300
SIREN_MAX_FREQ = 3000

# Sensitivity threshold
ENERGY_THRESHOLD = 100000


def detect_siren(callback_function):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("🎤 Siren Detection Started... Listening...")

    siren_counter = 0

    while True:
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

        # FFT Analysis
        fft_data = np.abs(fft(data))
        freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)

        # Positive frequencies only
        half = len(freqs) // 2
        positive_freqs = freqs[:half]
        positive_fft = fft_data[:half]

        # Find peak frequency
        peak_index = np.argmax(positive_fft)
        peak_freq = abs(positive_freqs[peak_index])
        peak_energy = positive_fft[peak_index]

        print(f"Peak Freq: {peak_freq:.2f} Hz | Energy: {peak_energy:.2f}")

        # Siren detection logic
        if SIREN_MIN_FREQ <= peak_freq <= SIREN_MAX_FREQ and peak_energy > ENERGY_THRESHOLD:
            siren_counter += 1
        else:
            siren_counter = 0

        # If siren-like sound continues for 3 cycles
        if siren_counter >= 2:
            print("🚑 Siren Detected! Activating Ambulance Mode...")
            callback_function()
            siren_counter = 0
            time.sleep(5)  # cooldown to avoid repeated triggering
