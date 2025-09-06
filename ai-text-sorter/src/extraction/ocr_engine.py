import cv2
import numpy as np
import logging
import os

try:
    import pytesseract
    TESSERACT = True
except ImportError:
    TESSERACT = False

try:
    import easyocr
    EASYOCR = True
except ImportError:
    EASYOCR = False

class MultiOCREngine:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.primary = config.get("primary_engine", "easyocr")
        self.languages = config.get("languages", ["en"])
        self.engines = {}

        if EASYOCR:
            self.engines['easyocr'] = easyocr.Reader(self.languages)
            self.logger.info("EasyOCR loaded")
        if TESSERACT:
            self.engines['tesseract'] = True
            self.logger.info("Tesseract available")

        if not self.engines:
            raise RuntimeError("No OCR engine available")

    def extract_text(self, image):
        if self.primary == 'easyocr' and 'easyocr' in self.engines:
            return self._easyocr(image)
        elif self.primary == 'tesseract' and 'tesseract' in self.engines:
            return self._tesseract(image)
        else:
            if 'easyocr' in self.engines:
                return self._easyocr(image)
            elif 'tesseract' in self.engines:
                return self._tesseract(image)
            else:
                return {'text': '', 'confidence': 0}

    def _easyocr(self, image):
        reader = self.engines['easyocr']
        results = reader.readtext(image)
        text = ' '.join([res[1] for res in results])
        confidence = np.mean([res[2] for res in results]) if results else 0
        return {'text': text, 'confidence': confidence, 'engine': 'easyocr'}

    def _tesseract(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(rgb_image)
        confs = pytesseract.image_to_data(rgb_image, output_type=pytesseract.Output.DICT)['conf']
        confs = [int(c) for c in confs if c.isdigit() and int(c) > 0]
        avg_conf = sum(confs)/len(confs)/100 if confs else 0.5
        return {'text': text, 'confidence': avg_conf, 'engine': 'tesseract'}
