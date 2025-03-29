import tkinter as tk
from topbar import TopBar
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from image_processing import ImageProcessor
from tkinter import messagebox
from graphics_filter import apply_gaussian_filter, apply_sharpening_filter, apply_averaging_filter
from edge_detection import (roberts_cross_own_working_way, sobel_operator_own_working_way,
                            scharr_operator_own_working_way, laplace_operator_own_working_way)
from operation_reversor import OperationReversor
from looks_options import DARK_THEME, LIGHT_THEME
import numpy as np


class ModernTheme:
    BACKGROUND_LIGHT = "#F0F4F8"
    BACKGROUND_DARK = "#1E2A38"
    PRIMARY_COLOR = "#3B82F6"
    SECONDARY_COLOR = "#10B981"
    TEXT_COLOR_LIGHT = "#1F2937"
    TEXT_COLOR_DARK = "#F9FAFB"
    PANEL_BACKGROUND = "#FFFFFF"
    BUTTON_COLOR = "#3B82F6"
    BUTTON_HOVER = "#2563EB"


def plot_gray_histogram_in_frame(frame, image, title="Histogram"):

    gray = image.convert("L")
    hist = gray.histogram()

    fig, ax = plt.subplots(figsize=(3, 2), dpi=100)
    fig.patch.set_facecolor("#f5f5f5")
    ax.set_facecolor('#FCFCFC')

    ax.bar(range(256), hist, width=1, color="gray", edgecolor="black")
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Intensity", fontsize=8)
    ax.set_ylabel("Count", fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, anchor="center")
    return canvas


def project_image(image, projection_type, return_projection=False):
    if image.mode != "L":
        image = image.convert("L")

    img_array = np.array(image)
    height, width = img_array.shape

    if projection_type == "Horizontal":
        projection = np.sum(img_array, axis=1).astype(np.float32)
        if np.max(projection) > 0:
            projection /= np.max(projection)
            projection *= 255.0

        result_array = img_array.copy()
        if return_projection:
            return Image.fromarray(result_array), projection
        return Image.fromarray(result_array)

    elif projection_type == "Vertical":
        projection = np.sum(img_array, axis=0).astype(np.float32)
        if np.max(projection) > 0:
            projection /= np.max(projection)
            projection *= 255.0

        result_array = img_array.copy()
        if return_projection:
            return Image.fromarray(result_array), projection
        return Image.fromarray(result_array)

    else:
        if return_projection:
            empty_projection = np.zeros(height if projection_type == "Horizontal" else width, dtype=np.float32)
            return image, empty_projection
        return image


class MainWindow(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(bg=ModernTheme.BACKGROUND_LIGHT)
        self.current_theme = "light"
        self.pack(fill='both', expand=True)

        self.vertical_projection_container = None
        self.horizontal_projection_container = None

        self.create_widgets()
        self.show_welcome_message()

        self.original_image = None
        self.modified_image = None

        self.horizontal_projection_on = False
        self.vertical_projection_on = False

        self.operation_reverse = OperationReversor()
        self.custom_weight_matrix = None

    def show_welcome_message(self):
        self.welcome_label = tk.Label(
            self.content,
            text="Biometrics project 01",
            font=("Helvetica", 48),
            bg="white"
        )
        self.welcome_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75)

        self.sub_label = tk.Label(
            self.content,
            text="Igor Rudolf (the application works for JPG files)",
            font=("Helvetica", 24),
            bg="white"
        )
        self.sub_label.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.75)

    def hide_welcome_message(self):
        if hasattr(self, "welcome_label"):
            self.welcome_label.destroy()
        if hasattr(self, "sub_label"):
            self.sub_label.destroy()

    def apply_theme(self, theme):
        self.current_theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME

        self.configure(bg=colors["bg_main"])
        self.content.configure(bg=colors["bg_main"])

        self.top_bar.configure(bg=colors["bg_panel"])
        self.top_bar.file_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])
        #self.top_bar.settings_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])
        self.top_bar.help_button.configure(bg=colors["button_bg"], fg=colors["button_fg"])

        self.update()

    def create_widgets(self):
        self.top_bar = TopBar(self)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)

        self.content = tk.Frame(self, bg='white')
        self.content.pack(fill='both', expand=True)

    def reverse_current_operation(self):
        try:
            if not self.operation_reverse.can_reverse():
                messagebox.showinfo("Info", "Cannot reverse the operation because one doesn't exist.")
                return

            self.modified_image = self.operation_reverse.pop()
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_matrix_event(self):
        kernel_value = self.kernel_entry.get().strip()
        if not kernel_value:
            messagebox.showinfo("Error", "Enter kernel size.")
            return

        try:
            ksize = int(kernel_value)
            if ksize < 2:
                messagebox.showinfo("Error", "Kernel size must be at least 2.")
                return
        except ValueError:
            messagebox.showinfo("Error", "Kernel size must be an integer.")
            return

        matrix_window = tk.Toplevel(self)
        matrix_window.title("Set your custom kernel")
        self.custom_weight_entries = []

        for r in range(ksize):
            row_entries = []
            for c in range(ksize):
                e = tk.Entry(matrix_window, width=5, font=("Helvetica", 8))
                e.grid(row=r, column=c, padx=3, pady=3)
                row_entries.append(e)
            self.custom_weight_entries.append(row_entries)

        btn_frame = tk.Frame(matrix_window)
        btn_frame.grid(row=ksize, column=0, columnspan=ksize, pady=10)

        def on_ok():
            custom_matrix = []
            try:
                for row in self.custom_weight_entries:
                    custom_row = []
                    for entry in row:
                        val = float(entry.get().strip())
                        custom_row.append(val)
                    custom_matrix.append(custom_row)
            except ValueError as err:
                messagebox.showinfo("Error", err)
                return

            if all(all(v == 0 for v in row) for row in custom_matrix):
                messagebox.showinfo("Error", "All weights combined must be not zero.")
                return

            self.custom_weight_matrix = custom_matrix
            matrix_window.destroy()

        def on_cancel():
            matrix_window.destroy()

        tk.Button(btn_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)

    def update_modified_histogram(self):
        for widget in self.hist_modified_panel.winfo_children():
            widget.destroy()

        if self.modified_image:
            plot_gray_histogram_in_frame(self.hist_modified_panel, self.modified_image, "Modified Histogram")

    def image_shower(self, files):
        self.hide_welcome_message()

        for widget in self.content.winfo_children():
            widget.destroy()

        panel_frame = tk.Frame(self.content, bg='white')
        panel_frame.pack(fill="both", expand=True)
        panel_frame.grid_rowconfigure(0, weight=1)
        panel_frame.grid_columnconfigure(0, weight=3)
        panel_frame.grid_columnconfigure(1, weight=7)

        self.left_panel = tk.Frame(panel_frame, bg='white')
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        top_left_container = tk.Frame(self.left_panel, bg="#F0F0F0")
        top_left_container.pack(side="top", fill="x", padx=5, pady=5)
        top_left_container.grid_columnconfigure(0, weight=1)
        top_left_container.grid_columnconfigure(1, weight=1)

        self._create_operations_frame(top_left_container)
        self._create_graphics_frame(top_left_container)

        projection_frame = tk.LabelFrame(
            self.left_panel,
            text="Projection",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        projection_frame.pack(side="top", fill="x", padx=5, pady=5)

        btn_horizontal = tk.Button(projection_frame, text="Horizontal", font=("Helvetica", 8), bg="lightgray",
                                   command=self.show_horizontal_projection)
        btn_vertical = tk.Button(projection_frame, text="Vertical", font=("Helvetica", 8), bg="lightgray",
                                 command=self.show_vertical_projection)
        btn_none = tk.Button(projection_frame, text="None", font=("Helvetica", 8), bg="lightgray",
                             command=self.hide_projections)

        btn_horizontal.pack(side="left", padx=5, pady=5)
        btn_vertical.pack(side="left", padx=5, pady=5)
        btn_none.pack(side="left", padx=5, pady=5)

        weights_container = tk.Frame(self.left_panel, bg="#F0F0F0")
        weights_container.pack(side="top", fill="x", padx=5, pady=5)

        self._create_weights_frame(weights_container)
        self._create_reverse_frame(weights_container)
        self._create_edge_frame(self.left_panel)

        hist_container = tk.Frame(self.left_panel, bg="#F0F0F0")
        hist_container.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.hist_original_panel = tk.Frame(hist_container, bg="green")
        self.hist_original_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.hist_modified_panel = tk.Frame(hist_container, bg="pink")
        self.hist_modified_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.right_panel = tk.Frame(panel_frame, bg="green")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.top_subpanel = tk.Frame(self.right_panel, bg="#FCFCFC")
        self.top_subpanel.grid(row=0, column=0, sticky="nsew")
        self.top_subpanel.grid_rowconfigure(0, weight=1)
        self.top_subpanel.grid_columnconfigure(0, weight=1)
        self.top_subpanel.grid_columnconfigure(1, weight=0)

        self.image_container = tk.Frame(self.top_subpanel, bg="#FCFCFC")
        self.image_container.grid(row=0, column=0, columnspan=2, sticky="nsew")

        modified_label = tk.Label(
            self.image_container,
            text="Modified Image",
            font=("Helvetica", 8, "bold"),
            bg="#FCFCFC",
            fg="black"
        )
        modified_label.pack(side="top", anchor="w", padx=5, pady=5)

        self.bottom_subpanel = tk.Frame(self.right_panel, bg="#EBEBEB")
        self.bottom_subpanel.grid(row=1, column=0, sticky="nsew")

        original_label = tk.Label(
            self.bottom_subpanel,
            text="Original Image",
            font=("Helvetica", 8, "bold"),
            bg="#EBEBEB",
            fg="black"
        )
        original_label.pack(side="top", anchor="w", padx=5, pady=5)

        panel_frame.update_idletasks()

        image_path = files[0]
        print("Wybrano plik:", image_path)
        try:
            self.original_image = Image.open(image_path)
            self.modified_image = self.original_image.copy()
        except Exception as e:
            print("Błąd podczas otwierania obrazu:", e)
            return

        self._display_image_in_panel(self.image_container, self.modified_image)
        self._display_image_in_panel(self.bottom_subpanel, self.original_image)

        plot_gray_histogram_in_frame(self.hist_original_panel, self.original_image, "Original Histogram")
        plot_gray_histogram_in_frame(self.hist_modified_panel, self.modified_image, "Modified Histogram")

        self.update_projections()

    def _create_operations_frame(self, parent):
        self.operations_frame = tk.LabelFrame(
            parent,
            text="Operations on pixels",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        self.operations_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        title_label = tk.Label(
            self.operations_frame,
            text="Basic operations",
            bg="#F0F0F0",
            fg="black",
            font=("Helvetica", 8, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        btn_shades = tk.Button(
            self.operations_frame,
            text="Shades of gray",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_shades_of_gray
        )
        btn_negative = tk.Button(
            self.operations_frame,
            text="Negative",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_negative
        )

        btn_shades.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        btn_negative.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        label_brightness = tk.Label(
            self.operations_frame,
            text="Korekta jasności",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        label_brightness.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.brightness_scale = tk.Scale(
            self.operations_frame,
            from_=0,
            to=200,
            orient="horizontal",
            resolution=1,
            length=150
        )
        self.brightness_scale.set(100)
        self.brightness_scale.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        self.brightness_scale.bind("<ButtonRelease-1>", self.apply_brightness)

        label_contrast = tk.Label(
            self.operations_frame,
            text="Korekta kontrastu",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        label_contrast.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.contrast_scale = tk.Scale(
            self.operations_frame,
            from_=0,
            to=200,
            orient="horizontal",
            resolution=1,
            length=150
        )
        self.contrast_scale.set(100)
        self.contrast_scale.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        self.contrast_scale.bind("<ButtonRelease-1>", self.apply_contrast)

        self.label_biner = tk.Label(
            self.operations_frame,
            text="Binerization",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        self.label_biner.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.biner_scale = tk.Scale(
            self.operations_frame,
            from_=0,
            to=255,
            orient="horizontal",
            resolution=1,
            length=150
        )
        self.biner_scale.set(128)
        self.biner_scale.grid(row=7, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="we")
        self.biner_scale.bind("<ButtonRelease-1>", self.apply_binarization)

    def _create_graphics_frame(self, parent):
        self.graphics_frame = tk.LabelFrame(
            parent,
            text="Graphics filters",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        self.graphics_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        gaussian_frame = tk.LabelFrame(
            self.graphics_frame,
            text="Gaussian filter",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=1,
            relief="groove"
        )
        gaussian_frame.pack(side="top", fill="x", padx=5, pady=5)

        sigma_label = tk.Label(
            gaussian_frame,
            text="Sigma:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        sigma_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.gaussian_sigma_scale = tk.Scale(
            gaussian_frame,
            from_=0.5,
            to=10,
            resolution=0.1,
            orient="horizontal",
            length=150
        )
        self.gaussian_sigma_scale.set(1.0)
        self.gaussian_sigma_scale.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.gaussian_sigma_scale.bind("<ButtonRelease-1>", self.apply_gaussian_filter_event)

        kernel_label = tk.Label(
            gaussian_frame,
            text="Kernel size:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        kernel_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.gaussian_kernel_entry = tk.Entry(gaussian_frame, width=5, font=("Helvetica", 8))
        self.gaussian_kernel_entry.insert(0, "3")
        self.gaussian_kernel_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        sharpening_frame = tk.LabelFrame(
            self.graphics_frame,
            text="Sharpening filter",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=1,
            relief="groove"
        )
        sharpening_frame.pack(side="top", fill="x", padx=5, pady=5)

        intensity_label = tk.Label(
            sharpening_frame,
            text="Intensity:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        intensity_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.sharpening_intensity_scale = tk.Scale(
            sharpening_frame,
            from_=0,
            to=5,
            resolution=0.1,
            orient="horizontal",
            length=150
        )
        self.sharpening_intensity_scale.set(1.0)
        self.sharpening_intensity_scale.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.sharpening_intensity_scale.bind("<ButtonRelease-1>", self.apply_sharpening_filter_event)

        sharpen_kernel_label = tk.Label(
            sharpening_frame,
            text="Kernel size:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        sharpen_kernel_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.sharpen_kernel_entry = tk.Entry(sharpening_frame, width=5, font=("Helvetica", 8))
        self.sharpen_kernel_entry.insert(0, "3")
        self.sharpen_kernel_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        averaging_frame = tk.LabelFrame(
            self.graphics_frame,
            text="Averaging filter",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=1,
            relief="groove"
        )
        averaging_frame.pack(side="top", fill="x", padx=5, pady=5)

        averaging_kernel_label = tk.Label(
            averaging_frame,
            text="Kernel size:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        averaging_kernel_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.averaging_kernel_entry = tk.Entry(averaging_frame, width=5, font=("Helvetica", 8))
        self.averaging_kernel_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.averaging_kernel_entry.bind("<Return>", self.apply_averaging_filter_event)

    def _create_weights_frame(self, parent):
        weights_frame = tk.LabelFrame(
            parent,
            text="Weights Creator",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        weights_frame.pack(side="left", padx=(0, 5), pady=0)

        size_label = tk.Label(
            weights_frame,
            text="Kernel size:",
            font=("Helvetica", 8),
            bg="#F0F0F0",
            fg="black"
        )
        size_label.pack(side="left", padx=5, pady=5)

        self.kernel_entry = tk.Entry(weights_frame, width=5, font=("Helvetica", 8))
        self.kernel_entry.pack(side="left", padx=5, pady=5)

        set_button = tk.Button(
            weights_frame,
            text="Set matrix",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.set_matrix_event
        )
        set_button.pack(side="left", padx=5, pady=5)

    def _create_reverse_frame(self, parent):
        reverse_frame = tk.LabelFrame(
            parent,
            text="Reverse Operation",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        reverse_frame.pack(side="left", padx=0, pady=0)

        back_button = tk.Button(
            reverse_frame,
            text="Back",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.reverse_current_operation
        )
        back_button.pack(side="left", padx=5, pady=5)

    def _create_edge_frame(self, parent):
        edge_frame = tk.LabelFrame(
            parent,
            text="Edge detection",
            font=("Helvetica", 8, "bold"),
            bg="#F0F0F0",
            fg="black",
            bd=2,
            relief="groove"
        )
        edge_frame.pack(side="top", fill="x", padx=5, pady=5)

        btn_roberts = tk.Button(
            edge_frame,
            text="Robert's cross",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_roberts_cross_event
        )
        btn_sobel = tk.Button(
            edge_frame,
            text="Sobel operator",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_sobel_operator_event
        )
        btn_scharr = tk.Button(
            edge_frame,
            text="Scharr operator",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_scharr_operator_event
        )
        btn_laplace = tk.Button(
            edge_frame,
            text="Laplace operator",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_laplace_operator_event
        )
        btn_custom = tk.Button(
            edge_frame,
            text="Custom Detection",
            font=("Helvetica", 8),
            bg="lightgray",
            command=self.apply_custom_detection_event
        )

        btn_roberts.pack(side="left", padx=5, pady=5)
        btn_sobel.pack(side="left", padx=5, pady=5)
        btn_scharr.pack(side="left", padx=5, pady=5)
        btn_laplace.pack(side="left", padx=5, pady=5)
        btn_custom.pack(side="left", padx=5, pady=5)

    def apply_roberts_cross_event(self, event=None):
        self.operation_reverse.push(self.modified_image)
        try:
            new_image = roberts_cross_own_working_way(self.modified_image, None)
            self.modified_image = new_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()
        except Exception as e:
            messagebox.showerror("Error", f"Roberts operator error: {str(e)}")

    def apply_sobel_operator_event(self, event=None):
        self.operation_reverse.push(self.modified_image)
        try:
            new_image = sobel_operator_own_working_way(self.modified_image, None)
            self.modified_image = new_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()
        except Exception as e:
            messagebox.showerror("Error", f"Sobel operator error: {str(e)}")

    def apply_scharr_operator_event(self, event=None):
        self.operation_reverse.push(self.modified_image)
        try:
            new_image = scharr_operator_own_working_way(self.modified_image, None)
            self.modified_image = new_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()
        except Exception as e:
            messagebox.showerror("Error", f"Scharr operator error: {str(e)}")

    def apply_laplace_operator_event(self, event=None):
        self.operation_reverse.push(self.modified_image)
        try:
            new_image = laplace_operator_own_working_way(self.modified_image, None)
            self.modified_image = new_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()
        except Exception as e:
            messagebox.showerror("Error", f"Laplace operator error: {str(e)}")

    def apply_custom_detection_event(self, event=None):
        if self.custom_weight_matrix is None:
            messagebox.showinfo("Error", "Please set a custom matrix (minimum size 2x2).")
            return

        size = len(self.custom_weight_matrix)
        if size not in (2, 3) or any(len(row) != size for row in self.custom_weight_matrix):
            messagebox.showinfo("Error", "Custom matrix must be 2x2 or 3x3.")
            return

        self.operation_reverse.push(self.modified_image)
        try:
            if size == 2:
                new_image = roberts_cross_own_working_way(self.modified_image, self.custom_weight_matrix)
            else:
                new_image = sobel_operator_own_working_way(self.modified_image, self.custom_weight_matrix)

            self.modified_image = new_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()

        except Exception as e:
            messagebox.showerror("Error", f"Custom detection error: {str(e)}")

    def show_horizontal_projection(self):
        if not self.modified_image:
            print("No image loaded.")
            return
        self.horizontal_projection_on = True
        self.update_projections()

    def show_vertical_projection(self):
        if not self.modified_image:
            print("No image loaded.")
            return
        self.vertical_projection_on = True
        self.update_projections()

    def hide_projections(self):
        self.horizontal_projection_on = False
        self.vertical_projection_on = False
        self.update_projections()

    def update_projections(self):

        if not self.horizontal_projection_on and not self.vertical_projection_on:
            if self.vertical_projection_container:
                self.vertical_projection_container.destroy()
                self.vertical_projection_container = None
            if self.horizontal_projection_container:
                self.horizontal_projection_container.destroy()
                self.horizontal_projection_container = None

            self.top_subpanel.grid_columnconfigure(0, weight=1)
            self.top_subpanel.grid_columnconfigure(1, weight=0)

            self.image_container.grid_forget()
            self.image_container.grid(row=0, column=0, columnspan=2, sticky="nsew")

        else:
            self.top_subpanel.grid_columnconfigure(0, weight=1)
            self.top_subpanel.grid_columnconfigure(1, weight=0)

            self.image_container.grid_forget()
            self.image_container.grid(row=0, column=0, sticky="nsew")

            if self.vertical_projection_on:
                if self.vertical_projection_container:
                    self.vertical_projection_container.destroy()

                self.vertical_projection_container = tk.Frame(self.top_subpanel, bg="white", width=100)
                self.vertical_projection_container.grid(row=0, column=1, sticky="ns")
                _, proj_data_v = project_image(self.modified_image, "Vertical", return_projection=True)
                self._display_vertical_projection(proj_data_v)
            else:
                if self.vertical_projection_container:
                    self.vertical_projection_container.destroy()
                    self.vertical_projection_container = None

            if self.horizontal_projection_on:
                if self.horizontal_projection_container:
                    self.horizontal_projection_container.destroy()

                self.horizontal_projection_container = tk.Frame(self.top_subpanel, bg="white", height=100)
                self.horizontal_projection_container.grid(row=1, column=0, columnspan=2, sticky="ew")
                _, proj_data_h = project_image(self.modified_image, "Horizontal", return_projection=True)
                self._display_horizontal_projection(proj_data_h)
            else:
                if self.horizontal_projection_container:
                    self.horizontal_projection_container.destroy()
                    self.horizontal_projection_container = None

    def _display_horizontal_projection(self, projection_data):
        fig, ax = plt.subplots(figsize=(6, 1.5), dpi=80)
        ax.plot(projection_data, color="black", linewidth=1)
        ax.set_title("Horizontal Projection", fontsize=8)
        ax.set_xlim(0, len(projection_data))
        ax.set_yticks([])
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.horizontal_projection_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _display_vertical_projection(self, projection_data):
        fig, ax = plt.subplots(figsize=(2, 4), dpi=80)
        y_values = np.arange(len(projection_data))
        ax.plot(projection_data, y_values, color="blue", linewidth=1)
        ax.set_title("Vertical Projection", fontsize=8)
        ax.set_ylim(0, len(projection_data))
        ax.set_xlim(0, np.max(projection_data) * 1.05 if np.max(projection_data) > 0 else 1)
        ax.invert_yaxis()
        ax.set_xticks([])
        ax.set_yticks([])
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.vertical_projection_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def apply_averaging_filter_event(self, event=None):
        kernel_value = self.averaging_kernel_entry.get().strip()
        if not kernel_value:
            messagebox.showinfo("Missing Input", "Input kernel size")
            return

        self.operation_reverse.push(self.modified_image)
        try:
            kernel_size = int(kernel_value)
            if kernel_size % 2 == 0:
                messagebox.showinfo("Invalid Input", "Kernel size must be odd.")
                return
        except ValueError:
            messagebox.showinfo("Invalid Input", "Kernel size must be an integer.")
            return

        filtered_img = apply_averaging_filter(self.modified_image, kernel_size)
        self.modified_image = filtered_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        self.update_modified_histogram()
        self.update_projections()

    def apply_sharpening_filter_event(self, event=None):
        kernel_value = self.sharpen_kernel_entry.get().strip()
        if not kernel_value:
            messagebox.showinfo("Input a kernel size")
            return

        self.operation_reverse.push(self.modified_image)
        try:
            kernel_size = int(kernel_value)
            if kernel_size % 2 == 0:
                messagebox.showinfo("Invalid Input", "Kernel size is not odd")
                return
        except ValueError:
            messagebox.showinfo("Invalid Input", "Write number as input.")
            return

        intensity_value = self.sharpening_intensity_scale.get()
        if not self.modified_image:
            return

        try:
            filtered_image = apply_sharpening_filter(self.modified_image, kernel_size, intensity_value)
            self.modified_image = filtered_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()
        except Exception as e:
            messagebox.showerror("Error", f"Some error appeared: {str(e)}")

    def apply_gaussian_filter_event(self, event=None):
        kernel_value = self.gaussian_kernel_entry.get().strip()
        if not kernel_value:
            messagebox.showinfo("Invalid Input", "Kernel size is not odd")
            return

        self.operation_reverse.push(self.modified_image)
        try:
            kernel_size = int(kernel_value)
            if kernel_size % 2 == 0:
                messagebox.showinfo("Invalid Input", "Kernel size is not odd")
                return
        except ValueError as err:
            messagebox.showerror("Error", f"Some error appeared: {str(err)}")
            return

        sigma_value = self.gaussian_sigma_scale.get()
        if not self.modified_image:
            print("No image loaded.")
            return

        try:
            filtered_image = apply_gaussian_filter(self.modified_image, kernel_size, sigma_value)
            self.modified_image = filtered_image
            self._display_image_in_panel(self.image_container, self.modified_image)
            self.update_modified_histogram()
            self.update_projections()

            print(f"kernel size: {kernel_size}, sigma: {sigma_value}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot apply gaussian cause: {str(e)}")
            print(f"Error: {e}")

    def apply_binarization(self, event=None):
        self.operation_reverse.push(self.modified_image)
        threshold = self.biner_scale.get()
        current_img = self.modified_image
        binarized_img = ImageProcessor.binarize(current_img, int(threshold))
        self.modified_image = binarized_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        self.update_modified_histogram()
        self.update_projections()

    def apply_contrast(self, event=None):
        if not self.modified_image:
            print("No image to adjust contrast.")
            return

        self.operation_reverse.push(self.modified_image)
        contrast_value = self.contrast_scale.get()
        factor = contrast_value / 100.0

        current_img = self.modified_image
        adjusted_img = ImageProcessor.adjust_contrast(current_img, factor)
        self.modified_image = adjusted_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        print(f"Applied contrast adjustment: {contrast_value}% (factor={factor:.2f})")

        self.update_modified_histogram()
        self.update_projections()

    def apply_brightness(self, event=None):
        if not self.modified_image:
            print("Brak obrazu.")
            return

        self.operation_reverse.push(self.modified_image)
        brightness_value = self.brightness_scale.get()
        factor = brightness_value / 100.0

        current_img = self.modified_image
        adjusted_img = ImageProcessor.adjust_brightness(current_img, factor)
        self.modified_image = adjusted_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        self.update_modified_histogram()
        self.update_projections()

    def apply_shades_of_gray(self):
        if not self.modified_image:
            print("Brak obrazu.")
            return

        self.operation_reverse.push(self.modified_image)
        gray_img = ImageProcessor.to_grayscale(self.modified_image)
        self.modified_image = gray_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        self.update_modified_histogram()
        self.update_projections()

    def apply_negative(self):
        if not self.modified_image:
            print("Brak obrazu.")
            return

        self.operation_reverse.push(self.modified_image)
        negative_img = ImageProcessor.to_negative(self.modified_image)
        self.modified_image = negative_img
        self._display_image_in_panel(self.image_container, self.modified_image)
        print("Przetworzono obraz do negatywu.")

        self.update_modified_histogram()
        self.update_projections()

    def _display_image_in_panel(self, panel, image):
        panel.update_idletasks()
        panel_width = panel.winfo_width()
        panel_height = panel.winfo_height()

        avail_width = int(panel_width * 0.95)
        avail_height = int(panel_height * 0.95)

        if isinstance(image, str):
            try:
                img = Image.open(image)
            except Exception as e:
                print("Error loading image:", e)
                return
        else:
            img = image

        orig_width, orig_height = img.size
        scale = min(avail_width / orig_width, avail_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        image_resized = img.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image_resized)

        if not hasattr(panel, "image_container"):
            container = tk.Frame(panel, bg=panel.cget("bg"))
            container.pack(expand=True, fill="both", padx=5, pady=5)
            panel.image_container = container
        else:
            container = panel.image_container
            for widget in container.winfo_children():
                widget.destroy()

        label = tk.Label(container, image=photo, bg=container.cget("bg"))
        label.image = photo
        label.place(relx=0.5, rely=0.5, anchor="center")

        self.update_projections()
