from flask import request, jsonify
from flask_restx import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)

from . import api
from .models import User, Recipe
from .resources import(
    signup_resource_fields,
    login_resource_fields,
    recipe_resource_fields
)

ns = api.namespace('', version='1.0', description="RECIPE operations")

PASSWORD_LENGTH = 6
FULLNAME_LENGTH = 4


@ns.route("/auth/signup")
class AuthSignup(Resource):

    @ns.expect(signup_resource_fields)
    @ns.marshal_with(signup_resource_fields, code=201)
    def post(self):
        """Create a new user"""
        data = request.json
        fullname = data["user_fullname"]
        addr_email = data['user_addr_email']
        password = data['user_password']

        if len(password) < PASSWORD_LENGTH:
            return jsonify({"message": "Password is too short"}), HTTP_400_BAD_REQUEST

        if len(fullname) < FULLNAME_LENGTH:
            return jsonify({"message": f"This user fullname '{fullname}' is too short"}), HTTP_400_BAD_REQUEST

        db_user = User.query.filter_by(user_addr_email=addr_email).one_or_none()
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


@ns.route("/auth/login")
class AuthLogin(Resource):

    @ns.expect(login_resource_fields)
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

            return data, 200

        return jsonify({"message": "Wrong credentials"}), 401


@ns.route("/recipes", endpoint='recipes')
class RecipesResource(Resource):
    '''Shows a list of all recipes, and lets you POST to add new recipes'''

    @ns.doc(recipe_resource_fields)
    @ns.marshal_list_with(recipe_resource_fields)
    def get(self):
        '''List all recipes'''
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 6, type=int)

        recipes = Recipe.query.order_by(Recipe.rcp_created.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        return recipes.items

    @ns.doc(body=recipe_resource_fields)
    @ns.expect(recipe_resource_fields)
    @ns.marshal_with(recipe_resource_fields, code=201)
    @jwt_required()
    def post(self):
        """Create a new recipe"""
        data = request.json
        new_recipe = Recipe(rcp_title=data["rcp_title"], rcp_desc=data['rcp_desc'])
        new_recipe.save()
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes, 201


@ns.route("/recipe/<int:id>", endpoint='recipe')
@ns.response(404, 'Recipe not found')
@ns.param('id', 'The recipe identifier')
class RecipeResource(Resource):
    """Show a single recipe item and lets you delete them"""

    @ns.doc(body=recipe_resource_fields)
    @ns.marshal_with(recipe_resource_fields, code=201)
    def get(self, id):
        """Fetch a given resource"""
        recipe = Recipe.query.get_or_404(id)
        return recipe, 201

    # @ns.expect(recipe_resource_fields)
    @ns.marshal_with(recipe_resource_fields, code=201)
    @jwt_required()
    def put(self, id):
        '''Update a recipe given its identifier'''
        data = request.json
        recipe = Recipe.query.get_or_404(id)
        recipe.update(data['rcp_title'], data['rcp_desc'])
        return recipe, 201

    @ns.doc('delete_recipe')
    @ns.response(204, 'Recipe deleted')
    @ns.marshal_with(recipe_resource_fields, code=204)
    @jwt_required()
    def delete(self, id):
        '''Delete a recipe given its identifier'''
        recipe = Recipe.query.get_or_404(id)
        recipe.delete()
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes, 200
