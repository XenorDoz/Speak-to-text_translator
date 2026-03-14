from datetime import datetime
import os
import sounddevice as sd
import soundfile as sf
import time
import numpy as np
import config as c

CHANNELS = 1
DURATION = 3
ENTRIES = []
OUTPUTS = []
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets", "recorded_samples")

# This is to make audio overlap, so it limits cutting off words
previous_tail = None

def is_silent(audio, threshold = c.THRESHOLD):
    rms = np.sqrt(np.mean(audio**2))
    return rms < threshold

def record_audio(duration = DURATION, samplerate = 48000):
    global previous_tail

    # Creating folder if necessary
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Naming the file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_FOLDER, f"record_{timestamp}.wav")
    audio = sd.rec(frames=int(duration * samplerate), samplerate=samplerate, channels=CHANNELS, dtype='float32')
    sd.wait()

    # Silence detection
    if is_silent(audio):
        if c.LOGGING:
            print("Ignored silence")

    # If we have something before, we add it to the beginning of the new file
    if previous_tail is not None:
        audio = np.concatenate([previous_tail, audio], axis=0)

    # We prepare the next overlap
    tail_length = int(c.OVERLAP * samplerate)
    if audio.shape[0] > tail_length:
        previous_tail = audio[-tail_length:]
    else:
        previous_tail = audio # if audio is too short

    sf.write(filename, audio, samplerate)
    if c.LOGGING:
        print(f"Saved record at :{filename}")
    return filename

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

def select_device(my_list):
    selected_sr = None
    selected_device = None
    input_index = None
    channel_list = []
    samplerate = set()

    # Grabbing every channel
    for channel in my_list:
        channel_list.append({'id': channel['id'], 'name': channel['name'],'samplerate': channel['samplerate']})
        samplerate.add(channel['samplerate'])
    
    samplerate_list = sorted(list(samplerate))
    print("Choose your device to be recorded:")
    print("What samplerate?")
    # Asking for samplerate 
    for index, elem in enumerate(samplerate_list):
        print(f"[{index}] {elem}Hz")

    while not isinstance(input_index, int):
        input_index = input()
        try:
            input_index = int(input_index)
        except Exception:
            print("Please type the id of the desired samplerate.")
    selected_sr = int(samplerate_list[input_index])
    
    # Asking for device with that samplerate
    print("\n\n\n What device?")
    for elem in channel_list:
        if int(elem["samplerate"]) == selected_sr:
            print(f"[{elem['id']}] {elem['name']} ({elem['samplerate']}Hz)")

    while not isinstance(selected_device, int):
        selected_device = input()
        try:
            selected_device = int(selected_device)
        except Exception:
            print("Please type the id of the desired samplerate.")
    return selected_device

def start_record():
    ENTRIES, OUTPUTS = grab_channels()
    seleted_device = select_device(ENTRIES)
    selected_device_info = next((d for d in ENTRIES if d["id"] == seleted_device), None)
    if selected_device_info:
        samplerate = int(selected_device_info["samplerate"])
    else:
        samplerate = 48000
    sd.default.device = seleted_device
    print(f"Starting a recording of {DURATION} seconds in...")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Starting recording!")
    record_audio(DURATION, samplerate)
    print("Finished recording!")

def live_record(duration = DURATION):

    ENTRIES, OUTPUTS = grab_channels()
    seleted_device = select_device(ENTRIES)
    selected_device_info = next((d for d in ENTRIES if d["id"] == seleted_device), None)
    if selected_device_info:
        samplerate = int(selected_device_info["samplerate"])
    else:
        samplerate = 48000
    sd.default.device = seleted_device
    print(f"Starting recordings every {DURATION} seconds in...")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Starting recording!")
    print("CTRL + C to kill script")

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