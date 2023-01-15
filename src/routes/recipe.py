from http import HTTPStatus

from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import api
from ..models import Recipe
from ..resources import recipe_resource_fields

recipe_ns = api.namespace("recipes", version="1.0", description="A name operations")


@recipe_ns.route("/", strict_slashes=False)
class RecipesResource(Resource):
    """Shows a list of all recipes, and lets you POST to add new recipes"""

    @recipe_ns.doc(recipe_resource_fields)
    @recipe_ns.marshal_list_with(recipe_resource_fields)
    def get(self):
        """List all recipes"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 6, type=int)

        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return recipes.items

    @recipe_ns.doc(body=recipe_resource_fields)
    @recipe_ns.expect(recipe_resource_fields)
    @recipe_ns.marshal_with(recipe_resource_fields, code=201)
    @jwt_required()
    def post(self):
        """Create a new recipe"""
        data = request.json
        current_user = get_jwt_identity()
        new_recipe = Recipe(
            rcp_title=data["rcp_title"], rcp_desc=data["rcp_desc"], user_id=current_user
        )
        new_recipe.save()
        recipes = (
            Recipe.query.filter_by(user_id=current_user)
            .order_by(Recipe.rcp_created.desc())
            .all()
        )
        return recipes, 201


@recipe_ns.route("/<int:id>", strict_slashes=False)
@recipe_ns.param("id", "The recipe identifier")
class RecipeResource(Resource):
    """Show a single recipe item and lets you delete them"""

    @recipe_ns.doc(body=recipe_resource_fields)
    @recipe_ns.marshal_with(recipe_resource_fields, code=201)
    def get(self, id):
        """Fetch a given resource"""
        current_user = get_jwt_identity()
        recipe = Recipe.query.filter_by(user_id=current_user, id=id).one_or_none()
        return recipe, 201

    @recipe_ns.response(int(HTTPStatus.NOT_FOUND), "Recipe not found")
    @recipe_ns.response(int(HTTPStatus.CREATED), "Recipe updated success")
    @recipe_ns.response(int(HTTPStatus.UNAUTHORIZED), "Logged required")
    @recipe_ns.expect(recipe_resource_fields)
    @recipe_ns.marshal_with(recipe_resource_fields, code=201)
    @jwt_required()
    def put(self, id):
        """Update a recipe given its identifier"""
        data = request.json
        current_user = get_jwt_identity()
        recipe = Recipe.query.filter_by(user_id=current_user, id=id).one_or_none()
        recipe.update(data["rcp_title"], data["rcp_desc"])
        return recipe

    @recipe_ns.response(int(HTTPStatus.UNAUTHORIZED), "Logged required")
    @recipe_ns.response(int(HTTPStatus.NOT_FOUND), "Recipe not found")
    @recipe_ns.response(int(HTTPStatus.NO_CONTENT), "Recipe deleted")
    @recipe_ns.doc("delete_recipe")
    @recipe_ns.marshal_with(recipe_resource_fields, code=204)
    @jwt_required()
    def delete(self):
        """Delete a recipe given its identifier"""
        current_user = get_jwt_identity()
        recipe = Recipe.query.filter_by(user_id=current_user).one_or_none()
        recipe.delete()
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes
