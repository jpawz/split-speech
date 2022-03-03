"""
Graphical User Interface for split_speech.py app.
"""

import tkinter as tk
from tkinter import *
from tkinter import filedialog

root = tk.Tk()
root.title("Split Speech")
root.geometry("300x300")


def add_files():
    filetypes = (("mp3 files", "*.mp3"),)
    filenames = filedialog.askopenfiles(mode='r', filetypes=filetypes)


button = tk.Button(root, text="Add files", command=lambda: add_files())

button.grid(row=1, column=0)
tk.mainloop()