"""
Graphical User Interface for split_speech.py app.
"""

import concurrent.futures
import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog

from split_speech import SoundFile

root = tk.Tk()
root.title("Split Speech")
root.geometry("300x300")
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

filepaths = []
listbox = tk.Listbox(root)
listbox.grid(row=1, column=0, sticky="nwes")


def add_if_not_already_in(paths):
    global filepaths
    for file in paths:
        if file not in filepaths:
            filepaths.append(file)

def add_files():
    global filepaths
    filetypes = (("mp3 files", "*.mp3"), )
    add_if_not_already_in(filedialog.askopenfilenames(filetypes=filetypes))
    listbox.delete(0, END)
    for file in filepaths:
        listbox.insert(END, file)


load_files_button = tk.Button(root,
                              text="Add files",
                              command=lambda: add_files())
load_files_button.grid(row=0, column=0)


def extend_silences(filepath):
    sound_file = SoundFile(filepath)
    sound_file.detect_silences_automatically()
    resulting_filename = filepath[:-4] + "_ext.mp3"
    sound_file.write_resulting_file(resulting_filename)


def process_files():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for filepath in filepaths:
            executor.submit(extend_silences, filepath)
    tk.messagebox.showinfo(message="Done!")


extend_silences_button = tk.Button(root,
                                   text="Start",
                                   command=lambda: process_files())
extend_silences_button.grid(row=2, column=0, sticky="s")

tk.mainloop()
