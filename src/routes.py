from flask import request
from flask_restx import Resource

from . import api
from .models import Recipe
from .resources import recipe_resource_model

ns = api.namespace("", description="RECIPE operations")


@ns.route("/recipes")
class RecipesResource(Resource):
    '''Shows a list of all recipes, and lets you POST to add new recipes'''

    @ns.doc('list_recipes')
    @ns.marshal_list_with(recipe_resource_model, code=200)
    def get(self):
        '''List all recipes'''
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes, 200

    @ns.doc('create_recipe')
    @ns.expect(recipe_resource_model)
    @ns.marshal_with(recipe_resource_model, code=201)
    def post(self):
        """Create a new recipe"""
        data = request.json
        new_recipe = Recipe(rcp_title=data["rcp_title"], rcp_desc=data['rcp_desc'])
        new_recipe.save()
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes, 201


@ns.route("/recipe/<int:id>")
@ns.response(404, 'Recipe not found')
@ns.param('id', 'The recipe identifier')
class RecipeResource(Resource):
    """Show a single recipe item and lets you delete them"""

    @ns.doc('get_recipe')
    @ns.marshal_with(recipe_resource_model, code=201)
    def get(self, id):
        """Fetch a given resource"""
        recipe = Recipe.query.get_or_404(id)
        return recipe, 201

    @ns.expect(recipe_resource_model)
    @ns.marshal_with(recipe_resource_model, code=201)
    def put(self, id):
        '''Update a recipe given its identifier'''
        data = request.json
        recipe = Recipe.query.get_or_404(id)
        recipe.update(data['rcp_title'], data['rcp_desc'])
        return recipe, 201

    @ns.doc('delete_recipe')
    @ns.response(204, 'Recipe deleted')
    @ns.marshal_with(recipe_resource_model, code=204)
    def delete(self, id):
        '''Delete a recipe given its identifier'''
        recipe = Recipe.query.get_or_404(id)
        recipe.delete()
        recipes = Recipe.query.order_by(Recipe.rcp_created.desc()).all()
        return recipes, 200
