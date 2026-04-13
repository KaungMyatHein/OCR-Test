"""
Myanmar OCR Web Application
A Flask web app that extracts text from images and PDFs using Tesseract OCR.
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
)

from ocr_engine import (
    process_file,
    create_zip,
    cleanup_output,
    is_allowed_file,
    get_available_languages,
    ALLOWED_EXTENSIONS,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not is_allowed_file(file.filename):
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return jsonify({"error": f"File type not supported. Allowed: {allowed}"}), 400

    lang = request.form.get("lang", "mya")

    try:
        file_bytes = file.read()
        result = process_file(file_bytes, file.filename, lang=lang)
        return jsonify(result)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/api/download/<output_id>")
def download_zip(output_id):
    if not output_id.isalnum():
        return jsonify({"error": "Invalid output ID"}), 400

    try:
        zip_buffer = create_zip(output_id)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"ocr_result_{output_id}.zip",
        )
    except FileNotFoundError:
        return jsonify({"error": "Output not found"}), 404


@app.route("/api/download/<output_id>/<filename>")
def download_file(output_id, filename):
    if not output_id.isalnum():
        return jsonify({"error": "Invalid output ID"}), 400

    # Prevent directory traversal
    if ".." in filename or "/" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join("outputs", output_id, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    return send_file(
        filepath,
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/cleanup/<output_id>", methods=["DELETE"])
def cleanup(output_id):
    if not output_id.isalnum():
        return jsonify({"error": "Invalid output ID"}), 400

    try:
        cleanup_output(output_id)
        return jsonify({"message": "Cleaned up successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/languages")
def languages():
    langs = get_available_languages()
    return jsonify({"languages": langs})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
