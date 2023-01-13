from flask_restx import Resource

from . import api

ns = api.namespace("", description="TODO operations")


@ns.route("/hello")
class HelloResource(Resource):
    def get(self):
        return {"message": "Hello world"}
