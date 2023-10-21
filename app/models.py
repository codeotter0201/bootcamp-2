from datetime import datetime
import json
from .extensions import db

class Attraction(db.Model):
    __tablename__ = 'attractions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    longitude = db.Column(db.String(255))
    latitude = db.Column(db.String(255))
    mrt = db.Column(db.String(255))
    file = db.Column(db.JSON)
    rate = db.Column(db.Integer)
    direction = db.Column(db.Text)
    date = db.Column(db.String(255))
    ref_wp = db.Column(db.String(255))
    avbegin = db.Column(db.String(255))
    langinfo = db.Column(db.String(255))
    serial_no = db.Column(db.String(255))
    rownumber = db.Column(db.String(255))
    cat = db.Column(db.String(255))
    memo_time = db.Column(db.Text)
    poi = db.Column(db.String(1))
    idpt = db.Column(db.String(255))
    avend = db.Column(db.String(255))
    
class AttractionFile(db.Model):
    __tablename__ = 'attraction_file'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'))
    file_url = db.Column(db.String(255))
    
    attraction = db.relationship('Attraction', backref=db.backref('files', lazy=True))

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def get_json(self):
        return {
            'name': self.name,
            'password': self.password,
            'email': self.email
        }

class Booking(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'))
    email = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    session = db.Column(db.String(255))

    def get_json(self):
        return {
            'attraction_id': self.attraction_id,
            'date': self.date,
            'session': self.session,
            'email': self.email
        }

def clean_data_and_save_to_sql(data:dict):
    pattern = 'https://'
    for spot in data:
        spot['file'] = [pattern + i for i in spot['file'].split(pattern) if ('.jpg' in i) | ('.png' in i) | ('.JPG' in i) | ('.PNG' in i)]
        temp_dict = {k.lower(): v for k, v in spot.items()}
        temp_dict['mrt'] = '週邊無捷運站' if not temp_dict['mrt'] else temp_dict['mrt']

        attraction = Attraction(
            id=temp_dict['_id'],
            name=temp_dict['name'],
            description=temp_dict['description'],
            address=temp_dict['address'],
            mrt=temp_dict['mrt'],
            rate=temp_dict['rate'],
            direction=temp_dict['direction'],
            avbegin=datetime.strptime(temp_dict['avbegin'], '%Y/%m/%d').date(),
            avend=datetime.strptime(temp_dict['avend'], '%Y/%m/%d').date(),
            longitude=float(temp_dict['longitude']),
            latitude=float(temp_dict['latitude']),
            date=temp_dict['date'],
            ref_wp=temp_dict['ref_wp'],
            langinfo=temp_dict['langinfo'],
            serial_no=temp_dict['serial_no'],
            rownumber=temp_dict['rownumber'],
            cat=temp_dict['cat'],
            memo_time=temp_dict['memo_time'],
            poi=temp_dict['poi'],
            idpt=temp_dict['idpt']
        )
        db.session.add(attraction)
    db.session.commit()
    print('create attraction!')

    for spot in data:
        temp_dict = {k.lower(): v for k, v in spot.items()}
        for file_url in temp_dict['file']:
            attraction_file = AttractionFile(file_url=file_url, attraction_id=temp_dict['_id'])
            db.session.add(attraction_file)
    db.session.commit()
    print('create attraction_file!')

def setup_db(app):
    with app.app_context():
        db.create_all()
        if not Attraction.query.first():
            with open('data/taipei-attractions.json', encoding='utf-8-sig') as file:
                data = json.load(file)
                data = data['result']['results']
            clean_data_and_save_to_sql(data)