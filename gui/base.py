import tkinter as tk
from tkinter import ttk

class StatusGUI(tk.Tk):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

        self.title("TNB Torre - Status")
        self.geometry("600x350")
        self.resizable("False", "False")

        self.status = ttk.Label(
            self,
            text="Aguardando dados...",
            font=("Segoe UI", 11, "bold")
        )
        self.status.pack(pady=10)

        self.log = tk.Text(self, height=15, state="disabled")
        self.log.pack(fill="both", padx=10)

        self.after(200, self.poll_queue)

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