import record_audio, speech_to_text
import threading
import time

import config as c

record_done = threading.Event()
model_ready = threading.Event()

def record_loop():
    # Calls the initial print
    record_audio.live_record(duration=c.DURATION)
    while True:
        # Starting recording
        filename = record_audio.record_audio(c.DURATION)
        if filename is None: # If it is empty, don't check it
            continue
        record_done.set()
    pass

def stt_loop():
    while True:
        record_done.wait()
        speech_to_text.main_recorded_files()
        record_done.clear()
    pass

def start_live_translation():
    speech_to_text.load()
    time.sleep(2)
    threading.Thread(target = record_loop, daemon = True).start()
    threading.Thread(target = stt_loop, daemon = True).start()

    # That is just to keep program alive
    while True:
        pass

def start_one_translation():
    record_audio.start_record()
    speech_to_text.main_recorded_files()

if __name__ == "__main__":
    start_live_translation()