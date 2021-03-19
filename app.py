from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, TIMESTAMP, func, desc
from datetime import datetime, timedelta
import bcrypt
import jwt
from uuid import uuid4

app = Flask(__name__)
dbURL = 'postgres://pguser:qX6iVXFgm0rb97JzsziI@db/klinify'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)
app.config['SECRET_KEY'] = 'GjIhOUzLBVs5CJ09j04KWg'


class Customer(db.Model):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(),
                        onupdate=func.current_timestamp())

    def __init__(self, id, name, dob):
        self.id = id
        self.name = name
        self.dob = dob

    def json(self):
        return {"id": self.id, "name": self.name, "dob": self.dob.strftime('%d%m%Y'), "updated_at": self.updated_at}


class Login(db.Model):
    __tablename__ = 'logins'

    user = Column(String, primary_key=True)
    key = Column(String, primary_key=True)

    def __init__(self, user, key):
        self.user = user
        self.key = key


engine = create_engine(dbURL)
db.create_all()
db.session.commit()


@app.before_request
def before_request():
    if request.endpoint != 'login':
        token = request.headers.get('Authorization')
        if token:
            token = token.split()[1]
        if not checkjwt(token):
            return "Unauthorised", 403


def checkjwt(token):
    try:
        decoded = jwt.decode(token, app.config.get('SECRET_KEY'), options={
                             "require": ["exp", "iat", "sub"]}, algorithms=["HS256"])
        user = Login.query.filter_by(
            user=decoded['sub'], key=decoded['key']).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
    except:
        return False
    return False


@app.route('/login', methods=['POST'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    if username == "admin" and bcrypt.checkpw(password.encode('utf-8'), '$2b$12$gtkx8jxsSewVLtiyMLYXRuqL8JFup3lJKRDGdtX5LOz8B95k.EcYK'.encode('utf-8')):
        key = uuid4().hex
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': username,
            'key': key
        }
        data = {"user": username, "key": key}
        db.session.merge(Login(**data))
        db.session.commit()
        return jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
    else:
        return "Unauthorised", 403


@app.route("/cust", methods=['PUT'])
def addcust():
    name = request.args.get('name')
    dob = request.args.get('dob')
    try:
        dob = datetime.strptime(dob, '%d%m%Y')
    except:
        return {"status": "Failed", "reason": "Incorrect date format"}
    data = {"id": None, "name": name, "dob": dob}
    customer = Customer(**data)
    try:
        db.session.add(customer)
        db.session.commit()
        return {"status": "Created", "id": customer.id}
    except:
        return {"status": "Failed"}


@app.route("/cust/<string:id>", methods=['GET'])
def getcust(id):
    customer = Customer.query.filter_by(id=id).first()
    return jsonify(customer.json())


@app.route("/cust/<string:id>", methods=['POST'])
def editcust(id):
    customer = Customer.query.filter_by(id=id).first()
    name = request.args.get('name')
    if name:
        customer.name = name
    dob = request.args.get('dob')
    if dob:
        try:
            dob = datetime.strptime(dob, '%d%m%Y')
        except:
            return {"status": "Failed", "reason": "Incorrect date format"}
        customer.dob = dob
    try:
        db.session.commit()
        return {"status": "Updated"}
    except:
        return {"status": "Failed"}


@app.route("/cust/<string:id>", methods=['DELETE'])
def deletecust(id):
    customer = Customer.query.filter_by(id=id).first()
    if customer:
        db.session.delete(customer)
        db.session.commit()
    return {"status": "Deleted"}


@app.route("/custlist", methods=['GET'])
def custlist():
    n = request.args.get('n')
    try:
        n = int(n)
    except:
        return {"status": "Error", "reason": "Invalid input"}
    return jsonify({"result": [customer.json() for customer in Customer.query.order_by(desc(Customer.dob)).limit(n).all()]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
