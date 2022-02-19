# split_speech.py
Looks for pauses in sound file and stretches the pauses to give time for repeating previous piece of speech. The purpose of this script was to prepare sound file for pronunciation exercises (repeating speech) for foreign language practice. The pause duration is equal to previous piece of sound duration.

## Example Use
`python split_speech.py input.mp3 resulting_file.mp3 -s 100 -p 100 -t -42`

-   s silence length (milliseconds)
-   p gap duration (percentage)
-   t threshold for silence (dB)
