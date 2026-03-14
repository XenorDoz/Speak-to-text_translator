from faster_whisper import WhisperModel
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


def get_random_audio(lang = None):
    if lang == None:
        lang = random.choice(languages)     # Grabs folder name of a random language
    folder_path = os.path.join(BASE_DIR, ASSET_FOLDER, "samples", lang)

    # To not load files again and again 
    if not lang in files:
        files[lang] = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp3', '.wav'))]
    if not files[lang]:
        raise RuntimeError(f"No file found for {lang}")
    
    filename = random.choice(files[lang])
    audio_path = os.path.join(folder_path, filename)
    return lang, filename, audio_path

def main():
    for i in range(5):
        # Sentences
        lang, filename, audio_path = get_random_audio(ENGLISH)
        segments, info = model.transcribe(audio_path, beam_size=5,word_timestamps=True)

        #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        for segment in segments:
            print(f"Transcripting {filename} from {lang} (guesssed {info.language})...")
            if not segment.words:
                continue
            for word in segment.words:
                print(f"\t{word.word}")
            print(f"Transcripted in {(segment.end - segment.start):.2f}s!")
            print(segment.text)

if __name__ == "__main__":
    main()