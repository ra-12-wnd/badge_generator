import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import ImageDraw, ImageFont, Image as PILImage, ImageTk
from organisation.section_pliable import SectionPliable


class ModeVisuelWindow:
    
    def __init__(self, master, config):
        self.config = config
        self.frame = tk.Frame(master, bg="#d3d3d3")  # C'est maintenant un panneau

        self.badge_image = None
        self.polices = ["Arial", "Helvetica", "Times", "Courier", "Calibri"]
        self.style_states = []
        self.couleur_labels = []
        self.trait_entries = []

        self.section_dimensions()
        self.section_polices()
        


        self.section_logo_traits()
        



    def section_dimensions(self):
        section = SectionPliable(self.frame, "Dimensions du Badge                                                                         ")
        section.pack(fill="x", pady=5, padx=10)

        tk.Label(section.content, text="Largeur (mm):", bg="#d3d3d3").grid(row=0, column=0, sticky="w", pady=3)
        self.largeur_entry = tk.Entry(section.content, width=10)
        self.largeur_entry.insert(0, str(self.config["dimensions"]["badge_width_mm"]))
        self.largeur_entry.grid(row=0, column=1, padx=5)

        tk.Label(section.content, text="Hauteur (mm):", bg="#d3d3d3").grid(row=1, column=0, sticky="w", pady=3)
        self.hauteur_entry = tk.Entry(section.content, width=10)
        self.hauteur_entry.insert(0, str(self.config["dimensions"]["badge_height_mm"]))
        self.hauteur_entry.grid(row=1, column=1, padx=5)

    def section_polices(self):
        section = SectionPliable(self.frame, "Polices                                                              ")
        section.pack(fill="x", pady=5, padx=10)

        # Titres des colonnes
        tk.Label(section.content, text="", bg="#d3d3d3").grid(row=0, column=0)
        tk.Label(section.content, text="Type", bg="#d3d3d3", font=("Arial", 9)).grid(row=0, column=1)
        tk.Label(section.content, text="Taille", bg="#d3d3d3", font=("Arial", 9)).grid(row=0, column=2)
        tk.Label(section.content, text="Style", bg="#d3d3d3", font=("Arial", 9)).grid(row=0, column=3, columnspan=3)
        tk.Label(section.content, text="Couleur", bg="#d3d3d3", font=("Arial", 9)).grid(row=0, column=6)

        self.type_widgets, self.size_widgets, self.style_buttons = [], [], []

        for i in range(4):
            row_index = i + 1  # Décalage pour ne pas écraser les titres

            font_name, font_size, style_dict, font_color = self.config["polices"][i]

            self.style_states.append([
                style_dict.get("bold", False),
                style_dict.get("italic", False),
                style_dict.get("underline", False)
            ])

            tk.Label(section.content, text=f"Ligne {i+1}:", bg="#d3d3d3").grid(row=row_index, column=0, sticky="w", padx=5, pady=3)

            cb = ttk.Combobox(section.content, values=self.polices, width=12)
            cb.set(font_name)
            cb.grid(row=row_index, column=1, padx=5, pady=3)
            self.type_widgets.append(cb)

            e = tk.Entry(section.content, width=5)
            e.insert(0, str(font_size))
            e.grid(row=row_index, column=2, padx=5, pady=3)
            self.size_widgets.append(e)

            buttons = []
            for idx, label in enumerate(["G", "I", "S"]):
                b = tk.Button(section.content, text=label, width=2, command=lambda i=i, s=idx: self.toggle_style(i, s))
                b.grid(row=row_index, column=3+idx, padx=2, pady=3)
                buttons.append(b)
            self.style_buttons.append(buttons)

            color_label = tk.Label(section.content, bg=font_color, width=2, relief="solid", borderwidth=1)
            color_label.grid(row=row_index, column=6, padx=10, pady=3)
            color_label.bind("<Button-1>", lambda e, i=i: self.choose_color(i))
            self.couleur_labels.append(color_label)

    def section_logo_traits(self):
        section = SectionPliable(self.frame, "Logo et Traits")
        section.pack(fill="x", pady=5, padx=10)

        tk.Label(section.content, text="Logo :", bg="#d3d3d3").grid(row=0, column=0, sticky="e")

        # 🔧 Créer le champ AVANT de l’utiliser
        self.logo_entry = tk.Entry(section.content, width=50)
        self.logo_entry.grid(row=0, column=1, padx=5, sticky="w")

        # Remplir selon la config
        logo_path = self.config.get("logo_path", "")
        self.default_logo_path = self.config.get("logo_path", "")  # Assurez-vous que ceci soit défini avant si utilisé ailleurs

        if logo_path == self.default_logo_path:
            self.logo_entry.insert(0, "logo par défaut")
        else:
            self.logo_entry.insert(0, logo_path)

        tk.Button(section.content, text="Parcourir", command=self.browse_logo).grid(row=0, column=2, padx=5)

        tk.Label(section.content, text="2 traits du bas :", bg="#d3d3d3").grid(row=1, column=0, sticky="ne", pady=5)

        # Headers
        tk.Label(section.content, text="Largeur", bg="#d3d3d3").grid(row=1, column=1, sticky="", padx=5)
        tk.Label(section.content, text="Couleur", bg="#d3d3d3").grid(row=1, column=2, sticky="", padx=5)

        for i in range(2):
            largeur, couleur = self.config["traits"][1 - i]
            
            entry = tk.Entry(section.content, width=10)
            entry.insert(0, str(largeur))
            entry.grid(row=i+2, column=1, sticky="", pady=2)

            color_label = tk.Label(section.content, bg=couleur, width=2, relief="solid", borderwidth=1)
            color_label.grid(row=i+2, column=2, padx=5)
            color_label.bind("<Button-1>", lambda e, i=i: self.choose_trait_color(i))

            self.trait_entries.append((entry, color_label))
            
    def section_boutons_globaux(self):
        button_frame = tk.Frame(self.frame, bg="#d3d3d3")
        button_frame.pack(pady=15)   # Plus de marge
    def wrap_text_pil(self, draw, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            width = draw.textlength(test_line, font=font)
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines



    def recharger_interface(self):
        """Recharge les champs avec les valeurs actuelles du config."""
        # Largeur / hauteur badge
        self.largeur_entry.delete(0, tk.END)
        self.largeur_entry.insert(0, str(self.config["dimensions"]["badge_width_mm"]))

        self.hauteur_entry.delete(0, tk.END)
        self.hauteur_entry.insert(0, str(self.config["dimensions"]["badge_height_mm"]))

        # Polices (4 lignes)
        for i in range(4):
            font_name, font_size, style_dict, font_color = self.config["polices"][i]

            self.type_widgets[i].set(font_name)
            self.size_widgets[i].delete(0, tk.END)
            self.size_widgets[i].insert(0, str(font_size))
            self.couleur_labels[i].configure(bg=font_color)

            self.style_states[i] = [
                style_dict.get("bold", False),
                style_dict.get("italic", False),
                style_dict.get("underline", False)
            ]

            for j in range(3):
                self.update_style_button(i, j)  # 👈 THIS is what makes buttons visually update


        # Logo
        self.logo_entry.delete(0, tk.END)
        if self.config.get("logo_path", "") == self.default_logo_path:
            self.logo_entry.insert(0, "logo par défaut")
        else:
            self.logo_entry.insert(0, self.config.get("logo_path", ""))

        # Traits
        for i in range(2):
            largeur, couleur = self.config["traits"][i]
            self.trait_entries[i][0].delete(0, tk.END)
            self.trait_entries[i][0].insert(0, str(largeur))
            self.trait_entries[i][1].configure(bg=couleur)
            
    def update_style_button(self, ligne, style_idx):
        btn = self.style_buttons[ligne][style_idx]
        state = self.style_states[ligne][style_idx]
        if state:
            btn.configure(bg="#333", fg="white")  # Active = dark style
        else:
            btn.configure(bg="SystemButtonFace", fg="black")  # Default look

    def generer_apercu(self):
        self.config["dimensions"]["badge_width_mm"] = float(self.largeur_entry.get())
        self.config["dimensions"]["badge_height_mm"] = float(self.hauteur_entry.get())

        for i in range(4):
            font_name = self.type_widgets[i].get()
            font_size = int(self.size_widgets[i].get())
            font_color = self.couleur_labels[i].cget("bg")
            style_dict = {
                "bold": self.style_states[i][0],
                "italic": self.style_states[i][1],
                "underline": self.style_states[i][2]
            }
            self.config["polices"][i] = (font_name, font_size, style_dict, font_color)

        for i in range(2):
            largeur = int(self.trait_entries[i][0].get())
            couleur = self.trait_entries[i][1].cget("bg")
            self.config["traits"][i] = (largeur, couleur)

        #self.config["logo_path"] = self.logo_entry.get()
        saisi = self.logo_entry.get()
        if saisi.strip().lower() == "logo par défaut":
            self.config["logo_path"] = self.default_logo_path
        else:
            self.config["logo_path"] = saisi

        # === Création de l'aperçu complet ===
        dims = self.config["dimensions"]
        interne = self.config["elements_internes"]

        w = int(dims["badge_width_mm"] * 3.78)
        h = int(dims["badge_height_mm"] * 3.78)
        img = PILImage.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(img)

        # Logo
        logo_path = self.config.get("logo_path")
        if logo_path:
            try:
                logo_img = PILImage.open(logo_path).convert("RGBA")
                logo_h = int(h * ((interne["logo_height_ratio"])-0.1))
                logo_img.thumbnail((int(w * 0.5), logo_h))
                logo_y = interne.get("logo_margin_top", 30)
                img.paste(logo_img, (w//2 - logo_img.width//2, logo_y), logo_img)

                y_text = logo_y + logo_img.height + 36  # 👈 Texte commence juste après le logo
            except Exception as e:
                print("Erreur chargement logo :", e)
                y_text = h // 2  # fallback
        else:
            y_text = h // 2

        # Textes d'exemple
        lignes_exemple = ["Nissrine RAOUANE", "Ingénieur en Génie Industriel et Transition Numérique", "nissrineraw@gmail.com", "XXX"]
        #y_text = h // 2

        for idx, texte in enumerate(lignes_exemple):
            police_name, taille, style_dict, couleur = self.config["polices"][idx]

            # Appliquer police avec styles
            font_base = "arial"
            if police_name.lower() == "times":
                font_base = "times"
            elif police_name.lower() == "courier":
                font_base = "cour"

            suffix = ""
            if style_dict.get("bold") and style_dict.get("italic"):
                suffix = "bi"
            elif style_dict.get("bold"):
                suffix = "bd"
            elif style_dict.get("italic"):
                suffix = "i"

            font_path = f"{font_base}{suffix}.ttf"

            try:
                font = ImageFont.truetype(font_path, taille*1.3)
            except:
                font = ImageFont.load_default()

            # Découper le texte en lignes (wrap)
            wrapped_lines = self.wrap_text_pil(draw, texte, font, w * 0.9)

            for line in wrapped_lines:
                draw.text((w/2, y_text), line, font=font, fill=couleur, anchor="mm")
                
                if style_dict.get("underline") and line.strip() != "":
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    underline_y = y_text + taille * 0.7  # Juste sous la ligne
                    draw.line(
                        (w/2 - text_width/2, underline_y, w/2 + text_width/2, underline_y),
                        fill=couleur,
                        width=1
                    )
                
                y_text += taille + 5.5  # espacement régulier
            # Décalage pour la ligne suivante


        # Traits colorés
        # Traits colorés (du bas vers le haut)
        current_y = h - 2
        for largeur_mm, couleur in reversed(self.config["traits"]):
            hauteur_trait_px = int(largeur_mm *1.2)
            draw.rectangle([0, current_y - hauteur_trait_px, w, current_y], fill=couleur)
            current_y -= hauteur_trait_px + 2.3

        # Bordure
        if dims["show_borders"]:
            draw.rectangle([0, 0, w-1, h-1], outline="black", width=1)

        # Affichage dans l'aperçu
        self.badge_image = ImageTk.PhotoImage(img)
        #self.preview_label.config(image=self.badge_image, text="")


    def toggle_style(self, ligne, style_idx, force=None):
        if force is not None:
            self.style_states[ligne][style_idx] = force
        else:
            self.style_states[ligne][style_idx] = not self.style_states[ligne][style_idx]

        btn = self.style_buttons[ligne][style_idx]
        if self.style_states[ligne][style_idx]:
            btn.configure(bg="#333", fg="white")
        else:
            btn.configure(bg="SystemButtonFace", fg="black")

    def choose_color(self, i):
        color = colorchooser.askcolor()[1]
        if color:
            self.couleur_labels[i].configure(bg=color)

    def choose_trait_color(self, i):
        color = colorchooser.askcolor()[1]
        if color:
            self.trait_entries[i][1].configure(bg=color)
            #self.trait_colors[i].set(color)  # 👈 mise à jour ici


    def browse_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.logo_entry.delete(0, tk.END)
            self.logo_entry.insert(0, path)
