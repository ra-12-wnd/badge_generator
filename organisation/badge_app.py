import tkinter as tk
from tkinter import filedialog
import pandas as pd
from organisation.badge_generator import BadgeGenerator
from organisation.config import default_config
import copy
from organisation.mode_visuel import ModeVisuelWindow


class BadgeApp:
    def __init__(self, root, config):
        self.root = root
        # Start from a fresh copy of the default configuration
        self.config = copy.deepcopy(default_config)
        # Window setup
        self.root.title("Générateur de Badges - RAWND")
        self.root.geometry("940x580")
        # Prevent excessive resizing
        self.root.minsize(940, 580)
        self.root.maxsize(940, 580)

        self.root.configure(bg="#d3d3d3")
        self.generator = BadgeGenerator(self.config)
        
        self.create_widgets()

    def create_widgets(self):
        # Top area: file picker
        top_frame = tk.Frame(self.root, bg="#d3d3d3")
        top_frame.pack(fill="x", pady=10)

        tk.Label(top_frame, text="Fichier Excel :", bg="#d3d3d3", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.excel_entry = tk.Entry(top_frame, width=50)
        self.excel_entry.pack(side="left", padx=5)
        tk.Button(top_frame, text="Parcourir", bg="#062f66", fg="white", command=self.browse_file).pack(side="left", padx=10)

        # Middle area: settings on the left + preview on the right
        self.center_frame = tk.Frame(self.root, bg="#d3d3d3")  # Important container
        self.center_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Settings panel (visual mode embedded)
        self.visuel_panel = ModeVisuelWindow(self.center_frame, self.config)
        self.visuel_panel.frame.pack(side="left", fill="y", expand=False, padx=5, pady=10)
        
        # Preview area
        self.preview_frame = tk.Frame(
            self.center_frame,
            width=550,
            height=320,
            bg="white",
            highlightbackground="#cccccc",
            highlightthickness=1
        )
        self.preview_frame.pack_propagate(False)

        self.preview_frame.pack(side="right", padx=5, pady=10)

        self.preview_label = tk.Label(self.preview_frame, text="Zone d’aperçu", font=("Arial", 12, "bold"), fg="gray", bg="white")
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Partie inférieure : boutons globaux
        bottom_frame = tk.Frame(self.root, bg="#d3d3d3")
        
        bottom_frame.pack(fill="x", pady=(5, 30))  # 👈 Réduit l'espace avant les boutons


        # Bottom area: global buttons
        buttons_frame = tk.Frame(bottom_frame, bg="#d3d3d3")
        buttons_frame.pack()

        # Side-by-side buttons
        tk.Button(buttons_frame, text="Réinitialiser", bg="#888888", fg="white", width=15, command=self.reset_config).pack(side="left", padx=15)
        tk.Button(buttons_frame, text="Valider & Aperçu", bg="#062f66", fg="white", width=15, command=self.generer_apercu).pack(side="left", padx=15)
        tk.Button(buttons_frame, text="Générer PDF", bg="#006600", fg="white", width=15, command=self.generer_pdf).pack(side="left", padx=15)

        # === Status area — just below the buttons ===
        self.status_label = tk.Label(
            bottom_frame,
            text="",
            bg="#d3d3d3",
            fg="blue",
            font=("Arial", 9, "italic")
        )
        self.status_label.pack(pady=(6, 0))



    def set_status(self, message, color="blue"):
        self.status_label.config(text=message, fg=color)
        self.status_label.update_idletasks()

    def generer_apercu(self):
        self.set_status("Mise à jour des paramètres...", "blue")
        self.visuel_panel.generer_apercu()
        self.preview_label.config(image=self.visuel_panel.badge_image, text="")
        self.set_status("Aperçu généré avec succès", "green")

    def reset_config(self):
        import copy
        from organisation.config import default_config

        # 1. Deep copy of config to reset all values
        self.config = copy.deepcopy(default_config)
        self.generator = BadgeGenerator(self.config)

        # 2. Clear Excel field
        self.excel_entry.delete(0, tk.END)

        # 3. Reset status label
        self.set_status("")

        # 4. Update visual panel's config and reload its interface
        if self.visuel_panel:
            self.visuel_panel.config = self.config
            self.visuel_panel.recharger_interface()

        # 5. Clear preview image and reset label
        self.preview_label.config(image="", text="Zone d’aperçu", fg="gray")
        self.preview_label.image = None  # optional: prevent memory leak

    # File picker dialog

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Sélectionner un fichier Excel", filetypes=[("Fichiers Excel", "*.xlsx *.xls *.csv")])
        if filename:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, filename)

    def generer_pdf(self):
        excel_path = self.excel_entry.get()
        if not excel_path:
            self.set_status("⚠️ Aucun fichier Excel sélectionné.", "red")
            return

        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            self.set_status(f"Erreur lecture Excel : {e}", "red")
            return

        output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_pdf_path:
            self.set_status("Génération du PDF en cours...", "blue")
            try:
                self.generator.generate_pdf(df, output_pdf_path)
                self.set_status("✅ PDF généré avec succès", "green")
            except Exception as e:
                self.set_status(f"❌ Erreur génération PDF : {e}", "red")
