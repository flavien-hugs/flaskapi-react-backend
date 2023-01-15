from http import HTTPStatus

from flask import request, jsonify
from flask_restx import Resource, representations
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)

from .. import api
from ..models import User, Recipe
from ..resources import (
    signup_resource_fields,
    login_resource_fields,
    user_resource_fields,
)

auth_ns = api.namespace(
    "auth", version="1.0", description="A namespace for our authentication"
)


PASSWORD_LENGTH = 6
FULLNAME_LENGTH = 4


@auth_ns.route("/signup", strict_slashes=False)
class AuthSignup(Resource):
    @auth_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @auth_ns.response(int(HTTPStatus.CONFLICT), "Email address is already registered.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @auth_ns.expect(signup_resource_fields)
    @auth_ns.doc(body=signup_resource_fields)
    def post(self):
        """Register a new user and return an user"""
        data = request.json
        fullname = data["user_fullname"]
        addr_email = data["user_addr_email"]
        password = data["user_password"]

        if len(password) < PASSWORD_LENGTH:
            return jsonify({"message": "Password is too short"}), HTTPStatus.BAD_REQUEST

        if len(fullname) < FULLNAME_LENGTH:
            return (
                jsonify({"message": f"This user fullname '{fullname}' is too short"}),
                400,
            )

        db_user = User.query.filter_by(user_addr_email=addr_email).one_or_none()
        if db_user is not None:
            return (
                jsonify({"message": f"This address email '{addr_email}' is taken !"}),
                409,
            )

        password_hashed = generate_password_hash(password)

        new_user = User(
            user_fullname=fullname,
            user_addr_email=addr_email,
            user_password=password_hashed,
        )
        new_user.save()
        return new_user


@auth_ns.route("/login", strict_slashes=False)
@auth_ns.response(int(HTTPStatus.OK), "User logged successfully")
@auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "User not found")
class AuthLogin(Resource):
    @auth_ns.expect(login_resource_fields)
    def post(self):
        data = request.get_json()
        user_addr_email = data.get("user_addr_email", None)
        user_password = data.get("user_password", None)

        db_user = User.query.filter_by(user_addr_email=user_addr_email).one_or_none()

        if db_user and check_password_hash(db_user.user_password, user_password):
            refresh_token = create_refresh_token(identity=db_user.id)
            access_token = create_access_token(identity=db_user.id)

            data = {
                "refresh_token": refresh_token,
                "access_token": access_token,
                "user_fullname": db_user.user_fullname,
                "user_email": db_user.user_addr_email,
            }

            return {"user": data}, 200

        return {"message": "Wrong credentials"}, 401


@auth_ns.route("/refresh", strict_slashes=False)
@auth_ns.response(int(HTTPStatus.OK), "User logout successfully")
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        data = {"access_token": new_access_token, "user": current_user}
        return data, 200


@auth_ns.route("/me", strict_slashes=False)
@auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized access")
class AuthUser(Resource):
    """Show a user item and lets you delete them"""

    @auth_ns.expect(user_resource_fields)
    @auth_ns.doc(body=user_resource_fields)
    @jwt_required()
    def get(self):
        """Get a user"""
        current_user = get_jwt_identity()
        recipes = Recipe.query.filter_by(user_id=current_user).all()
        print(representations.output_json(recipes, 4))
        return {"user": current_user}

    @auth_ns.expect(user_resource_fields)
    @auth_ns.marshal_with(user_resource_fields, code=201)
    @jwt_required()
    def put(self):
        """Update a user given its identifier"""
        data = request.json
        current_user = get_jwt_identity()
        user = User.query.get_or_404(current_user)
        user.update(data["user_fullname"], data["user_addr_email"])
        return user, 201

    @auth_ns.expect(user_resource_fields)
    @auth_ns.marshal_with(user_resource_fields, code=201)
    @jwt_required()
    def delete(self):
        """Delete a user given its identifier"""
        current_user = get_jwt_identity()
        user = User.query.get_or_404(current_user)
        user.delete()
        return user, 200
