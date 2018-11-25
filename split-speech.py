"""
Looks for pauses in sound file and streches the pauses
to give time for repeating previous pice of speech.
The purpose of this script was to prepare sound file
for pronunciation exercises (repeting speech) for
foreign language practice. The pause duration is
equal to previous piece of sound duration.
"""

import sys
import argparse
from pydub import AudioSegment
from pydub.silence import detect_silence

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input mp3 file")
parser.add_argument("output", help="resulting mp3 file")
parser.add_argument(
    "-s",
    type=int,
    default=100,
    metavar="SILENCE_LENGTH",
    help="minimu silence length in miliseconds (default 100)")
parser.add_argument(
    "-n",
    type=int,
    default=500,
    metavar="SOUND_LENGTH",
    help="minimu sound length in miliseconds (default 500)")

args = parser.parse_args()

input_file = args.input
output_file = args.output

min_sil_length = args.s
min_sound_len = args.n

sound_file = AudioSegment.from_mp3(input_file)
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

resulting_sound.export(output_file, format="mp3")
