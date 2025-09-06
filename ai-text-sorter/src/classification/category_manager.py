import os
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '..', '..', 'config', 'categories.json')

class CategoryManager:
    def __init__(self, config):
        with open(CONFIG_PATH, 'r') as f:
            self.categories_config = json.load(f)['categories']
        self.output_dir = Path('sorted_documents')
        self.output_dir.mkdir(exist_ok=True)

    def assign_category(self, classification_result, text):
        cat = classification_result.get('primary_category', 'uncategorized')
        if cat not in self.categories_config:
            cat = 'uncategorized'
        return {'category': cat, 'confidence': classification_result.get('confidence', 0)}
