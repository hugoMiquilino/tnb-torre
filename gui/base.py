import sys
import os
import tkinter as tk
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from pathlib import Path

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
        icon_path = Path(__file__).parent / "assets" / "app.ico"

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

    def restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def close_app(self):
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
