import os
import json

# Configuration Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_LIB_DIR = os.path.join(BASE_DIR, 'audio_lib')
AUDIO_DICT_FILE = os.path.join(AUDIO_LIB_DIR, 'text_to_audio_dict.json')

def main():
    if not os.path.exists(AUDIO_LIB_DIR):
        print(f"Directory not found: {AUDIO_LIB_DIR}")
        return

    print(f"Cleaning up {AUDIO_LIB_DIR}...")

    # Delete mp3 files
    deleted_count = 0
    for filename in os.listdir(AUDIO_LIB_DIR):
        if filename.lower().endswith('.mp3'):
            file_path = os.path.join(AUDIO_LIB_DIR, filename)
            try:
                os.remove(file_path)
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting {filename}: {e}")

    print(f"Deleted {deleted_count} .mp3 files.")

    # Reset dictionary
    try:
        with open(AUDIO_DICT_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)
        print(f"Reset {AUDIO_DICT_FILE} to empty dictionary.")
    except OSError as e:
        print(f"Error resetting dictionary file: {e}")

if __name__ == "__main__":
    main()