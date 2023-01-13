from flask import request
from flask_restx import Namespace, Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

from .. import api
from ..models import User
from ..resources import signup_resource_fields, login_resource_fields

auth_ns = api.namespace(
    'auth', version='1.0',
    description="A namespace for our authentication"
)


PASSWORD_LENGTH = 6
FULLNAME_LENGTH = 4


@auth_ns.route("/signup", strict_slashes=False)
class AuthSignup(Resource):

    @auth_ns.expect(signup_resource_fields)
    @auth_ns.marshal_with(signup_resource_fields, code=201)
    def post(self):
        """Create a new user"""
        data = request.json
        fullname = data["user_fullname"]
        addr_email = data['user_addr_email']
        password = data['user_password']

        if len(password) < PASSWORD_LENGTH:
            return jsonify({"message": "Password is too short"}), HTTP_400_BAD_REQUEST

        if len(fullname) < FULLNAME_LENGTH:
            return jsonify({"message": f"This user fullname '{fullname}' is too short"}), 400

        db_user = User.query.filter_by(
            user_addr_email=addr_email).one_or_none()
        if db_user is not None:
            return jsonify({"message": f"This address email '{addr_email}' is taken !"}), 409

        password_hashed = generate_password_hash(password)

        new_user = User(
            user_fullname=fullname,
            user_addr_email=addr_email,
            user_password=password_hashed
        )
        new_user.save()
        return new_user, 201


@auth_ns.route("/login", strict_slashes=False)
class AuthLogin(Resource):

    @auth_ns.expect(login_resource_fields)
    def post(self):
        data = request.get_json()
        user_addr_email = data.get("user_addr_email", None)
        user_password = data.get("user_password", None)

        db_user = User.query.filter_by(
            user_addr_email=user_addr_email
        ).one_or_none()

        if db_user and check_password_hash(db_user.user_password, user_password):
            refresh_token = create_refresh_token(
                identity=db_user.user_addr_email)
            access_token = create_access_token(
                identity=db_user.user_addr_email)

            data = {
                "refresh_token": refresh_token,
                "access_token": access_token,
                "user_fullname": db_user.user_fullname,
                "user_email": db_user.user_addr_email,
            }

            return {"user": data}, 200

        return {"message": "Wrong credentials"}, 401
