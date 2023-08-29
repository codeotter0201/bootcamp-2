from flask import Flask, render_template, request, redirect, session, url_for, jsonify, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__, 
            static_folder="static", 
            static_url_path="/static",
            template_folder="templates"
            )
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://test:test@db/testdb'
db = SQLAlchemy(app)

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

def clean_data_and_save_to_sql():
    with open('data/taipei-attractions.json', encoding='utf-8-sig') as file:
        data = json.load(file)
        data = data['result']['results']

    with app.app_context():
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

@app.before_request
def setup_db():
    with app.app_context():
        db.create_all()
        if not Attraction.query.first():
            clean_data_and_save_to_sql()

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")
@app.route("/setup")
def setup():
    setup_db()
    return 'ok'

@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    keyword = request.args.get('keyword', None)  # 獲取關鍵字參數
    try:
        page_number = int(request.args.get('page', 0))
        if page_number < 0:
            response = jsonify(error=True, message=str("請輸入正整數的頁碼"))
            response.status_code = 500
            return make_response(response)
    except:
        response = jsonify(error=True, message=str("請輸入正整數的頁碼"))
        response.status_code = 500
        return make_response(response)

    page_size = 12  # Number of rows per page
    offset = page_number * page_size

    if keyword:
        # attractions = Attraction.query.filter(Attraction.name.like(f"%{keyword}%") | Attraction.mrt.like(f"%{keyword}%")).all()
        attractions = Attraction.query.filter(
            (Attraction.name.like(f"%{keyword}%")) | (Attraction.mrt==keyword)
        ).offset(offset).limit(page_size).all()
    else:
        # attractions = Attraction.query.all()
        attractions = Attraction.query.offset(offset).limit(page_size).all()

    attraction_list = []
    for attraction in attractions:
        attraction_dict = {
            "id": attraction.id,
            "name": attraction.name,
            "category": attraction.cat,
            "description": attraction.description,
            "address": attraction.address,
            "transport": attraction.direction,
            "mrt": attraction.mrt,
            "lat": attraction.latitude,
            "lng": attraction.longitude,
            "images": [i.file_url for i in AttractionFile.query.filter_by(attraction_id=attraction.id).all()]
        }
        attraction_list.append(attraction_dict)
        
    response = {
        "nextPage": page_number+1,
        "data": attraction_list
    }
    return json.dumps(response, ensure_ascii=False).encode('utf8')

@app.route('/api/attraction/<attractionId>', methods=['GET'])
def get_attraction_by_id(attractionId):
    try:
        attractionId = int(attractionId)
    except:
        response = jsonify(error=True, message=str("請輸入正整數的ID"))
        response.status_code = 500
        return make_response(response)

    attraction = Attraction.query.filter_by(id=attractionId).first()
    if attraction:
        attraction_dict = {
            "id": attraction.id,
            "name": attraction.name,
            "category": attraction.cat,
            "description": attraction.description,
            "address": attraction.address,
            "transport": attraction.direction,
            "mrt": attraction.mrt,
            "lat": attraction.latitude,
            "lng": attraction.longitude,
            "images": [i.file_url for i in AttractionFile.query.filter_by(attraction_id=attraction.id).all()]
        }
        response = {
            "data": attraction_dict
        }
        return json.dumps(response, ensure_ascii=False).encode('utf8')
    else:
        response = jsonify(error=True, message=str("景點編號不正確"))
        response.status_code = 400
        return make_response(response)
    
@app.route('/api/mrts', methods=['GET'])
def get_mrts():
    try:
        attractions = Attraction.query.limit(40).all()
    except:
        response = jsonify(error=True, message=str("資料庫讀取錯誤"))
        response.status_code = 500
        return make_response(response)

    temp = {}
    for i in attractions:
         temp[i.mrt] = temp.get(i.mrt, 0)
         temp[i.mrt] += 1

    sorted_data = sorted(temp.items(), key=lambda x: x[1], reverse=True)
    sorted_mrts = [item[0] for item in sorted_data]
    response = {
        "data": sorted_mrts
    }
    return json.dumps(response, ensure_ascii=False).encode('utf8')
     
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=3000)