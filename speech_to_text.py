from faster_whisper import WhisperModel
from datetime import datetime
import os
import random

import config as c

####################################
#               Code               #
####################################

def load():
    load_variables()
    load_model()

def load_variables():
    global BASE_DIR, ASSET_FOLDER, ENGLISH, FRENCH, RUSSIAN, languages, model_size, files, last_text, full_text, choosen_lang, model_task
    print("Loading variables...")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_FOLDER = "assets"
    ENGLISH = "britishenglish"
    FRENCH = "french"
    RUSSIAN = "russian"
    languages = [ENGLISH, FRENCH, RUSSIAN]
    model_size = "medium"
    files = {}
    last_text = ""
    full_text = ""
    choosen_lang = None
    model_task = "tanscribe"
    print("Variables loaded!")

def load_model():
    global model
    print("Starting up the model...")
    # Run on GPU with FP16
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    # model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print("Model started!")

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

def get_first_audio_from_recorded_samples():
    folder_path = os.path.join(BASE_DIR, ASSET_FOLDER, "recorded_samples")
    recorded_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp3', '.wav'))]
    first_file = "" # Most recent file
    first_file_date = datetime.max
    for file in recorded_files:
        # We grab the most recent file
        file_date = grab_date(file)
        if file_date < first_file_date:
            first_file_date = file_date
            first_file = file
    audio_path = os.path.join(folder_path, first_file)
    return first_file, audio_path

def grab_date(file: str):
    file_date = file.replace("record_", "")[:-4]
    dt = datetime.strptime(file_date, "%Y-%m-%d_%H-%M-%S")
    return dt

def read_recorded_audio(filename = None, file_path = None):
    global last_text, full_text
    if not filename or not file_path:
        filename, file_path = get_first_audio_from_recorded_samples()
    
    segments, info = model.transcribe(file_path, beam_size=5,language = choosen_lang, task=model_task)

    if c.LOGGING:
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    full_text = "" # This is the final text that will be sent

    for segment in segments:
        if segment.no_speech_prob > 0.6:
            if c.LOGGING:
                print("No speech prob high, ignored segment.")
            continue
        if c.LOGGING:
            print(f"Transcripting {filename} (guesssed {info.language})...")
            print(f"Transcripted in {(segment.end - segment.start):.2f}s!")

        text = segment.text.strip() # We grab every word
        # Anti-duplication with the overlap
        if text.startswith(last_text):
            text = text[len(last_text):].strip()
        
        # Updating last text for next segment
        last_text = segment.text.strip()

        if text:
            print(text)
            full_text += " " + text
    return filename, file_path

def delete_file(file_path: str):
    if os.path.isfile(file_path):
        os.remove(file_path)
        if c.LOGGING:
            print(f"File '{file_path}' deleted successfully.")
    else:
        print(f"No file found at: {file_path}")

def main():
    for i in range(10):      # Sentences
        lang, filename, audio_path = get_random_audio_from_sample(ENGLISH)
        segments, info = model.transcribe(audio_path, beam_size=5,)

        #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        for segment in segments:
            print(f"Transcripting {filename} from {lang} (guesssed {info.language})...")
            print(f"Transcripted in {(segment.end - segment.start):.2f}s!")
            print(segment.text)

def main_recorded_files():
    filename, file_path = read_recorded_audio()
    delete_file(file_path)

def choose_lang():
    global choosen_lang
    selected = None
    languages = {0: None, 1: "en", 2: "fr", 3: "ru"}
    print("Do you know what will be the language spoken ?")
    for elem in languages.items():
        print(f"[{elem[0]}] {elem[1]}")
    
    while not isinstance(selected, int):
        try:
            selected = int(input("Please type the index: "))
        except:
            print("Please type the index of the desired language")
    choosen_lang = languages[selected]
    
def choose_mode():
    global model_task
    selected = None
    while not isinstance(selected, int):
        try:
            selected = int(input("Do you want to transcribe (1) or translate to english (2)?"))
        except:
            print("Please type 1 or 2.")
    if selected == 1:
        model_task = "transcribe"
    else:
        model_task = "translate"
    pass

if __name__ == "__main__":
    main_recorded_files()

# TODO: Check if file is considered empty before feeding to model, this will limits lags