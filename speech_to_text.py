from faster_whisper import WhisperModel
from datetime import datetime
import os
import random

####################################
#            Variables             #
####################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_FOLDER = "assets"
ENGLISH = "britishenglish"
FRENCH = "french"
RUSSIAN = "russian"
languages = [ENGLISH, FRENCH, RUSSIAN]
model_size = "medium"
files = {}

####################################
#               Code               #
####################################

# Run on GPU with FP16
print("Starting up the model...")
model = WhisperModel(model_size, device="cuda", compute_type="float16")
print("Model started!")
# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")


def get_random_audio_from_sample(lang = None):
    global files
    if lang == None:
        lang = random.choice(languages)     # Grabs folder name of a random language
    folder_path = os.path.join(BASE_DIR, ASSET_FOLDER, "samples", lang)

    # To not load files again and again 
    if not lang in files:
        # Adding every file of corresponding language in the array
        files[lang] = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp3', '.wav'))]
    if not files[lang]:
        raise RuntimeError(f"No file found for {lang}")
    
    filename = random.choice(files[lang])
    audio_path = os.path.join(folder_path, filename)
    return lang, filename, audio_path

def get_audio_from_recorded_samples():
    folder_path = os.path.join(BASE_DIR, ASSET_FOLDER, "recorded_samples")
    recorded_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp3', '.wav'))]
    last_file = "" # Most recent file
    last_file_date = datetime.min
    for file in recorded_files:
        # We grab the most recent file
        file_date = grab_date(file)
        if file_date > last_file_date:
            last_file_date = file_date
            last_file = file
    audio_path = os.path.join(folder_path, last_file)
    return last_file, audio_path

def grab_date(file: str):
    file_date = file.replace("record_", "")[:-4]
    dt = datetime.strptime(file_date, "%Y-%m-%d_%H-%M-%S")
    return dt

def main():
    # Sentences
    lang, filename, audio_path = get_random_audio_from_sample(ENGLISH)
    segments, info = model.transcribe(audio_path, beam_size=5,)

    #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print(f"Transcripting {filename} from {lang} (guesssed {info.language})...")
        print(f"Transcripted in {(segment.end - segment.start):.2f}s!")
        print(segment.text)

def main_recorded_files():
    # Sentences
    filename, audio_path = get_audio_from_recorded_samples()
    
    segments, info = model.transcribe(audio_path, beam_size=5,)

    #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    for segment in segments:
        print(f"Transcripting {filename} (guesssed {info.language})...")
        print(f"Transcripted in {(segment.end - segment.start):.2f}s!")
        print(segment.text)

if __name__ == "__main__":
    main_recorded_files()

# TODO: Link record_audio.py and speech_to_text.py
# TODO: Manage the recorded files to be deleted after used
#       -> delete function, called by whatever would use the audio if possible