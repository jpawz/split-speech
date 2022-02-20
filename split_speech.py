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


class SoundFile:

    def __init__(self, sound_file):
        self.input_file = AudioSegment.from_mp3(sound_file)

    def detect_silences(self,
                        minimum_silence_length=100,
                        silence_threshold=-50):
        """
        Seeks silences of the minimum length. Silence is detected by the given threshold value.
        """
        self.silences = detect_silence(self.input_file,
                                       min_silence_len=minimum_silence_length,
                                       silence_thresh=silence_threshold)

        return self.silences

    def generate_speech_chunks(self, minimum_sentence_length=100):
        """
        Get two dimensional array of speech starts and stops withing given sound_file.
        [[first_piece_start, first_pice_end], [second_piece_start, second_piece_end]...]
        """
        self.speech_chunks = []
        begining_of_sample = 0
        self.speech_chunks.append([begining_of_sample])

        for i in range(len(self.silences)):
            current_silence_begining = self.silences[i][0]
            current_silence_end = self.silences[i][1]
            self.speech_chunks[i].append(current_silence_begining)
            self.speech_chunks.append([current_silence_end])

        end_of_sample = len(self.input_file)
        self.speech_chunks[-1].append(end_of_sample)

        return self.speech_chunks

    def extend_silences(self, percentage_of_speech=100):
        """
        Inserts after a speech piece silence of percentage_of_speech length.
        E.g. if the piece is 1500ms length and the percentage_of_speech = 100,
        it inserts a 1500ms long silence after the speech piece.
        """
        self.resulting_sound = AudioSegment.empty()

        for i in range(len(self.speech_chunks)):
            beggining_of_chunk = self.speech_chunks[i][0]
            end_of_chunk = self.speech_chunks[i][1]
            chunk_length = end_of_chunk - beggining_of_chunk
            silence_length = chunk_length * percentage_of_speech / 100
            self.resulting_sound = self.resulting_sound + self.input_file[
                beggining_of_chunk:end_of_chunk] + AudioSegment.silent(
                    silence_length)

    def write_resulting_file(self, file_name):
        """
        Exports resulting file to file_name.
        """
        with open(file_name, "wb") as f:
            self.resulting_sound.export(f, format="mp3")


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

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    min_sil_length = args.s
    sil_percentage = args.p
    sil_threshold = args.t

    sound_file = SoundFile(input_file)
    sound_file.detect_silences(minimum_silence_length=min_sil_length,
                               silence_threshold=sil_threshold)
    sound_file.generate_speech_chunks()
    sound_file.extend_silences(percentage_of_speech=sil_percentage)
    sound_file.write_resulting_file(output_file)
