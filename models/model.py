from models.conn import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class_users = db.Table('class_users',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata
    api_key = db.Column(db.String(32))

    classes = db.relationship('Class', secondary=class_users, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)
    
    def set_api_key(self, api_key):
        self.api_key = api_key
        db.session.commit()

    def add_class(self, _class):
        self.classes.append(_class)
        db.session.commit()

    def has_class(self, _class):
        return any(c.id == _class.id for c in self.classes)
    
    def has_student(self, student):
        for _class in student.classes:
            if self.has_class(_class):
                return True
            
        return False
    
    def get_classes_data(self):
        data = {}
        for _class in self.classes:
            if not _class.school_year in data:
                data[_class.school_year] = []

            data[_class.school_year].append(_class.name)
        return data

    
    @staticmethod
    def authenticate_key(api_key):
        """ Ritorna l'utente con la data chiave."""
        stmt = db.select(User).filter_by(api_key=api_key)
        user = db.session.execute(stmt).first()
        if user:
            return user[0]
        else:
            return user
    
    
    @staticmethod
    def insert(username, email, password):
        try:
            model = User(username=username, email=email)
            model.set_password(password=password)
            db.session.add(model)
            db.session.commit()
            return model
        except:
            db.session.rollback()
    
    @staticmethod
    def get_from_email(email):
        """Ritorna l'utente con la mail corrispondente."""
        stmt = db.select(User).filter_by(email=email)
        user = db.session.execute(stmt).first()
        if user:
            return user[0]
        else:
            return user
    

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

    # Relazione many-to-many tra Student e Class
    students = db.relationship('Student', secondary=class_students, back_populates='classes')

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
    classes = db.relationship('Class', secondary=class_students, back_populates='students')

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
    
    
    @staticmethod
    def get_one_by_id(id):
        stmt = db.select(Student).filter_by(id=id)
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
    