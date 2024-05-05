import tkinter as tk
from tkinter import filedialog
import main
import time
from PIL import Image, ImageTk
class gui:
    def browseFiles(self):
        self.file_path = filedialog.askopenfilename(title="Open C file", filetypes=(("C files", "*.c"), ("All files", "*.*")))
        self.plt = main.main(self.file_path)

    def __init__(self):
        self.root = tk.Tk()
        self.file_path = ""
        self.plt = None
        image = Image.open('0015-register-allocation-graph-coloring-110901024344-phpapp02-thumbnail.webp')
        image = ImageTk.PhotoImage(image)

        # Create a label to display the image
        image_label = tk.Label(self.root, image=image)
        image_label.pack()

        self.button = tk.Button(self.root, text="Browse C File", command=self.browseFiles, font=("Arial", 12),
                   height=2,
                   highlightbackground="black",
                   highlightcolor="green",
                   highlightthickness=2,
                   justify="center",
                   overrelief="raised",
                   padx=10,
                   pady=5,
                   width=15,
                   wraplength=100)

        self.button.pack()
        self.root.resizable(False, False)
        self.root.mainloop()

if __name__ == "__main__":
    g = gui()