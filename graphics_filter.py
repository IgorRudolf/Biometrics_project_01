from PIL import Image
import math


def kernel_of_the_gauss(kernel_size, sigma):
    kernel = [[0 for _ in range(kernel_size)] for _ in range(kernel_size)]
    center = kernel_size // 2
    sum_val = 0.0
    for i in range(kernel_size):
        for j in range(kernel_size):
            x = i - center
            y = j - center
            kernel[i][j] = math.exp(-(x * x + y * y) / (2 * sigma * sigma))
            sum_val += kernel[i][j]
    for i in range(kernel_size):
        for j in range(kernel_size):
            kernel[i][j] /= sum_val
    return kernel


def sharpening_kernel(kernel_size, intensity):
    tot = kernel_size * kernel_size
    avg = 1.0 / tot
    ker = []
    for i in range(kernel_size):
        row = []
        for j in range(kernel_size):
            row.append(-intensity * avg)
        ker.append(row)
    mid = kernel_size // 2
    ker[mid][mid] = 1 + intensity - intensity * avg
    return ker


def apply_averaging_filter(img, k_size):
    img = img.convert("RGB")
    w, h = img.size
    new_img = img.copy()
    pix = img.load()
    new_pix = new_img.load()

    val = 1.0 / (k_size * k_size)
    kernel = [[val for _ in range(k_size)] for _ in range(k_size)]

    off = k_size // 2

    for y in range(h):
        for x in range(w):
            r_sum = 0.0
            g_sum = 0.0
            b_sum = 0.0

            for j in range(-off, off + 1):
                for i in range(-off, off + 1):
                    xi = min(max(x + i, 0), w - 1)
                    yj = min(max(y + j, 0), h - 1)
                    r, g, b = pix[xi, yj]
                    weight = kernel[j + off][i + off]
                    r_sum += r * weight
                    g_sum += g * weight
                    b_sum += b * weight
            new_pix[x, y] = (int(r_sum), int(g_sum), int(b_sum))

    return new_img


def apply_sharpening_filter(img, k_size, inten):
    img = img.convert("RGB")
    w, h = img.size
    new_img = Image.new("RGB", (w, h))
    pix = img.load()
    new_pix = new_img.load()

    ker = sharpening_kernel(k_size, inten)
    mid = k_size // 2

    for y in range(h):
        for x in range(w):
            sum_r = 0.0
            sum_g = 0.0
            sum_b = 0.0

            for j in range(-mid, mid + 1):
                for i in range(-mid, mid + 1):
                    xi = min(max(x + i, 0), w - 1)
                    yj = min(max(y + j, 0), h - 1)
                    r, g, b = pix[xi, yj]
                    weight = ker[j + mid][i + mid]
                    sum_r += r * weight
                    sum_g += g * weight
                    sum_b += b * weight

            new_r = min(255, max(0, int(sum_r)))
            new_g = min(255, max(0, int(sum_g)))
            new_b = min(255, max(0, int(sum_b)))
            new_pix[x, y] = (new_r, new_g, new_b)

    return new_img


def apply_gaussian_filter(image, kernel_size, sigma):
    image = image.convert("RGB")
    width, height = image.size
    result_img = Image.new("RGB", (width, height))
    pixels = image.load()
    result_pixels = result_img.load()

    kernel = kernel_of_the_gauss(kernel_size, sigma)
    offset = kernel_size // 2

    for y in range(height):
        for x in range(width):
            r_acc = 0.0
            g_acc = 0.0
            b_acc = 0.0
            for ky in range(-offset, offset + 1):
                for kx in range(-offset, offset + 1):
                    px = min(max(x + kx, 0), width - 1)
                    py = min(max(y + ky, 0), height - 1)
                    r, g, b = pixels[px, py]
                    weight = kernel[ky + offset][kx + offset]
                    r_acc += r * weight
                    g_acc += g * weight
                    b_acc += b * weight
            result_pixels[x, y] = (int(r_acc), int(g_acc), int(b_acc))
    return result_img
