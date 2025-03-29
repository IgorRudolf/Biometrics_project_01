# Biometrics Application 01

**Biometrics Application 01** is an image processing and edge detection desktop app developed as part of my college coursework in biometrics. The project uses Python with Tkinter for the GUI, Pillow for image processing, Matplotlib for visualizations, and NumPy for numerical operations.

## Features

- **Basic Image Operations:** Convert images to grayscale, create negatives, adjust brightness and contrast, and perform binarization.
- **Graphic Filters:** Apply filters such as Gaussian, Sharpening, and Averaging to enhance or modify images.
- **Edge Detection Algorithms:** Includes implementations of:
  - Robert's Cross
  - Sobel Operator
  - Scharr Operator
  - Laplace Operator
  - **Custom Detection:** Allows the user to input a custom weight matrix (minimum size 2x2 or 3x3) for edge detection.
- **Projection Visualization:** Display horizontal and vertical projections of the image for analysis.
- **Undo Feature:** Reverse operations to step back through image modifications.
- **Documentation Access:** A built-in "Information" option opens the project report in PDF format.

## Project Structure

- **Source Code:** Contains all the Python modules for image processing, GUI, and edge detection.
- **main.exe:** The compiled executable of the application, which you can find in the `dist` folder.
- **Sprawozdanie_poprawne_biometria_01_igor_rudolf_327310.pdf:** The project report (documentation) is included in the repository.
