from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required

from models import UserModel
from db import db
from api_schemas import UserSchema
from redis_conn import r

blp = Blueprint("Users", __name__, "Operations on users")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel(**user_data)
        user.password = sha256.hash(user.password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(409, message="User already exists")
        except SQLAlchemyError:
            abort(500, message="An error occured while inseting into the database")
        return {"message": "User Created Successfully"}, 201


@blp.route("/users/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()
        if user and sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}

        abort(401, message="Invalid username or password")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        r.set(jti, jti)
        return {"message": "Successfully logged out"}
