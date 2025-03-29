import tkinter as tk
from window import MainWindow


class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(bg='white')
        self.root.title("Biometrics_project_01")

        self.root.state('zoomed')
        self.last_state = self.root.state()

        self.root.bind("<Configure>", self.size_changer)

        self.window = MainWindow(self.root)

    def size_changer(self, event):
        our_state = self.root.state()

        if our_state != self.last_state and our_state == "normal" and self.last_state == "zoomed":
            self.root.geometry("500x500")

        self.last_state = our_state

    def run(self):
        self.root.mainloop()
