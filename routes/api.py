from flask import Blueprint, request, flash, request
import os
import fitz
import pymupdf
import io
from PIL import Image
from werkzeug.utils import secure_filename

api = Blueprint('api', __name__)


UPLOAD_FOLDER = 'E:\\SAMT\\IV\\Labo Flask\\FlaskPDFExtracotr\\ups'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "pdf"

@api.route("/", methods=["POST"])
def extract_data_from_pdf():
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "no file in request"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            get_pdf_text(filename) 
            save_pictures(filename) 
            return "ok"
        else:
            return "ERROR"
        

def save_pictures(pdf_filename):
    pdf_file = fitz.open(UPLOAD_FOLDER + "\\" + pdf_filename)
    for page_number in range(len(pdf_file)): 
        page=pdf_file[page_number]
        
        image_list = page.get_images()
        print(image_list)
        
        for image_index, img in enumerate(page.get_images(),start=1):
            print(image_index)
            xref = img[0] 
            # extract image bytes 
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            # get image extension
            image_ext = base_image["ext"]
            
            # Create a PIL Image object from the image bytes
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Save the image to disk
            image_path = f"image_{page_number}_{image_index}.{image_ext}"
            pil_image.save(image_path)

def get_pdf_text(filename):
    doc = pymupdf.open(UPLOAD_FOLDER + "\\" + filename)
    page = doc[0]
    text = page.get_text()
    print(text)