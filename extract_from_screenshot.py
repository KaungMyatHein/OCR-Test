"""
Utility script: Extract Myanmar text from an image file.
Usage: python3 extract_from_screenshot.py <image_path>
"""

import sys
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(img):
    """Preprocess image for better OCR results."""
    # Convert to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Convert to grayscale
    gray = img.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)

    # Sharpen
    gray = gray.filter(ImageFilter.SHARPEN)

    # Binarize (threshold)
    threshold = 140
    gray = gray.point(lambda x: 255 if x > threshold else 0, "1")

    return gray


def ocr_image(image_path, lang="mya+eng", preprocess=True):
    """Run OCR on an image file."""
    img = Image.open(image_path)

    if preprocess:
        img = preprocess_image(img)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
    return text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_from_screenshot.py <image_path>")
        sys.exit(1)

    path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "mya+eng"

    print(f"Processing: {path}")
    print(f"Language: {lang}")
    print("=" * 60)

    # Without preprocessing
    print("\n--- Raw OCR ---")
    text_raw = ocr_image(path, lang=lang, preprocess=False)
    print(text_raw)

    # With preprocessing
    print("\n--- Preprocessed OCR ---")
    text_pp = ocr_image(path, lang=lang, preprocess=True)
    print(text_pp)
