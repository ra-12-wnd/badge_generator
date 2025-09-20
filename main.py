import tkinter as tk
from organisation.config import default_config
from organisation.badge_app import BadgeApp
import os
import sys
from organisation.utils import resource_path


if __name__ == "__main__":
    root = tk.Tk()
    
    # Load icon
    icon_path = resource_path("organisation/assets/monlogoRAWND.ico")
    root.iconbitmap(icon_path)

    app = BadgeApp(root, default_config)
    root.mainloop()
