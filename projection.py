from PIL import Image, ImageDraw
import numpy as np


def project_image(image, projection_type, normalization_factor, return_projection=False):
    if image.mode != "L":
        image = image.convert("L")

    img_array = np.array(image)
    height, width = img_array.shape

    if projection_type == "Horizontal":

        projection = np.sum(img_array, axis=1)

        if np.max(projection) > 0:
            projection = projection / np.max(projection) * 255 * normalization_factor

        result_array = img_array.copy()

        if return_projection:
            return Image.fromarray(result_array), projection

        return Image.fromarray(result_array)

    elif projection_type == "Vertical":

        projection = np.sum(img_array, axis=0)

        if np.max(projection) > 0:
            projection = projection / np.max(projection) * 255 * normalization_factor

        result_array = img_array.copy()

        if return_projection:
            return Image.fromarray(result_array), projection

        return Image.fromarray(result_array)

    else:
        if return_projection:
            if projection_type == "Horizontal":
                empty_projection = np.zeros(height)
            else:
                empty_projection = np.zeros(width)
            return image, empty_projection

        return image
