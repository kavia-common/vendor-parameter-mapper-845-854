from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from bson import ObjectId
from ..db import get_collections
from ..models.schemas import StandardParameterSchema, StandardParameterCreateSchema
from ..services.audit_service import audit

blp = Blueprint(
    "Standard Parameters",
    "standard_parameters",
    url_prefix="/standard-parameters",
    description="CRUD for standard parameters",
)

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

@blp.route("/")
class StandardParametersList(MethodView):
    @blp.response(200, StandardParameterSchema(many=True))
    @blp.doc(summary="List standard parameters", description="List with pagination and search by key or label.")
    def get(self):
        cols = get_collections()
        page = int(request.args.get("page", 1))
        size = min(100, int(request.args.get("size", 20)))
        search = request.args.get("search")
        q = {}
        if search:
            q["$or"] = [
                {"key": {"$regex": search, "$options": "i"}},
                {"label": {"$regex": search, "$options": "i"}},
            ]
        cursor = cols["standard_parameters"].find(q).skip((page - 1) * size).limit(size)
        items = [to_str_id(x) for x in cursor]
        return items

    @blp.arguments(StandardParameterCreateSchema)
    @blp.response(201, StandardParameterSchema)
    @blp.doc(summary="Create standard parameter", description="Create a new standard parameter with unique key.")
    @audit(action="create", entity="standard_parameter")
    def post(self, payload):
        cols = get_collections()
        res = cols["standard_parameters"].insert_one(
            {"key": payload["key"], "label": payload["label"], "description": payload.get("description")}
        )
        doc = cols["standard_parameters"].find_one({"_id": res.inserted_id})
        return to_str_id(doc)

@blp.route("/<string:std_id>")
class StandardParameterItem(MethodView):
    @blp.response(200, StandardParameterSchema)
    @blp.doc(summary="Get standard parameter", description="Fetch by ID")
    def get(self, std_id: str):
        cols = get_collections()
        doc = cols["standard_parameters"].find_one({"_id": ObjectId(std_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.arguments(StandardParameterCreateSchema)
    @blp.response(200, StandardParameterSchema)
    @blp.doc(summary="Update standard parameter", description="Update by ID")
    @audit(action="update", entity="standard_parameter")
    def put(self, payload, std_id: str):
        cols = get_collections()
        cols["standard_parameters"].update_one(
            {"_id": ObjectId(std_id)},
            {"$set": {"key": payload["key"], "label": payload["label"], "description": payload.get("description")}},
        )
        doc = cols["standard_parameters"].find_one({"_id": ObjectId(std_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.response(204)
    @blp.doc(summary="Delete standard parameter", description="Delete by ID")
    @audit(action="delete", entity="standard_parameter")
    def delete(self, std_id: str):
        cols = get_collections()
        cols["standard_parameters"].delete_one({"_id": ObjectId(std_id)})
        return "", 204
