from models.conn import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def insert_user():
        return ""
    
    @staticmethod
    def get_from_id(id):
        return ""
    

    def __repr__(self):
        return f'<User {self.username}>'
    

class_students = db.Table('class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'))
)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    school_year = db.Column(db.String(80), nullable=False)

    @staticmethod
    def get_one(name, year):
        stmt = db.select(Class).filter_by(name=name, school_year=year)
        item = db.session.execute(stmt).first()
        if item:
            return item[0]
        else:
            return item
    
    @staticmethod
    def insert(name, year):
        try:
            model = Class(name=name, school_year= year)
            db.session.add(model)
            db.session.commit()
            return model
        except:
            db.session.rollback()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.String(10), nullable=False)
    image_path = db.Column(db.String(120), unique=True, nullable=False)

    # Relazione many-to-many tra Student e Class
    classes = db.relationship('Class', secondary=class_students, backref=db.backref('students', lazy='dynamic'))

    def in_class(self, _class):
        return any(c.id == _class.id for c in self.classes)

    def add_class(self, _class):
        self.classes.append(_class)
        db.session.commit()

    @staticmethod
    def insert(name, lastname, birth_date, image_path):
        try:
            model = Student(name=name, lastname=lastname, birth_date=birth_date, image_path=image_path)
            db.session.add(model)
            db.session.commit()
            return model
        except:
            db.session.rollback()

    
    @staticmethod
    def get_all():
        stmt = db.select(Student)
        students = db.session.execute(stmt).scalars().all()
        return students
    
    @staticmethod
    def get_one(name, lastname, birth_date):
        stmt = db.select(Student).filter_by(name=name, lastname=lastname, birth_date=birth_date)
        student = db.session.execute(stmt).first()
        if student:
            return student[0]
        else:
            return student
    


    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'birth_date': self.birth_date,
            #'image_path': self.image_path
        }
    