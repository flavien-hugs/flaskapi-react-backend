from flask_restx import fields

from . import api


recipe_resource_fields = api.model('Recipe', {
    'id': fields.Integer(readonly=True, description='The recipe unique identifier'),
    'rcp_title': fields.String(required=True, description='The recipe title'),
    'rcp_desc': fields.String(required=True, description='The recipe description'),
    'rcp_created':  fields.Date()
})
