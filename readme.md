# Objective
Create workout audio with Google TTS by reading a json file which includes breaks and repetitions. Pauses are handled by the program.

# Methodology
- walk folder ./json_transcripts and get the name of the json file. This will be the name of our output.
- Loop through the array of strings and dicts in "transcript" it will either be a string which is the text to read, a dict with key break_sec and an integer for how many seconds to break or another dict with key "repeat" and an integer then "transcript" which has many loops. It is assumed this will only be one level deep and regression is not required.
- Convert string to audio using Google Text-To-Speech
- When a string is converted to audio it is saved in the folder ./audio_lib with the filename being a unique ID and then updating the file ./audio_lib/text_to_audio_dict.json which is a dictionary of file names to text. For future this means common phrases can be read from the audio library instead of hitting Google TTS repetitively. 
- Finally convert the whole thing into audio and pause as required to make an file such that it has the same file name as the json transcripts original file

# repos
Python environment can be found at C:\Users\alexs\venv\workout-audio-gen\Scripts\python.exe

# utilities
- To reset audio generation there is a script delete_audio_lib_cache.py and this will remove all files in audio_lib/* except for text_to_audio_dict.json, which it will set to {}

# Google Text-to-speech
- service account 
email: workout-audio-gen-service-acco@workout-audio-gen.iam.gserviceaccount.com
name: workout-audio-gen-service-account
- keys are stored in json

# Google TTS limitations
- 240seconds hard limit
- Max break 10 seconds
