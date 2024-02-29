import os
from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

import models
from db import db
from redis_conn import r

from resources.complaint import blp as ComplaintBlueprint
from resources.user import blp as UserBlueprint


app = Flask(__name__)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "CRIME REPORTING SYSTEM API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET")

db.init_app(app)
with app.app_context():
    db.create_all()
api = Api(app)

jwt = JWTManager(app)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"message": "The token has expired.", "error": "token expired"}, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
        "message": "Signature verification failed.",
        "error": "invalid token",
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
        "message": "Request does not contain an access token.",
        "error": "authorization required",
    }, 401


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    if r.get(jti):
        return True


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"message": "Token has been revoked.", "error": "token revoked"}, 401


api.register_blueprint(UserBlueprint)
api.register_blueprint(ComplaintBlueprint)
