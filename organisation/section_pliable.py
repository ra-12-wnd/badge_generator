import tkinter as tk
from PIL import ImageTk, Image
import os

class SectionPliable(tk.Frame):
    def __init__(self, master, title):
        super().__init__(master, bg="#d3d3d3")

        # Gestion des chemins des icônes
        ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
        expand_icon_path = os.path.join(ASSETS_DIR, "expand.png")
        collapse_icon_path = os.path.join(ASSETS_DIR, "collapse.png")

        # Chargement des images
        self.icon_expand = ImageTk.PhotoImage(Image.open(expand_icon_path).resize((16, 16)))
        self.icon_collapse = ImageTk.PhotoImage(Image.open(collapse_icon_path).resize((16, 16)))

        self.is_expanded = True

        # En-tête
        self.header = tk.Frame(self, bg="#cccccc")
        self.header.pack(fill="x")

        self.button_icon = tk.Button(self.header, image=self.icon_collapse, command=self.toggle, relief="flat", bg="#cccccc")
        self.button_icon.pack(side="left")

        self.label_title = tk.Label(self.header, text=title, bg="#cccccc", font=("Arial", 10, "bold"), anchor="w")
        self.label_title.pack(side="left", padx=5, fill="x", expand=True)

        # Contenu pliable
        self.content = tk.Frame(self, bg="#d3d3d3")
        self.content.pack(fill="both", expand=True)

    def toggle(self):
        if self.is_expanded:
            self.content.forget()
            self.button_icon.config(image=self.icon_expand)
            self.is_expanded = False
        else:
            self.content.pack(fill="both", expand=True)
            self.button_icon.config(image=self.icon_collapse)
            self.is_expanded = True
