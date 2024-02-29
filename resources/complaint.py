from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import ComplaintModel, UserModel
from api_schemas import ComplaintSchema, ComplaintUpdateSchema
from db import db

blp = Blueprint("Complaints", __name__, "Operations on complaints")


@blp.route("/my_complaints")
class ComplaintList(MethodView):

    @jwt_required()
    @blp.response(200, ComplaintSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if user.isAdmin:
            abort(400, message="Unauthorized: only accessible by the user")
        return ComplaintModel.query.filter_by(user_id=user_id).all()

    @jwt_required()
    @blp.response(201, ComplaintSchema)
    @blp.arguments(ComplaintSchema)
    def post(self, complaint_data):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if user.isAdmin:
            abort(400, message="Unauthorized: only accessible by the user")
        complaint_data["user_id"] = user_id
        complaint = ComplaintModel(**complaint_data)
        try:
            db.session.add(complaint)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting into the database")
        return complaint


@blp.route("/all_complaints")
class AllComplaints(MethodView):

    @jwt_required()
    @blp.response(200, ComplaintSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if user.isAdmin:
            return ComplaintModel.query.all()
        abort(400, message="Unauthorized: only accessible by the admin")


@blp.route("/my_complaints/<int:complaint_id>")
class Complaint(MethodView):
    @jwt_required()
    @blp.response(200, ComplaintSchema)
    @blp.arguments(ComplaintUpdateSchema)
    def put(self, complaint_data, complaint_id):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if user.isAdmin:
            abort(400, message="Unauthorized: only accessible by the user")
        complaint = ComplaintModel.query.get_or_404(complaint_id)
        if complaint and complaint.user_id == user_id:
            for key, value in complaint_data.items():
                setattr(complaint, key, value)
            db.session.add(complaint)
            db.session.commit()
            return complaint
        abort(404, message="Complaint not found")

    @jwt_required()
    def delete(self, complaint_id):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if user.isAdmin:
            abort(400, message="Unauthorized: only accessible by the user")
        complaint = ComplaintModel.query.get_or_404(complaint_id)
        if complaint and complaint.user_id == user_id:
            db.session.delete(complaint)
            db.session.commit()
            return {"message": "Complaint deleted."}, 200
        abort(404, message="Complaint not found")


@blp.route("/all_complaints/<int:complaint_id>/status")
class ComplaintStatus(MethodView):
    @jwt_required()
    def put(self, complaint_id):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if not user.isAdmin:
            abort(400, message="Unauthorized: only accessible by the admin")
        complaint = ComplaintModel.query.get_or_404(complaint_id)
        if not complaint:
            abort(404, message="Complaint not found")
        complaint.status = True
        db.session.add(complaint)
        db.session.commit()
        return {"message": "Complaint status updated."}, 200
