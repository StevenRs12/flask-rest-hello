"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():

    users=User.query.all();
    users = list(map(lambda x: x.serialize(), users))
    # users2 =[user.serialize() for user in users]
    print('aqui estan los usuarios', users)

    return jsonify(users), 200

@app.route('/user', methods=['POST'])
def create_user():
    data=request.json

    if 'email' not in data or 'password' not in data:
        raise APIException('Falta el correo o la clave', status_code=400)

    new_user=User(
        email=data['email'],
        password=data['password'],
        is_active=data.get('is_active',False),
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user=User.query.get(user_id);

    if not user:
         raise APIException('el user id no existe', status_code=400)
    
    db.session.delete(user);
    db.session.commit();

    return jsonify({"msj": "Eliminado"}),200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites_by_user_id(user_id):
    print(user_id)
    user = User.query.get(user_id);
    if not user:
        raise APIException('El usuario no exite', status_code=400)
    
    favorites_products = [favorite.product.serialize() for favorite in user.favorites]

    return jsonify(favorites_products), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)