"""
Graphical User Interface for split_speech.py app.
"""

from tkinter import *

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()

        self.title("Split Speech")
        self.minsize(500, 400)

root = Root()
root.mainloop()

