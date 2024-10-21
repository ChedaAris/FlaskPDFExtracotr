from flask import Blueprint, request, flash, request, send_file
import os
import fitz
import pymupdf
import io
import re
from PIL import Image
from werkzeug.utils import secure_filename
from models.model import Student
from flask import jsonify

api = Blueprint('api', __name__)

names = []
lastnames = []
birth_dates = []
images = []

@api.route("/", methods=["GET"])
def get_all():
    students = Student.get_all()
    students_list = [student.to_dict() for student in students]  # Convert each student to a dict
    return jsonify(students_list)

@api.route("/<int:id>", methods=["GET"])
def get_one(id):
    student = Student.get_one(id);
    if not student:
        return "Student not found"
    
    return jsonify(student[0].to_dict())

@api.route("/image/<int:id>", methods=["GET"])
def get_image(id):
    student = Student.get_one(id);
    if not student:
        return "Student not found"

    return send_file(student[0].image_path, mimetype="image/jpeg")


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
            file.save(os.path.join(os.getenv("UPLOAD_STORAGE_FOLDER"), filename))
            get_pdf_text(filename) 
            save_pictures(filename)

            for i in range(len(names)):
                try:
                    Student.insert(name=names[i], lastname=lastnames[i], birth_date=birth_dates[i], image_path=images[i])
                except:
                    return "User already exists in database"
            
            return "ok"
        else:
            return "ERROR"
        
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() == "pdf"

def save_pictures(pdf_filename):
    pdf_file = fitz.open(os.getenv("UPLOAD_STORAGE_FOLDER") + "\\" + pdf_filename)
    for page_number in range(len(pdf_file)): 
        page=pdf_file[page_number]
        
        for image_index, img in enumerate(page.get_images(),start=0):
            if(image_index == len(lastnames)):
                break
            xref = img[0] 
            # extract image bytes 
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            # get image extension
            image_ext = base_image["ext"]
            
            # Create a PIL Image object from the image bytes
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Save the image to disk and the student to the DB
            image_path = f"{os.getenv("IMAGES_STORAGE_FOLDER")}\\image_{lastnames[image_index]}_{image_index}.{image_ext}"
            images.append(image_path)
            pil_image.save(image_path)

def get_pdf_text(filename):
    doc = pymupdf.open(os.getenv("UPLOAD_STORAGE_FOLDER") + "\\" + filename)
    page = doc[0]
    text = page.get_text()

    #Cerca nel file l'indicazione di quanti studenti ci sono nella classe
    students_number_pattern = r'[0-9] Studenti'
    match = re.findall(students_number_pattern, text, re.MULTILINE)
    if(len(match) > 1):
        print("ERRORE inaspettato")
        return
    
    lines = text.split('\n')
    print(lines)
    #Estrare il numero di studenti nella classe
    students_number = int(match[0].split(' ')[0])
    
    #Per ogni allievo ci sono 2 righe nel pdf: prima riga con nome e cognome, seconda con data di nasicta
    #I dati degli allievi sono sempre sulle prime righe del file
    for i in range(students_number*2):
        line = lines[i]
        if(i % 2 == 0):
            values = line.split(' ')
            lastnames.append(values[0])
            names.append(values[1])
        else:
            #validate birth date
            birth_dates.append(line)
    
    print(names)
    print(lastnames)
    print(birth_dates)