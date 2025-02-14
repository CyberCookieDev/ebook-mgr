
"""
The features:

- Get author
- Get cover
- Nicely organised
- Send to dropbox

"""
import subprocess
from ebooklib import epub
import os
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

UPLOAD_FOLDER = "/home/pi/incoming_files"  # Adjust path if needed
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
library_path = ""

def get_metadata(file_path):
    book = epub.read_epub(file_path)
    if book.get_metadata('DC', 'title'):
        title = book.get_metadata('DC', 'title')[0][0]
    else:
        title = "Unknown Title"

    if book.get_metadata('DC', 'creator'):
        author = book.get_metadata('DC', 'creator')[0][0]
    else:
        author = "Unknown"

    return [title, author]


def place_in_library(file_path):
    title = get_metadata(file_path)[0]
    author = get_metadata(file_path)[1]
    if author not in os.listdir("./library"):
        os.mkdir(f"./library/{author}")
    file = os.path.basename(file_path)
    file_name = os.path.splitext(file)[0]
    shutil.move(file_path, f"./library/{author}")
    subprocess.run(f"ebook-convert './library/{author}/{file}' './library/{author}/{file_name}.epub'", shell=True)
    os.rename(f"./library/{author}" + "/" + f"{file}", f"./library/{author}" + "/" + f"{title}.epub")


@app.route('/upload', methods=['POST'])
def upload_file(incoming_dir):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file.save(os.path.join(incoming_dir, file.filename))
    place_in_library(os.path.join(incoming_dir, file.filename))
    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200

