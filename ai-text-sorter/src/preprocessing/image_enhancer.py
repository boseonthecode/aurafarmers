import cv2

class ImageEnhancer:
    def __init__(self, config=None):
        pass

    def enhance(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
