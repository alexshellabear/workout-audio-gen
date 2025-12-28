import os
import json
import hashlib
import time
from google.cloud import texttospeech
from pydub import AudioSegment

# Configuration Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TRANSCRIPTS_DIR = os.path.join(BASE_DIR, 'json_transcripts')
AUDIO_LIB_DIR = os.path.join(BASE_DIR, 'audio_lib')
AUDIO_DICT_FILE = os.path.join(AUDIO_LIB_DIR, 'text_to_audio_dict.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Audio Tuning
TTS_SPEED = 1.25  # Speed multiplier (1.0 = normal, 1.25 = 25% faster)

# Rate Limiting
QUERIES_PER_MINUTE = 15
MIN_REQUEST_INTERVAL = 60.0 / QUERIES_PER_MINUTE
last_request_time = 0

# Ensure directories exist
os.makedirs(AUDIO_LIB_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set Google Application Credentials if a JSON key file exists in the base directory
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'service_account.json')
if os.path.exists(CREDENTIALS_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

# Load existing cache
if os.path.exists(AUDIO_DICT_FILE):
    with open(AUDIO_DICT_FILE, 'r', encoding='utf-8') as f:
        text_to_audio_map = json.load(f)
else:
    text_to_audio_map = {}

def save_cache():
    """Saves the text-to-audio map to disk."""
    with open(AUDIO_DICT_FILE, 'w', encoding='utf-8') as f:
        json.dump(text_to_audio_map, f, indent=4)

def get_audio_segment_from_text(text):
    """
    Retrieves an AudioSegment for the given text.
    Checks cache first; if missing, generates via gTTS.
    """
    global last_request_time
    text = text.strip()
    if not text:
        return AudioSegment.empty()

    file_path = None
    # Check if text is already cached (search by value)
    existing_filename = None
    for fname, content in text_to_audio_map.items():
        if content == text:
            existing_filename = fname
            print(f"Using cached audio for: {text[:40]}...")
            break
    
    if existing_filename:
        potential_path = os.path.join(AUDIO_LIB_DIR, existing_filename)
        if os.path.exists(potential_path):
            file_path = potential_path
    
    if not file_path:
        # Generate new audio
        print(f"Generating TTS for: {text[:40]}...")
        elapsed = time.time() - last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)

        file_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        filename = f"{file_hash}.wav"
        file_path = os.path.join(AUDIO_LIB_DIR, filename)
        
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-au",
            name="Schedar", # Algieba too high pitched
            model_name="gemini-2.5-flash-tts"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=0,
            speaking_rate=TTS_SPEED
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        last_request_time = time.time()

        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        
        # Update cache
        text_to_audio_map[filename] = text
        save_cache()
    
    audio = AudioSegment.from_file(file_path)
    return audio

def parse_transcript(transcript_list):
    """Recursively parses the transcript list and builds the audio track."""
    combined_audio = AudioSegment.empty()
    
    for item in transcript_list:
        if isinstance(item, str):
            combined_audio += get_audio_segment_from_text(item)
            
        elif isinstance(item, dict):
            if "break_sec" in item:
                # pydub silent duration is in milliseconds
                silence_ms = item["break_sec"] * 1000
                combined_audio += AudioSegment.silent(duration=silence_ms)
                
            elif "repeat" in item:
                count = item["repeat"]
                sub_transcript = item.get("transcript", [])
                loop_segment = parse_transcript(sub_transcript)
                combined_audio += (loop_segment * count)
                
    return combined_audio

def main():
    # Check for ffmpeg dependency to prevent confusing WinError 2
    from pydub.utils import which
    if which("ffmpeg") is None:
        raise FileNotFoundError("ffmpeg is not installed or not found in PATH. It is required by pydub to process MP3s.")

    for filename in os.listdir(TRANSCRIPTS_DIR):
        if filename.lower().endswith('.json'):
            print(f"Processing {filename}...")
            with open(os.path.join(TRANSCRIPTS_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            final_audio = parse_transcript(data.get("transcript", []))
            
            output_filename = os.path.splitext(filename)[0] + ".mp3"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            print(f"Exporting to {output_path}")
            final_audio.export(output_path, format="mp3")

if __name__ == "__main__":
    main()