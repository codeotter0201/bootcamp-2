from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    jsonify,
    abort,
    make_response,
    Blueprint,
)
import json
from .extensions import db
from .models import Attraction, AttractionFile, User, Order
import jwt

api = Blueprint("api", __name__)


@api.route("/")
def index():
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


@api.route("/api/create_order", methods=["POST"])
def create_order():
    token = request.headers.get("Authorization").split()[1]
    user_data = jwt.decode(token, "secret", algorithms=["HS256"])
    email = user_data.get("email")

    data = request.get_json()
    v = data.get("attraction_id")
    attraction_id = int(v) if isinstance(v, str) else v
    date = data.get("date")
    session = data.get("session")

    orders = Order.query.filter_by(email=email).all()
    if orders:
        for pending_order in orders:
            db.session.delete(pending_order)
        db.session.commit()

    order = Order(attraction_id=attraction_id, email=email, date=date, session=session)
    db.session.add(order)
    db.session.commit()
    return jsonify(result="訂購成功")

@api.route("/api/get_order")
def get_order():
    token = request.headers.get("Authorization").split()[1]
    user_data = jwt.decode(token, "secret", algorithms=["HS256"])
    email = user_data.get("email")
    order = Order.query.filter_by(email=email).first()
    if order:
        return jsonify(result=order.get_json())
    else:
        return jsonify(result="無訂單")


@api.route("/api/delete_order")
def delete_order():
    token = request.headers.get("Authorization").split()[1]
    user_data = jwt.decode(token, "secret", algorithms=["HS256"])
    email = user_data.get("email")

    orders = Order.query.filter_by(email=email).all() # 刪除本帳號所有 order
    for order in orders:
        db.session.delete(order)
        db.session.commit()
    return jsonify(result="刪除成功")


@api.route("/api/signin", methods=["POST"])
def signin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    # 比對資料庫，如果 email 或 password 不正確，回傳 {"result": "帳號或密碼錯誤"}
    user_info = User.query.filter_by(email=email, password=password).first()
    if not user_info:
        return jsonify(result="帳號或密碼錯誤")
    # email 與 password 正確，回傳 {"result": "登入成功", "token": "JWT"}
    else:
        token = jwt.encode(
            {"id": user_info.id, "email": email, "name": user_info.name},
            "secret",
            algorithm="HS256",
        )
        return jsonify(result="登入成功", token=token)


@api.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # 用email檢查資料庫，如果被註冊的帳號已存在，回傳 {"result": "此帳號已被註冊"}
    if User.query.filter_by(email=email).first():
        return jsonify(result="此帳號已被註冊")
    # 將資料存入資料庫
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(result=f"{name} 註冊成功")


@api.route("/api/currentuser")
def current_user():
    # 接收前端 JWT 資料，檢查當前是否登入，並且回傳 {"id":id, "email":email, "name":user_info.name}
    # 需要驗證會員身份的後端程式,接收到前端請求後,可以從 Authorization Header 取得 Token,並透過解析判斷登入
    # 從 Authorization Header
    try:
        # 如果解出來的 token 能取得 id, email, name 則為有效的 token
        token = request.headers.get("Authorization").split()[1]
        data = jwt.decode(token, "secret", algorithms=["HS256"])
        return jsonify(
            id=data.get("id"), email=data.get("email"), name=data.get("name")
        )
    except:
        return jsonify(id=None, email=None, name=None)


@api.route("/api/attractions", methods=["GET"])
def get_attractions():
    keyword = request.args.get("keyword", None)  # 獲取關鍵字參數
    try:
        page_number = int(request.args.get("page", 0))
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
        attractions = (
            Attraction.query.filter(
                (Attraction.name.like(f"%{keyword}%")) | (Attraction.mrt == keyword)
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )
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
            "images": [
                i.file_url
                for i in AttractionFile.query.filter_by(
                    attraction_id=attraction.id
                ).all()
            ],
        }
        attraction_list.append(attraction_dict)

    nextPage = page_number + 1 if len(attractions) == 13 else None

    response = {"nextPage": nextPage, "data": attraction_list}
    return json.dumps(response, ensure_ascii=False).encode("utf8")


@api.route("/api/attraction/<attractionId>", methods=["GET"])
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
            "images": [
                i.file_url
                for i in AttractionFile.query.filter_by(
                    attraction_id=attraction.id
                ).all()
            ],
        }
        response = {"data": attraction_dict}
        return json.dumps(response, ensure_ascii=False).encode("utf8")
    else:
        response = jsonify(error=True, message=str("景點編號不正確"))
        response.status_code = 400
        return make_response(response)


@api.route("/api/mrts", methods=["GET"])
def get_mrts():
    try:
        attractions = (
            db.session.query(Attraction.mrt, db.func.count())
            .group_by(Attraction.mrt)
            .order_by(db.func.count().desc())
            .all()
        )
        sorted_mrts = [mrt for mrt, count in attractions]
        response = {"data": sorted_mrts}
        return jsonify(response)
    except:
        response = jsonify(error=True, message=str("資料庫讀取錯誤"))
        response.status_code = 500
        return make_response(response)
