import math
from PIL import Image

def roberts_cross_own_working_way(img, weight_matrix=None):

    if weight_matrix is None:
        weight_matrix = [[1, 0], [0, -1]]
    if len(weight_matrix) != 2 or any(len(row) != 2 for row in weight_matrix):
        raise ValueError("Weights matrix must be 2x2.")
    gray = img.convert("L")
    width, height = gray.size
    new_img = Image.new("L", (width, height))
    src = gray.load()
    dst = new_img.load()

    second_matrix = [
        [weight_matrix[0][1], -weight_matrix[0][0]],
        [-weight_matrix[1][1], weight_matrix[1][0]]
    ]

    for y in range(height - 1):
        for x in range(width - 1):
            gx = (weight_matrix[0][0] * src[x, y] +
                  weight_matrix[0][1] * src[x + 1, y] +
                  weight_matrix[1][0] * src[x, y + 1] +
                  weight_matrix[1][1] * src[x + 1, y + 1])
            gy = (second_matrix[0][0] * src[x, y] +
                  second_matrix[0][1] * src[x + 1, y] +
                  second_matrix[1][0] * src[x, y + 1] +
                  second_matrix[1][1] * src[x + 1, y + 1])
            magnitude = math.sqrt(gx * gx + gy * gy)
            dst[x, y] = min(255, int(magnitude))

    for y in range(height):
        dst[width - 1, y] = 0
    for x in range(width):
        dst[x, height - 1] = 0

    return new_img.convert("RGB")


def sobel_operator_own_working_way(img, weight_matrix=None):
    if weight_matrix is None:
        weight_matrix = [[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]]
    if len(weight_matrix) != 3 or any(len(row) != 3 for row in weight_matrix):
        raise ValueError("Weight matrix must be 3x3")
    second_matrix = [list(row) for row in zip(*weight_matrix[::-1])]
    gray = img.convert("L")
    width, height = gray.size
    new_img = Image.new("L", (width, height))
    src = gray.load()
    dst = new_img.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            gx = 0.0
            gy = 0.0
            for j in range(-1, 2):
                for i in range(-1, 2):
                    pixel = src[x + i, y + j]
                    gx += pixel * weight_matrix[j + 1][i + 1]
                    gy += pixel * second_matrix[j + 1][i + 1]
            g = int(math.sqrt(gx * gx + gy * gy))
            if g > 255:
                g = 255
            dst[x, y] = g

    return new_img.convert("RGB")


def laplace_operator_own_working_way(img, weight_matrix=None):
    if weight_matrix is None:
        weight_matrix = [[0, -1, 0],
                         [-1, 4, -1],
                         [0, -1, 0]]
    if len(weight_matrix) != 3 or any(len(row) != 3 for row in weight_matrix):
        raise ValueError("Weights matrix must be 3x3.")
    gray = img.convert("L")
    w, h = gray.size
    new_img = Image.new("L", (w, h))
    src = gray.load()
    dst = new_img.load()

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            acc = 0.0
            for j in range(-1, 2):
                for i in range(-1, 2):
                    acc += src[x + i, y + j] * weight_matrix[j + 1][i + 1]
            acc = abs(acc)
            if acc > 255:
                acc = 255
            dst[x, y] = int(acc)

    return new_img.convert("RGB")


def scharr_operator_own_working_way(img, weight_matrix=None):
    if weight_matrix is None:
        weight_matrix = [[-3, 0, 3],
                         [-10, 0, 10],
                         [-3, 0, 3]]
    if len(weight_matrix) != 3 or any(len(row) != 3 for row in weight_matrix):
        raise ValueError("Weight matrix must be 3x3")
    second_matrix = [list(row) for row in zip(*weight_matrix[::-1])]
    gray = img.convert("L")
    width, height = gray.size
    new_img = Image.new("L", (width, height))
    src = gray.load()
    dst = new_img.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            gx = 0.0
            gy = 0.0
            for j in range(-1, 2):
                for i in range(-1, 2):
                    p = src[x + i, y + j]
                    gx += p * weight_matrix[j + 1][i + 1]
                    gy += p * second_matrix[j + 1][i + 1]
            g = int(math.sqrt(gx * gx + gy * gy))
            if g > 255:
                g = 255
            dst[x, y] = g

    return new_img.convert("RGB")
