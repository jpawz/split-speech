"""
sample.mp3 - speech generated by the ttsmp3.com site from first
four sentences of Zen of Python.
Length of the sample.mp3 is 7628ms.
"""

import unittest
from pydub import AudioSegment
from split_speech import get_silences


class TestSplitSpeech(unittest.TestCase):

    def test_should_detect_three_silences(self):
        """
        Test if finds three silences.
        """
        sample = AudioSegment.from_file("sample.mp3", format="mp3")

        silences = get_silences(sample)

        self.assertEquals(len(silences), 3)

    def test_output_file_have_proper_length(self):
        """
        Test if resulting file have proper length. With the default
        parameters, after the conversion the length should be ms.
        """

    def test_split_sample_file(self):
        """
        Test that the script will find four gaps in sample file
        """
        pass

    def test_parameters_properly_assigned(self):
        """
        Test if parameters passed to the script are properly assigned
        """
        pass


if __name__ == "__main__ ":
    unittest.main()