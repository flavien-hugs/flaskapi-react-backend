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
