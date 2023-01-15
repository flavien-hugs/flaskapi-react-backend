from flask_restx import fields, inputs

from . import api


signup_resource_fields = api.model(
    "AuthSignup",
    {
        "user_fullname": fields.String(required=True, description="The user fullname"),
        "user_addr_email": fields.String(
            required=True, type=inputs.email, description="The user adresse email"
        ),
        "user_password": fields.String(required=True, description="The user password"),
    },
)


login_resource_fields = api.model(
    "AuthLogin",
    {
        "user_addr_email": fields.String(
            required=True, type=inputs.email, description="The user adresse email"
        ),
        "user_password": fields.String(required=True, description="The user password"),
    },
)


user_resource_fields = api.model(
    "User",
    {
        "id": fields.Integer(readonly=True, description="The recipe unique identifier"),
        "user_fullname": fields.String(required=True, description="The user fullname"),
        "user_addr_email": fields.String(
            required=True, type=inputs.email,  description="The user adresse email"
        )
    },
)

recipe_resource_fields = api.model(
    "Recipe",
    {
        "id": fields.Integer(readonly=True, description="The recipe unique identifier"),
        "rcp_title": fields.String(required=True, description="The recipe title"),
        "rcp_desc": fields.String(required=True, description="The recipe description"),
        "rcp_created": fields.Date(),
    },
)
