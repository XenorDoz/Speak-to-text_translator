from datetime import datetime
import os
import sounddevice as sd
import soundfile as sf

CHANNELS = 1
DURATION = 5
ENTRIES = []
OUTPUTS = []
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets", "recorded_samples")

def record_audio(duration = DURATION, samplerate = 48000):
    # Creating folder if necessary
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Naming the file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_FOLDER, f"record_{timestamp}.wav")
    audio = sd.rec(frames=int(duration * samplerate), samplerate=samplerate, channels=CHANNELS, dtype='float32')
    sd.wait()

    sf.write(filename, audio, samplerate)
    print(f"Saved record at :{filename}")

def grab_channels():
    devices = sd.query_devices()
    entries = []
    output = []
    for item in devices:
        new_item = {"name": item["name"], "id": item["index"], "samplerate": item["default_samplerate"]}
        if item["max_input_channels"] > 0:
            entries.append(new_item)
        if item["max_output_channels"] > 0:
            output.append(new_item)
    return entries, output

def select_device(list):
    selected = None
    channel_list = []
    print("Choose your device to be recorded:")
    for channel in list:
        print(f"[{channel['id']}] {channel['name']} ({channel['samplerate']}Hz)")
        channel_list.append(channel)
    while not isinstance(selected, int):
        selected = input()
        try:
            selected = int(selected)
        except Exception:
            print("Please type the id of the desired device.")

    return selected

def main():
    ENTRIES, OUTPUTS = grab_channels()
    seleted_device = select_device(ENTRIES)
    selected_device_info = next((d for d in ENTRIES if d["id"] == seleted_device), None)
    if selected_device_info:
        samplerate = int(selected_device_info["samplerate"])
    else:
        samplerate = 48000
    sd.default.device = seleted_device
    print(f"Starting a recording of {DURATION} seconds...")
    record_audio(DURATION, samplerate)
    print("Finished recording!")

if __name__ == "__main__":
    main()