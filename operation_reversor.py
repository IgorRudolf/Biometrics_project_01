from PIL import Image


class OperationReversor:
    def __init__(self):
        self._stack = []

    def push(self, image: Image.Image):
        copy_of_image = image.copy()
        self._stack.append(copy_of_image)

    def pop(self):
        if not self._stack:
            raise Exception('Stack is empty')
        return self._stack.pop()

    def can_reverse(self):
        return len(self._stack) > 0
