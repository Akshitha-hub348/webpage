import sounddevice as sd
import numpy as np
import time

duration = 5
sample_rate = 44100
THRESHOLD = 50   # Adjust if needed

roads = ["Road A", "Road B", "Road C", "Road D"]

current_green = "Road A"


def show_signals(active_road):
    print("\n🚦 Traffic Signal Status:")
    for road in roads:
        if road == active_road:
            print(f"{road} → GREEN")
        else:
            print(f"{road} → RED")

def detect_siren():
    print("\n🎤 Listening for siren...")

    audio = sd.rec(int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1)
    sd.wait()

    audio = audio.flatten()

    fft = np.fft.fft(audio)
    frequencies = np.fft.fftfreq(len(fft), 1/sample_rate)
    magnitude = np.abs(fft)

    positive_freqs = frequencies[:len(frequencies)//2]
    positive_magnitude = magnitude[:len(magnitude)//2]

    siren_band = (positive_freqs > 700) & (positive_freqs < 1600)
    band_energy = np.mean(positive_magnitude[siren_band])

    print("Siren Band Energy:", band_energy)

    if band_energy > THRESHOLD:
        return True
    else:
        return False

# Step 1: Show current normal traffic state
show_signals(current_green)

# Step 2: Check for emergency
if detect_siren():

    # Assume siren detected on Road A (change later if using multiple mics)
    detected_road = "Road A"

    print("\n🚑 EMERGENCY VEHICLE DETECTED!")
    print("Giving priority to:", detected_road)

    show_signals(detected_road)

    print("\n⏳ Keeping emergency green for 5 seconds...")
    time.sleep(5)
    
    print("\n🔁 Returning to normal traffic mode...")
    show_signals(current_green)

else:
    print("\nNo Emergency Detected.")
    print("Traffic signals continues normally.")
