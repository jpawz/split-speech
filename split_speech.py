"""
Looks for pauses in sound file and stretches the pauses
to give time for repeating previous piece of speech.
The purpose of this script was to prepare sound file
for pronunciation exercises (repeating speech) for
foreign language practice.
"""

import sys
import argparse
from pydub import AudioSegment
from pydub.silence import detect_silence

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='split-speech',
        description='extends silences to give time for repetition')
    parser.add_argument("input", help="input mp3 file")
    parser.add_argument("output", help="resulting mp3 file")
    parser.add_argument(
        "-s",
        type=int,
        default=100,
        metavar="ms",
        help="minimum silence length in milliseconds (default 100)")
    parser.add_argument(
        "-n",
        type=int,
        default=500,
        metavar="ms",
        help="minimum sound length in milliseconds (default 500)")
    parser.add_argument(
        "-p",
        type=int,
        default=100,
        metavar="%",
        help=
        "set silence length as percentage of previous sound duration (default 100)"
    )
    parser.add_argument(
        "-t",
        type=int,
        default=-50,
        metavar="dB",
        help=
        "threshold for silence (dB) (default -50): below this level sound is counted as silence"
    )

    parser.add_argument(
        "-a",
        type=int,
        nargs="?",
        default=None,
        metavar="ms",
        help=
        "detect threshold: provide value for desired sound length (in milliseconds)"
    )

    parser.add_argument(
        "-m",
        type=int,
        default=None,
        metavar="ms",
        help="do not add pause after sound longer than length in milliseconds")

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    min_sil_length = args.s
    min_sound_len = args.n
    max_sound_len = args.m
    sil_percentage = args.p / 100
    sil_threshold = args.t

    sound_file = AudioSegment.from_mp3(input_file)

    if args.a is not None:
        desired_sound_len = args.a
        one_minute = 60 * 1000
        detected_chunks = 0
        initial_sil_threshold = -60
        if (len(sound_file) > 2 * one_minute):
            sound_probe = sound_file[one_minute:2 * one_minute]
            min_number_of_chunks = int(len(sound_probe) / desired_sound_len)
            while detected_chunks <= min_number_of_chunks:
                initial_sil_threshold += 1
                silences_in_probe = detect_silence(
                    sound_probe,
                    min_silence_len=min_sil_length,
                    silence_thresh=initial_sil_threshold)
                detected_chunks = len(silences_in_probe)
            silences = detect_silence(sound_file,
                                      min_silence_len=min_sil_length,
                                      silence_thresh=initial_sil_threshold)
        else:
            min_number_of_chunks = int(len(sound_file) / desired_sound_len)
            while detected_chunks <= min_number_of_chunks:
                initial_sil_threshold += 1
                silences = detect_silence(sound_file,
                                          min_silence_len=min_sil_length,
                                          silence_thresh=initial_sil_threshold)
                detected_chunks = len(silences)
    else:
        silences = detect_silence(sound_file,
                                  min_silence_len=min_sil_length,
                                  silence_thresh=sil_threshold)

    resulting_sound = AudioSegment.empty()

    silence_len = 0
    last_chunk_index = len(silences) - 1
    for i in range(len(silences) - 1, 0, -1):
        if args.m is not None and silences[i][0] - silences[
                i - 1][1] > max_sound_len:
            resulting_sound = sound_file[
                silences[i - 1][0]:silences[i][1]] + resulting_sound
        elif (silences[last_chunk_index][0] -
              silences[i - 1][1]) > min_sound_len:
            silence_len = silence_len + (silences[i][1] - silences[i - 1][0])
            resulting_sound = sound_file[silences[i-1][0]:silences[i][1]] + \
            AudioSegment.silent(int(round(silence_len * sil_percentage))) + resulting_sound
            silence_len = 0
            last_chunk_index = i
        else:
            resulting_sound = sound_file[silences[i - 1][0]:silences[i][1]] + \
            resulting_sound
            silence_len = silence_len + (silences[i][1] - silences[i - 1][0])
    resulting_sound = sound_file[:silences[0][0]] + AudioSegment.silent(
        int(round(silences[0][0] * sil_percentage))) + resulting_sound
    resulting_sound.export(output_file, format="mp3")


class SoundFile:

    def __init__(self, sound_file):
        self.input_file = AudioSegment.from_mp3(sound_file)

    def get_silences(self,
                     automatic_mode=False,
                     minimum_silence_length=100,
                     silence_threshold=-50):
        self.silences = detect_silence(self.input_file,
                                       min_silence_len=minimum_silence_length,
                                       silence_thresh=silence_threshold)

        return self.silences

    def get_speech_chunks(self, minimum_speech_length=2000):
        """
        Get two dimensional array of speech starts and stops withing given sound_file.
        [[first_piece_start, first_pice_end], [second_piece_start, second_piece_end]...]
        The pieces of sound are of longer then minimum_speech_length.
        """
        speech_chunks = []
        begining_of_sample = 0
        speech_chunks.append([begining_of_sample])
        first_silence_start = self.silences[0][0]
        speech_chunks[0].append(first_silence_start)

        first_silence_end = self.silences[0][1]
        speech_chunks.append([first_silence_end])
        second_silence_start = self.silences[1][0]
        speech_chunks[1].append(second_silence_start)

        third_silence_end = self.silences[1][1]
        speech_chunks.append([third_silence_end])
        third_silence_start = self.silences[2][0]
        speech_chunks[2].append(third_silence_start)

        fourth_silence_end = self.silences[2][1]
        speech_chunks.append([fourth_silence_end])
        end_of_sample = len(self.input_file)
        speech_chunks[3].append(end_of_sample)

        return speech_chunks