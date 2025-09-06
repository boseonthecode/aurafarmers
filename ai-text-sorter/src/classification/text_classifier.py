import os
import json
import logging
from transformers import pipeline
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '..', '..', 'config', 'categories.json')

class SmartTextClassifier:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.model_name = config.get('model', 'distilbert-base-uncased')
        self.conf_threshold = config.get('confidence_threshold', 0.7)
        try:
            self.classifier = pipeline("zero-shot-classification",
                                       model="facebook/bart-large-mnli",
                                       device=0 if torch.cuda.is_available() else -1)
            self.logger.info("Transformer zero-shot classifier ready")
        except Exception as e:
            self.logger.error(f"Failed to load classifier {e}")
            self.classifier = None
        with open(CONFIG_PATH) as f:
            self.categories = list(json.load(f)['categories'].keys())

    def classify(self, text, ocr_confidence=1.0):
        if not text.strip() or not self.classifier:
            return {'primary_category': 'uncategorized', 'confidence': 0.0, 'all_scores': {}}

        try:
            result = self.classifier(text, self.categories)
            primary = result['labels'][0]
            confidence = result['scores'][0]
            return {'primary_category': primary,
                    'confidence': confidence,
                    'all_scores': dict(zip(result['labels'], result['scores']))}
        except Exception as e:
            self.logger.error(f"Classification error: {e}")
            return {'primary_category': 'uncategorized', 'confidence': 0.0, 'all_scores': {}}
