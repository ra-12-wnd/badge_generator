from organisation.utils import resource_path
default_config = {
    "dimensions": {
        "badge_width_mm": 85,
        "badge_height_mm": 54,
        "margin_mm": 0,
        "badge_spacing_mm": 0,
        "show_borders": True
    },
    "elements_internes": {
        "logo_height_ratio": 0.35,
        "logo_margin_top": 15,
        "name_offset_y": 1,
        "function_offset_y": 0,
        "line_height": 3.5,
        "line_spacing": 2
    },
    "polices": [
        ("Helvetica-Bold", 16, {}, "#000000"),
        ("Helvetica", 14, {}, "#000000"),
        ("Helvetica", 12, {}, "#000000"),
        ("Helvetica", 10, {}, "#000000")
    ],
    "traits": [
        
        
        (3, "#0033B3"),
        (3, "#FF8000")
    ],
    "logo_path": resource_path("organisation/assets/logo se 1.png"),
    "text_color": "#000000"
}
