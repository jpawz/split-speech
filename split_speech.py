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

    def detect_silences_manually(self,
                                 minimum_silence_length=100,
                                 silence_threshold=-50):
        """
        Seeks silences of the minimum length. Silence is detected by the given threshold value.
        """
        self.silences = detect_silence(self.input_file,
                                       min_silence_len=minimum_silence_length,
                                       silence_thresh=silence_threshold)

        self.delete_leading_silence()
        self.delete_trailing_silence()

        return self.silences

    def detect_silences_automatically(self):
        """
        Try to detect the silences automatically.
        """
        # 1. take a 20seconds sample from the middle of the recording
        sample = get_20s_from_the_middle()
        # 2. start searching for silences starting from T=2*dBFS threshold and 100ms silence length
        threshold = 2 * int(self.input_file.dBFS)

        threshold = find_threshold_in_sample(threshold, sample)

        # 5. analyze the whole recording for silences with T threshold
        minimum_silence_length = 100
        self.silences = detect_silence(self.input_file, minimum_silence_length,
                                       threshold)
        self.delete_leading_silence()
        self.delete_trailing_silence()

        minimum_sentence_length = 800
        self.generate_speech_chunks(minimum_sentence_length)

    def generate_speech_chunks(self, minimum_sentence_length=100):
        """
        Get two dimensional array of speech starts and stops withing given sound_file.
        [[first_piece_start, first_pice_end], [second_piece_start, second_piece_end]...]
        """
        self.speech_chunks = []
        begining_of_sample = 0
        self.speech_chunks.append([begining_of_sample])

        index = 0
        for silence in self.silences:
            current_silence_begining = silence[0]
            current_silence_end = silence[1]
            current_speech_chunk_beggining = self.speech_chunks[index][0]
            current_speech_chunk_length = current_silence_begining - current_speech_chunk_beggining
            if current_speech_chunk_length >= minimum_sentence_length:
                self.speech_chunks[index].append(current_silence_begining)
                self.speech_chunks.append([current_silence_end])
                index += 1

        end_of_sample = len(self.input_file)
        self.speech_chunks[-1].append(end_of_sample)

        return self.speech_chunks

    def extend_silences(self,
                        percentage_of_speech=100,
                        maximum_sentence_length=10000):
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
            if chunk_length < maximum_sentence_length:
                silence_length = chunk_length * percentage_of_speech / 100
                self.resulting_sound = self.resulting_sound + self.input_file[
                    beggining_of_chunk:end_of_chunk] + AudioSegment.silent(
                        silence_length)
            else:
                its_last_chunk = (len(self.speech_chunks) - 1) == i
                if its_last_chunk:
                    self.resulting_sound = self.resulting_sound + self.input_file[
                        beggining_of_chunk:end_of_chunk]
                else:
                    beggining_of_next_chunk = self.speech_chunks[i + 1][0]
                    self.resulting_sound = self.resulting_sound + self.input_file[
                        beggining_of_chunk:beggining_of_next_chunk]

    def write_resulting_file(self, file_name):
        """
        Exports resulting file to file_name.
        """
        with open(file_name, "wb") as f:
            self.resulting_sound.export(f, format="mp3")

    def delete_leading_silence(self):
        """
        Remove leading silence from silences list.
        """
        beggining_of_first_silence = self.silences[0][0]
        if beggining_of_first_silence == 0:
            del self.silences[0]

    def delete_trailing_silence(self):
        """
        Remove trailing silence from silences list.
        """
        length_of_input_file = len(self.input_file)
        end_of_last_silence = self.silences[-1][1]
        if end_of_last_silence == length_of_input_file:
            del self.silences[-1]

    def get_20s_from_the_middle(self):
        """
        Returns a 20s sample.
        """
        length = len(self.input_file)
        twenty_seconds = 20_000
        ten_seconds = 10_000
        if length <= twenty_seconds:
            return self.input_file
        else:
            middle = int(length / 2)
            return self.input_file[middle - ten_seconds:middle + ten_seconds]

    def find_threshold_in_sample(self, initial_threshold, sample):
        """
        Find threshold for silence in the sample starting with initial_threshold value.
        """
        threshold = initial_threshold
        for i in range(0, -10, -2):
            sample_silences = detect_silence(sample,
                                             min_silence_len=100,
                                             silence_thresh=threshold + i)
            # 3. count number of detected silences
            number_of_silences_in_sample = len(sample_silences)
            # 4. if number of silences isn't between 8 and 16 go to point 2 with T=T-2
            if 8 <= number_of_silences_in_sample <= 16:
                threshold += i
                break
        return threshold


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
    parser.add_argument(
        "-e",
        type=int,
        default=200,
        metavar="ms",
        help=
        "minimum speech length: after sentences shorter than this limit do not add silences"
    )

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    min_sil_length = args.s
    min_speech_length = args.e
    sil_percentage = args.p
    sil_threshold = args.t

    sound_file = SoundFile(input_file)
    sound_file.detect_silences_manually(minimum_silence_length=min_sil_length,
                                        silence_threshold=sil_threshold)
    sound_file.generate_speech_chunks(
        minimum_sentence_length=min_speech_length)
    sound_file.extend_silences(percentage_of_speech=sil_percentage)
    sound_file.write_resulting_file(output_file)
