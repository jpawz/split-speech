"""
sample.mp3 - speech generated by the ttsmp3.com site from first
four sentences of Zen of Python.
Length of the sample.mp3 is 7628ms.
"""

import os
import unittest
import pathlib
from pydub import AudioSegment
from pydub.silence import detect_silence
from split_speech import SoundFile


class TestSplitSpeech(unittest.TestCase):

    # Detected silences: [[1407, 1912], [3397, 3945], [5426, 5876]]
    # all values are in milliseconds
    begining_of_sample = 0
    end_of_sample = 7628
    first_silence_start = 1407
    first_silence_end = 1912
    second_silence_start = 3397
    second_silence_end = 3945
    third_silence_start = 5426
    third_silence_end = 5876
    first_chunk_length = first_silence_start - begining_of_sample
    second_chunk_length = second_silence_start - first_silence_end
    third_chunk_length = third_silence_start - second_silence_end
    fourth_chunk_length = end_of_sample - third_silence_end

    def setUp(self):
        self.sample = SoundFile("./test_data/sample.mp3")
        self.output_file_name = "sample_ext.mp3"
        self.path_to_output_file = pathlib.Path("./" + self.output_file_name)

    def tearDown(self):
        self.path_to_output_file.unlink(missing_ok=True)

    def test_should_detect_three_silences(self):
        """
        Test if finds three silences.
        """
        number_of_silences = 3
        silences = self.sample.detect_silences_manually()

        self.assertEqual(
            len(silences), number_of_silences,
            f"The sample contains four sentences, so there should be {number_of_silences} silences between them."
        )

    def test_get_correct_chunk_length(self):
        """
        Test if gets the correct length of speech (not silence). After the chunk
        will be added some length of silence. 
        """
        silences = self.sample.detect_silences_manually()

        chunks = self.sample.generate_speech_chunks()
        first_length = chunks[0][1] - chunks[0][0]
        second_length = chunks[1][1] - chunks[1][0]
        third_length = chunks[2][1] - chunks[2][0]
        fourth_length = chunks[3][1] - chunks[3][0]

        self.assertEqual(self.first_chunk_length, first_length,
                         "Incorrect first chunk length")
        self.assertEqual(self.second_chunk_length, second_length,
                         "Incorrect second chunk length")
        self.assertEqual(self.third_chunk_length, third_length,
                         "Incorrect third chunk length")
        self.assertEqual(self.fourth_chunk_length, fourth_length,
                         "Incorrect fourth chunk length")

    def test_resulting_audio_have_proper_length(self):
        """
        Test if resulting audio have proper length. It means test if it's
        extended by a specified percentage of speech length.
        """
        one_hundred_percent = 100
        two_hundred_percent = 200
        all_chunks_length = self.first_chunk_length + self.second_chunk_length + self.third_chunk_length + self.fourth_chunk_length
        resulting_length_extended_100_percentage = (
            all_chunks_length * one_hundred_percent / 100) + all_chunks_length
        resulting_length_extended_200_percentage = (
            all_chunks_length * two_hundred_percent / 100) + all_chunks_length

        self.sample.detect_silences_manually()
        self.sample.generate_speech_chunks()

        self.sample.extend_silences(one_hundred_percent)
        self.assertEqual(
            len(self.sample.resulting_sound),
            resulting_length_extended_100_percentage,
            r"Resulting audio extended by 100% have incorrect length")

        self.sample.extend_silences(two_hundred_percent)
        self.assertEqual(
            len(self.sample.resulting_sound),
            resulting_length_extended_200_percentage,
            r"Resulting audio extended by 200% have incorrect length")

    def test_exports_resulting_sound(self):
        """
        Test if resulting sound is exported to file.
        """
        self.sample.detect_silences_manually()
        self.sample.generate_speech_chunks()
        self.sample.extend_silences()

        self.sample.write_resulting_file(self.output_file_name)

        self.assertEqual((str(
            self.path_to_output_file), self.path_to_output_file.is_file()),
                         (str(self.path_to_output_file), True),
                         "Can't find exported file.")


class TestSpecialCases(unittest.TestCase):

    def test_ignore_too_short_speech(self):
        """
        Too short speech should not be splitted. The sample file
        contains four sentences but one is too short so three pieces
        should be detected. The short sentence is 1053ms long.
        """
        sample = SoundFile("./test_data/sample_with_short_sentence.mp3")
        minimum_sentence_length = 1200  # milliseconds
        number_of_sentences_with_minimum_length = 3

        silences = sample.detect_silences_manually()
        speech_pieces = sample.generate_speech_chunks(
            minimum_sentence_length=minimum_sentence_length)

        self.assertEqual(
            len(speech_pieces), number_of_sentences_with_minimum_length,
            f"There should be {number_of_sentences_with_minimum_length} sentences with at least {minimum_sentence_length}ms length detected."
        )

    def test_ignore_leading_silence(self):
        """
        Silence from the beggining and end of the audio should be ignored.
        There are three sentences in the test data, so there are two silences between them.
        """
        sample = SoundFile("./test_data/sample_lead_trail_sil.mp3")

        silences_without_leading_and_trailing = sample.detect_silences_manually()

        self.assertEqual(
            len(silences_without_leading_and_trailing), 2,
            "Without leading and trailing, there are two silences in the sample."
        )

    def test_ignore_too_long_speech_pieces(self):
        """
        Test if too long speeches are not extended. Sample data have two sentences:
        first 5641ms long and second 2997ms long.
        """
        sample = SoundFile("./test_data/sample_with_too_long_sent.mp3")
        first_sentence_length = 5641
        second_sentence_length = 2997
        both_sentences_extended = (first_sentence_length +
                                   second_sentence_length) * 2

        sample.detect_silences_manually()
        sample.generate_speech_chunks()
        sample.extend_silences(maximum_sentence_length=5000)

        self.assertLess(len(sample.resulting_sound), both_sentences_extended)


if __name__ == "__main__ ":
    unittest.main()