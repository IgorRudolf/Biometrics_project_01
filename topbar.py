import tkinter as tk
from tkinter import filedialog
import os
import webbrowser
import sys

class TopBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack_propagate(False)
        self.configure(bg='lightgray', height=30)

        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label='Read image', command=self.read_image)

        self.file_button = tk.Button(self, text="File", relief=tk.FLAT, bg="lightgray", command=self.show_file_menu)
        self.file_button.pack(side=tk.LEFT)

        #self.settings_menu = tk.Menu(self, tearoff=0)
        #self.settings_menu.add_command(label='Font', command=self.change_font)
        #self.settings_menu.add_command(label='Theme', command=self.change_theme)

        #self.settings_button = tk.Button(self, text="Settings", relief=tk.FLAT, bg="lightgray",
        #                                 command=self.show_settings_menu)
        #self.settings_button.pack(side=tk.LEFT)

        self.help_menu = tk.Menu(self, tearoff=0)
        self.help_menu.add_command(label='Information', command=self.show_information)

        self.help_button = tk.Button(self, text="Help", relief=tk.FLAT, bg="lightgray", command=self.show_help_menu)
        self.help_button.pack(side=tk.LEFT)

        self.counter = 0

    def read_image(self):
        photo_opened = filedialog.askopenfilenames(title='Select a specific photo',
                                                   filetypes=[("Image Files", "*.jpg *.png")])
        if photo_opened:
            main_window = self.master
            self.counter += 1

            if self.counter == 1:
                self.file_menu.add_command(label="Save image", command=self.save_image)

            main_window.image_shower(photo_opened)

    def save_image(self):
        main_window = self.master

        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".jpg",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                main_window.modified_image.save(file_path)
            except Exception as e:
                tk.messagebox.showerror("Save Image", f"Error while saving image: {e}")

    def change_font(self):
        pass

    def change_theme(self):
        window = tk.Toplevel(self)
        window.geometry('300x120')
        window.title("Change Theme Style")

        theme_variant = tk.StringVar(value="light")

        frame = tk.Frame(window)
        frame.pack(pady=20, anchor="center")

        tk.Label(frame, text="Main theme:").pack(side="left")
        tk.Radiobutton(frame, text="Light", variable=theme_variant, value='light').pack(side="left", padx=5)
        tk.Radiobutton(frame, text="Dark", variable=theme_variant, value='dark').pack(side="left", padx=5)

        button_frame = tk.Frame(window)
        button_frame.pack(side="bottom", pady=5)

        def theme_changer():
            chosen_theme = theme_variant.get()
            main_window = self.master
            if hasattr(main_window, "apply_theme"):
                main_window.apply_theme(chosen_theme)
            window.destroy()

        tk.Button(button_frame, text="Ok", command=theme_changer).pack(side="left", padx=3)
        tk.Button(button_frame, text="Cancel", command=window.destroy).pack(side="left", padx=3)

    def show_information(self):
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        pdf_filename = "Sprawozdanie_poprawne_biometria_01_igor_rudolf_327310.pdf"
        pdf_path = os.path.join(base_dir, pdf_filename)
        url = f"file:///{pdf_path}"
        webbrowser.open_new(url)

    def show_file_menu(self):
        x = self.file_button.winfo_rootx()
        y = self.file_button.winfo_rooty() + self.file_button.winfo_height()
        self.file_menu.post(x, y)

    def show_settings_menu(self):
        x = self.settings_button.winfo_rootx()
        y = self.settings_button.winfo_rooty() + self.settings_button.winfo_height()
        self.settings_menu.post(x, y)

    def show_help_menu(self):
        x = self.help_button.winfo_rootx()
        y = self.help_button.winfo_rooty() + self.help_button.winfo_height()
        self.help_menu.post(x, y)
