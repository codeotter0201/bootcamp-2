from flask import Flask, render_template, request, redirect, session, url_for, jsonify, abort, make_response, Blueprint
import json
from .extensions import db
from .models import Attraction, AttractionFile, User

api = Blueprint('api', __name__)

# Pages
@api.route("/")
def index():
    # url = url_for('template', 'index.html')
    return render_template("index.html")
@api.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html", id_value=id)
@api.route("/booking")
def booking():
	return render_template("booking.html")
@api.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@api.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = request.form.get('email')
    password = request.form.get('password')
    # 比對資料庫，如果 email 或 password 不正確，回傳 {"result": "帳號或密碼錯誤"}
    if not User.query.filter_by(email=email, password=password).first():
        return jsonify(result='帳號或密碼錯誤')
    # email 與 password 正確，回傳 {"result": "登入成功", "token": "JWT"}
    else:
        return jsonify(result='登入成功', token='JWT')


@api.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # 用email檢查資料庫，如果被註冊的帳號已存在，回傳 {"result": "此帳號已被註冊"}
    if User.query.filter_by(email=email).first():
         return jsonify(result='此帳號已被註冊')
    # 將資料存入資料庫
    new_attraction = User(name=name, email=email, password=password)
    db.session.add(new_attraction)
    db.session.commit()
    return jsonify(result=f'{name} 註冊成功')

@api.route('/api/currentuser', methods=['GET'])
def current_user(token:str):
     # 接收前端 JWT 資料，檢查當前是否登入，並且回傳 {"result": "登入成功", "token": "JWT"}
    return jsonify(result='登入成功', token='JWT')


@api.route('/api/attractions', methods=['GET'])
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

    page_size = 13  # Number of rows per page
    offset = page_number * page_size

    if keyword:
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
    
    nextPage = page_number + 1 if len(attractions) == 13 else None

    response = {
        "nextPage": nextPage,
        "data": attraction_list
    }
    return json.dumps(response, ensure_ascii=False).encode('utf8')

@api.route('/api/attraction/<attractionId>', methods=['GET'])
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
    
@api.route('/api/mrts', methods=['GET'])
def get_mrts():
    try:
        attractions = db.session.query(Attraction.mrt, db.func.count()).group_by(Attraction.mrt).order_by(db.func.count().desc()).all()
        sorted_mrts = [mrt for mrt, count in attractions]
        response = {
            "data": sorted_mrts
        }
        return jsonify(response)
    except:
        response = jsonify(error=True, message=str("資料庫讀取錯誤"))
        response.status_code = 500
        return make_response(response)
    

@api.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # 允許的網域
    # response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3002'  # 允許的網域
    # response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # 允許的 HTTP 方法
    # response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # 允許的標頭
    return response