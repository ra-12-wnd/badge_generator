from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage
from PIL import Image
import io
import pandas as pd
class BadgeGenerator:
    def __init__(self, config):
        self.config = config
        self.default_logo_path = config.get("logo_path", "")

    
    @staticmethod
    def resize_image_keep_aspect(img, max_width, max_height):
        original_width, original_height = img.size
        ratio = min(max_width / original_width, max_height / original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)


    def wrap_text_pdf(self, canvas_obj, text, font_name, font_size, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            width = canvas_obj.stringWidth(test_line, font_name, font_size)
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def generate_pdf(self, df, output_pdf_path):
        dims = self.config["dimensions"]
        interne = self.config["elements_internes"]
        badge_w = dims["badge_width_mm"] * mm
        badge_h = dims["badge_height_mm"] * mm
        margin = dims["margin_mm"] * mm
        spacing = dims["badge_spacing_mm"] * mm

        c = canvas.Canvas(output_pdf_path, pagesize=A4)
        page_w, page_h = A4

        try:
            #logo_img = PILImage.open(self.config["logo_path"]).convert("RGBA")
            try:
                logo_img = Image.open(self.config["logo_path"])

                # Calcul des dimensions max autorisées sur le badge
                logo_w_max = badge_w * 0.75
                logo_h_max = badge_h * interne["logo_height_ratio"]

                # Resize en gardant les proportions (et fix ANTIALIAS obsolète)
                logo_img = self.resize_image_keep_aspect(
                    logo_img, max_width=logo_w_max, max_height=logo_h_max
                )

                buffer = io.BytesIO()
                logo_img.save(buffer, format="PNG")
                logo_reader = ImageReader(buffer)

                # Important : convertir taille réelle du logo (en points)
                final_logo_w_pt = logo_img.width * 0.75  # pixels → points (1 px ≈ 0.75 pt)
                final_logo_h_pt = logo_img.height * 0.75

            except Exception as e:
                print(f"Erreur chargement logo : {e}")
                logo_reader = None
                final_logo_w_pt = 0
                final_logo_h_pt = 0

            buffer = io.BytesIO()

            logo_img.save(buffer, format="PNG")
            logo_reader = ImageReader(buffer)
        except Exception as e:
            print(f"Erreur chargement logo : {e}")
            logo_reader = None

        cols = int((page_w - 2 * margin + spacing) // (badge_w + spacing))
        rows = int((page_h - 2 * margin + spacing) // (badge_h + spacing))
        badges_per_page = cols * rows

        pdf_font_mapping = {
            "Arial": "Helvetica",
            "Calibri": "Helvetica",
            "Times": "Times-Roman",
            "Courier": "Courier"
        }

        for index, row in df.iterrows():
            badge_idx = index % badges_per_page
            col = badge_idx % cols
            row_pos = badge_idx // cols
            x = margin + col * (badge_w + spacing)
            y = page_h - margin - (row_pos + 1) * (badge_h + spacing)

            if dims["show_borders"]:
                c.setStrokeColor(HexColor("#000000")) 
                c.setLineWidth(0.5)
                c.rect(x, y, badge_w, badge_h)

            if logo_reader:
                #logo_w = badge_w * 0.5
                #logo_h = badge_h * interne["logo_height_ratio"]
                logo_x = x + (badge_w - final_logo_w_pt) / 2
                logo_y = y + badge_h - final_logo_h_pt - interne["logo_margin_top"]
                c.drawImage(logo_reader, logo_x, logo_y, width=final_logo_w_pt, height=final_logo_h_pt, mask='auto')

            center_x = x + badge_w / 2
            text_y = y + badge_h / 2

            for i in range(4):
                texte = str(row.iloc[i]) if i < len(row) and pd.notnull(row.iloc[i]) else ""

                font_name, font_size, style_dict, font_color = self.config["polices"][i]
                font_final = pdf_font_mapping.get(font_name, "Helvetica")
                if font_final == "Helvetica":
                    if style_dict.get("bold") and style_dict.get("italic"):
                        font_final = "Helvetica-BoldOblique"
                    elif style_dict.get("bold"):
                        font_final = "Helvetica-Bold"
                    elif style_dict.get("italic"):
                        font_final = "Helvetica-Oblique"
                c.setFont(font_final, font_size)
                c.setFillColor(HexColor(font_color))
                if texte.strip():  # Le texte principal n'est pas vide
                    wrapped_lines = self.wrap_text_pdf(c, texte, font_final, font_size, badge_w * 0.9)

                    for line in wrapped_lines:
                        if not line.strip():
                            continue  # Ne rien faire pour les sous-lignes vides

                        c.drawCentredString(center_x, text_y, line)

                        if style_dict.get("underline"):
                            text_width = c.stringWidth(line, font_final, font_size)
                            underline_y = text_y - font_size * 0.15  # Juste sous la ligne
                            c.setStrokeColor(HexColor(font_color))
                            c.setLineWidth(0.5)
                            c.line(center_x - text_width / 2, underline_y, center_x + text_width / 2, underline_y)

                        text_y -= font_size + 2

                #text_y -= font_size +1

            current_y = y  # position de départ en bas du badge

            for largeur_mm, couleur in reversed(self.config["traits"]):  # ordre inversé pour dessiner de bas en haut
                hauteur_pt = (largeur_mm * mm)/2.5 # conversion mm → points
                c.setFillColor(HexColor(couleur))
                c.rect(x, current_y, badge_w, hauteur_pt, fill=1, stroke=0)
                current_y += (hauteur_pt + 2) # espacement entre les traits


            if (index + 1) % badges_per_page == 0:
                c.showPage()

        if len(df) % badges_per_page != 0:
            c.showPage()

        c.save()
        print(f"✅ PDF généré : {output_pdf_path}")
