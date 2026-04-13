"""
Myanmar OCR Engine
Handles text extraction from images and PDFs using Tesseract OCR.
"""

import os
import uuid
import zipfile
from io import BytesIO
from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes


UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_PDF_EXTENSIONS


def is_allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def is_pdf(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_PDF_EXTENSIONS


def extract_text_from_image(image: Image.Image, lang: str = "mya") -> str:
    """Extract text from a PIL Image using Tesseract OCR."""
    try:
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except pytesseract.TesseractError as e:
        raise RuntimeError(f"OCR processing failed: {e}")


def extract_text_from_pdf_bytes(pdf_bytes: bytes, lang: str = "mya") -> list[dict]:
    """Extract text from each page of a PDF file."""
    results = []
    try:
        images = convert_from_bytes(pdf_bytes, dpi=300)
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}")

    for i, image in enumerate(images, start=1):
        text = extract_text_from_image(image, lang=lang)
        results.append({
            "page": i,
            "text": text,
        })
    return results


def extract_text_from_image_bytes(image_bytes: bytes, lang: str = "mya") -> str:
    """Extract text from image bytes."""
    try:
        image = Image.open(BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
        return extract_text_from_image(image, lang=lang)
    except Exception as e:
        raise RuntimeError(f"Image processing failed: {e}")


def process_file(file_bytes: bytes, filename: str, lang: str = "mya") -> dict:
    """
    Process an uploaded file and return OCR results.
    Returns a dict with 'type' ('image' or 'pdf'), 'results', and 'output_id'.
    """
    output_id = str(uuid.uuid4())[:8]

    if is_pdf(filename):
        pages = extract_text_from_pdf_bytes(file_bytes, lang=lang)
        output_dir = OUTPUT_DIR / output_id
        output_dir.mkdir(parents=True, exist_ok=True)

        text_files = []
        full_text = []
        for page in pages:
            page_filename = f"page_{page['page']:03d}.txt"
            page_path = output_dir / page_filename
            page_path.write_text(page["text"], encoding="utf-8")
            text_files.append(page_filename)
            full_text.append(page["text"])

        combined_path = output_dir / "full_text.txt"
        combined_path.write_text("\n\n--- Page Break ---\n\n".join(full_text), encoding="utf-8")
        text_files.append("full_text.txt")

        return {
            "type": "pdf",
            "output_id": output_id,
            "total_pages": len(pages),
            "pages": pages,
            "text_files": text_files,
        }
    else:
        text = extract_text_from_image_bytes(file_bytes, lang=lang)
        output_dir = OUTPUT_DIR / output_id
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "extracted_text.txt"
        output_path.write_text(text, encoding="utf-8")

        return {
            "type": "image",
            "output_id": output_id,
            "text": text,
            "text_files": ["extracted_text.txt"],
        }


def create_zip(output_id: str) -> BytesIO:
    """Create a ZIP file containing all text outputs for a given output_id."""
    output_dir = OUTPUT_DIR / output_id
    if not output_dir.exists():
        raise FileNotFoundError(f"Output not found: {output_id}")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for txt_file in sorted(output_dir.glob("*.txt")):
            zf.write(txt_file, txt_file.name)

    zip_buffer.seek(0)
    return zip_buffer


def cleanup_output(output_id: str):
    """Remove output files for a given output_id."""
    import shutil
    output_dir = OUTPUT_DIR / output_id
    if output_dir.exists():
        shutil.rmtree(output_dir)


def get_available_languages() -> list[str]:
    """Get list of available Tesseract languages."""
    try:
        langs = pytesseract.get_languages()
        return [l for l in langs if l != "osd"]
    except Exception:
        return ["mya", "eng"]
