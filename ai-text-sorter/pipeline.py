import os
import yaml
import logging
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(os.path.join(BASE_DIR, 'src'))

from preprocessing.image_enhancer import ImageEnhancer
from extraction.ocr_engine import MultiOCREngine
from classification.text_classifier import SmartTextClassifier
from classification.category_manager import CategoryManager
from vlm.perplexity_client import PerplexityVisionClient

class AITextSorterPipeline:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(BASE_DIR, 'config', 'config.yaml')

        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

        self.setup_logging()

        self.image_enhancer = ImageEnhancer(self.config.get('preprocessing', {}))
        self.ocr_engine = MultiOCREngine(self.config.get('ocr', {}))
        self.text_classifier = SmartTextClassifier(self.config.get('nlp', {}))
        self.category_manager = CategoryManager(self.config.get('classification', {}))
        self.vlm_client = PerplexityVisionClient()

    def setup_logging(self):
        log_folder = self.config.get('storage', {}).get('log_folder', 'logs')
        Path(log_folder).mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_folder, 'pipeline.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_document(self, image_path):
        self.logger.info(f'Processing image: {image_path}')

        # Step 1: Enhance image
        enhanced_image = self.image_enhancer.enhance(image_path)

        # Step 2: Extract text with OCR
        ocr_result = self.ocr_engine.extract_text(enhanced_image)
        raw_text = ocr_result['text']

        if not raw_text.strip():
            return {'success': False, 'error': 'No text extracted from OCR'}

        # Step 3: Refine text with Vision-Language Model (NLM)
        vlm_result = self.vlm_client.process(image_path, context=raw_text)
        corrected_text = vlm_result.get('corrected_text', raw_text)
        if 'error' in vlm_result:
            self.logger.warning(f"NLM processing error: {vlm_result['error']} - Falling back to OCR text")

        # Step 4: Classification on corrected (or fallback) text
        classification = self.text_classifier.classify(corrected_text)

        # Step 5: Assign category based on classification
        category_info = self.category_manager.assign_category(classification, corrected_text)

        # Step 6: Organize document into proper folder
        final_path = self.organize_document(image_path, category_info)

        return {
            'success': True,
            'original_text': raw_text,
            'corrected_text': corrected_text,
            'classification': classification,
            'category': category_info,
            'final_path': final_path
        }

    def organize_document(self, src_path, category_info):
        base_output = Path(self.config.get('storage', {}).get('output_folder', 'sorted_documents'))
        category_folder = base_output / category_info['category']
        category_folder.mkdir(parents=True, exist_ok=True)

        filename = Path(src_path).name
        dest = category_folder / filename
        count = 1
        while dest.exists():
            dest = category_folder / f"{Path(filename).stem}_{count}{Path(filename).suffix}"
            count += 1

        import shutil
        shutil.copy2(src_path, dest)

        return str(dest)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Text Sorter with OCR + NLM")
    parser.add_argument("--input", required=True, help="Input image path")
    args = parser.parse_args()

    pipeline = AITextSorterPipeline()
    result = pipeline.process_document(args.input)

    if result["success"]:
        print(f"Original OCR text:\n{result['original_text'][:300]}\n")
        print(f"NLM corrected text:\n{result['corrected_text'][:300]}\n")
        print(f"Category: {result['category']['category']}")
        print(f"Saved to: {result['final_path']}")
    else:
        print(f"Failed: {result.get('error', 'Unknown error')}")
