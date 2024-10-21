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
    

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.String(10), nullable=False)
    image_path = db.Column(db.String(120), unique=True, nullable=False)

    @staticmethod
    def insert(name, lastname, birth_date, image_path):
        model = Student(name=name, lastname=lastname, birth_date=birth_date, image_path=image_path)
        db.session.add(model)
        db.session.commit()
    
    @staticmethod
    def get_all():
        stmt = db.select(Student)
        students = db.session.execute(stmt).scalars().all()
        return students
    
    @staticmethod
    def get_one(id):
        stmt = db.select(Student).filter_by(id=id)
        student = db.session.execute(stmt).first()
        return student
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'birth_date': self.birth_date,
            #'image_path': self.image_path
        }