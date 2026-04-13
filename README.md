# Myanmar OCR Web Application

Image နှင့် PDF ဖိုင်များမှ မြန်မာစာ Text ထုတ်ယူပေးသော Web Application

## Features

- Image files (PNG, JPG, JPEG, BMP, TIFF, WebP) မှ text extraction
- PDF files မှ page-by-page text extraction
- Myanmar (မြန်မာ), English, Myanmar+English language support
- Drag & drop file upload
- Download results as text files (individual or ZIP)
- Copy to clipboard
- Mobile responsive UI

## Prerequisites

- Python 3.10+
- Tesseract OCR with Myanmar language data
- poppler-utils (for PDF processing)

### Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# Install Myanmar language data
cd /usr/share/tesseract-ocr/5/tessdata/
sudo curl -L -O "https://github.com/tesseract-ocr/tessdata_best/raw/main/mya.traineddata"
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Web Application

```bash
python3 app.py
```

Open http://localhost:5000 in your browser.

### Command Line

```bash
python3 extract_from_screenshot.py <image_path> [language]
```

Example:
```bash
python3 extract_from_screenshot.py document.png mya+eng
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| POST | `/api/ocr` | Upload file and extract text |
| GET | `/api/download/<id>` | Download all results as ZIP |
| GET | `/api/download/<id>/<filename>` | Download individual text file |
| DELETE | `/api/cleanup/<id>` | Clean up output files |
| GET | `/api/languages` | List available OCR languages |

## Project Structure

```
├── app.py                    # Flask web application
├── ocr_engine.py             # OCR processing engine
├── extract_from_screenshot.py # CLI tool for single image OCR
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html            # Web UI template
├── static/
│   ├── css/style.css         # Styles
│   └── js/app.js             # Frontend JavaScript
```

## Credits

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [myanmar-ocr-data-generator](https://github.com/chuuhtetnaing/myanmar-ocr-data-generator)
