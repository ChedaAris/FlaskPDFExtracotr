from flask import Blueprint, request, flash, request, send_file
import os
import fitz
import pymupdf
import io
import re
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from models.model import Student, Class
from flask import jsonify

api = Blueprint('api', __name__)

names = []
lastnames = []
birth_dates = []
images = []
pil_images = []

school_year = ""
school_class = ""

@api.route("/", methods=["GET"])
def get_all():
    students = Student.get_all()
    students_list = [student.to_dict() for student in students]  # Convert each student to a dict
    return jsonify(students_list)

@api.route("/<int:id>", methods=["GET"])
def get_one(id):
    student = Student.get_one_by_id(id);
    if not student:
        return "Student not found", 404
    
    return jsonify(student.to_dict())

@api.route("/image/<int:id>", methods=["GET"])
def get_image(id):
    student = Student.get_one_by_id(id);
    if not student:
        return "Student not found", 404

    return send_file(student.image_path, mimetype="image/jpeg")


@api.route("/class/<name>/<year>", methods=["GET"])
def get_students_from_class(name, year):
    _class = Class.get_one(name=name, year=year)
    if not _class:
        return "Class not found", 404

    students = Student.get_all()

    
    students_list = [student.to_dict() for student in students]  # Convert each student to a dict
    return jsonify(students_list)



@api.route("/", methods=["POST"])
def extract_data_from_pdf():

    reset_vars()
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

        current_class = Class.get_one(school_class, school_year)
        if not current_class:
            current_class = Class.insert(school_class, school_year)

        for i in range(len(names)):
            student = Student.get_one(name=names[i], lastname=lastnames[i], birth_date=birth_dates[i])
            if not student:
                Student.insert(name=names[i], lastname=lastnames[i], birth_date=birth_dates[i], image_path=images[i])
                #saves images to FilySystem only when the record has been inserted
                pil_img = pil_images[i]
                pil_img.save(images[i])

            student = Student.get_one(name=names[i], lastname=lastnames[i], birth_date=birth_dates[i])
            if not student.in_class(current_class):
                student.add_class(current_class);

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
            image_path = f"{os.getenv('IMAGES_STORAGE_FOLDER')}\\img_{uuid.uuid4()}.{image_ext}"
            images.append(image_path)
            pil_images.append(pil_image)

def get_pdf_text(filename):
    doc = pymupdf.open(os.getenv("UPLOAD_STORAGE_FOLDER") + "\\" + filename)
    page = doc[0]
    text = page.get_text()

    extract_class_and_year(text)
    print(school_year)
    print(school_class)
    #Cerca nel file l'indicazione di quanti studenti ci sono nella classe
    students_number_pattern = r'\d Studenti'
    students_number_match = re.findall(students_number_pattern, text, re.MULTILINE)

    lines = text.split('\n')
    print(lines)
    #Estrare il numero di studenti nella classe
    students_number = int(students_number_match[0].split(' ')[0])
    
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

def extract_class_and_year(pdf_content):
    school_year_pattern = r'\d{4}-\d{4}'
    school_year_match = re.findall(school_year_pattern, pdf_content, re.MULTILINE)
    global school_year
    school_year = school_year_match[0]

    lines = pdf_content.split('\n')
    for i, line in enumerate(lines):
        if school_year in line:
            global school_class 
            school_class = lines[i+1]
            break

def reset_vars():
    global names
    global lastnames
    global birth_dates
    global images
    global pil_images
    global school_class
    global school_year
    names = []
    lastnames = []
    birth_dates = []
    images = []
    pil_images = []

    school_year = ""
    school_class = ""

    
    
    
