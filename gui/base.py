import sys
import os
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from pathlib import Path
import pystray
from PIL import Image
from pathlib import Path
import threading

icon_path = Path(__file__).parent / "assets" / "app.ico"

class StatusGUI(ttk.Window):
    def __init__(self, queue):
        super().__init__(
            title="TNB Torre - Status",
            themename="darkly",
            size=(700, 500),
            resizable=(False, False),
        )

        self.queue = queue

        # Icon
        if icon_path.exists():
            self.iconbitmap(icon_path)

        # Status
        self.status = ttk.Label(
            self,
            text="Aguardando dados...",
            font=("Segoe UI", 11, "bold"),
            bootstyle=INFO,
        )
        self.status.pack(pady=10)

        # Log
        self.log = tk.Text(
            self,
            height=15,
            state="disabled",
            bg="#1e1e1e",
            fg="#dcdcdc",
            insertbackground="white",
            font=("Consolas", 10),
            relief="flat",
        )
        self.log.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        self.after(200, self.poll_queue)

        # Botões inferiores
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=10)

        ttk.Button(
            btn_frame, text="🔄 Reiniciar", bootstyle=(INFO, OUTLINE), command=self.restart_app
        ).pack(side=LEFT)

        ttk.Button(
            btn_frame, text="❌ Encerrar", bootstyle=(DANGER, OUTLINE), command=self.close_app
        ).pack(side=RIGHT)

        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def restart_app(self):
        import subprocess, sys, os

        subprocess.Popen([sys.executable])
        os._exit(0)

    def close_app(self):
        if hasattr(self, "tray_icon"):
            self.tray_icon.stop()
        self.destroy()
        os._exit(0)

    def poll_queue(self):
        while not self.queue.empty():
            msg = self.queue.get()
            self.update_ui(msg)
        self.after(200, self.poll_queue)

    def update_ui(self, msg):
        self.status.config(text=msg)

        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    #Tray
    def create_tray_icon(self):
        if hasattr(self, "tray_icon"):
            return
        
        image = Image.open(icon_path)

        menu = pystray.Menu(
            pystray.MenuItem("Abrir", self.show_window),
            pystray.MenuItem("Sair", self.exit_app)
        )

        self.tray_icon = pystray.Icon(
            "tnb_torre",
            image,
            "TNB Torre",
            menu
        )

        threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        ).start()
    
    def hide_window(self):
        self.withdraw()
        self.create_tray_icon()
        
    def show_window(self, icon=None, item=None):
        self.tray_icon.stop()
        del self.tray_icon
        self.deiconify()
        self.lift()

    def exit_app(self, icon=None, item=None):
        if hasattr(self, "tray_icon"):
            self.tray_icon.stop()
        self.destroy()