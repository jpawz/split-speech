"""
Looks for pauses in sound file and streches the pauses
to give time for repeating previous pice of speech.
The purpose of this script was to prepare sound file
for pronunciation exercises (repeting speech) for
foreign language practice. The pause duration is
equal to previous piece of sound duration.
"""

import sys
from pydub import AudioSegment
from pydub.silence import detect_silence



if len(sys.argv) < 3:
    print("not enough parameters")
    print("usage: python split-speech.py INPUT.MP3 OUTPUT.MP3 [a] [b]")
    print(" a: minimum silence length in miliseconds (default 100)")
    print(" b: minimum sound length in miliseconds (default 500)")
    exit()
elif len(sys.argv) == 4:
    min_sil_length = int(sys.argv[3])
elif len(sys.argv) == 5:
    min_sil_length = int(sys.argv[3])
    min_sound_len = int(sys.argv[4])
else:
    min_sil_length = 100
    min_sound_len = 500

sound_file = AudioSegment.from_mp3(sys.argv[1])
silences = detect_silence(
    sound_file, min_silence_len=min_sil_length, silence_thresh=-40)
resulting_sound = AudioSegment.empty()

silence_len = 0
for i in range(len(silences) - 1, 0, -1):
    if (silences[i][0] - silences[i - 1][1]) > min_sound_len:
        silence_len = silence_len + (silences[i][1] - silences[i - 1][0])
        resulting_sound = sound_file[silences[i-1][0]:silences[i][1]] + \
          AudioSegment.silent(silence_len) + resulting_sound
        silence_len = 0
    else:
        resulting_sound = sound_file[silences[i - 1][0]:silences[i][1]] + \
          resulting_sound
        silence_len = silence_len + (silences[i][1] - silences[i - 1][0])

resulting_sound.export(sys.argv[2], format="mp3")
