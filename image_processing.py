from PIL import Image

class ImageProcessor:
    @staticmethod
    def to_grayscale(img: Image.Image) -> Image.Image:
        width, height = img.size
        gray_img = Image.new("RGB", (width, height))
        pixels = img.load()
        gray_pixels = gray_img.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                gray_pixels[x, y] = (gray, gray, gray)
        return gray_img

    @staticmethod
    def to_negative(img: Image.Image) -> Image.Image:
        width, height = img.size
        negative_img = Image.new("RGB", (width, height))
        pixels = img.load()
        negative_pixels = negative_img.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                negative_pixels[x, y] = (255 - r, 255 - g, 255 - b)
        return negative_img

    @staticmethod
    def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
        width, height = img.size
        result_img = Image.new("RGB", (width, height))
        pixels = img.load()
        result_pixels = result_img.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                r = min(255, max(0, int(r * factor)))
                g = min(255, max(0, int(g * factor)))
                b = min(255, max(0, int(b * factor)))
                result_pixels[x, y] = (r, g, b)
        return result_img

    @staticmethod
    def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
        width, height = img.size
        result_img = Image.new("RGB", (width, height))
        pixels = img.load()
        result_pixels = result_img.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                nr = 128 + factor * (r - 128)
                ng = 128 + factor * (g - 128)
                nb = 128 + factor * (b - 128)
                nr = max(0, min(255, int(nr)))
                ng = max(0, min(255, int(ng)))
                nb = max(0, min(255, int(nb)))
                result_pixels[x, y] = (nr, ng, nb)
        return result_img

    @staticmethod
    def binarize(img: Image.Image, threshold: int) -> Image.Image:
        width, height = img.size
        result_img = Image.new("RGB", (width, height))
        pixels = img.load()
        result_pixels = result_img.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                if gray > threshold:
                    result_pixels[x, y] = (255, 255, 255)
                else:
                    result_pixels[x, y] = (0, 0, 0)
        return result_img
