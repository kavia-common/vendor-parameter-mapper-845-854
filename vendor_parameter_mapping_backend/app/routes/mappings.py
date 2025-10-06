from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from bson import ObjectId
from ..db import get_collections
from ..models.schemas import MappingSchema, MappingCreateSchema, SuggestionQuerySchema, SuggestionResultsSchema
from ..services.audit_service import audit
from ..services.mapping_service import suggest_standard_keys

blp = Blueprint(
    "Mappings",
    "mappings",
    url_prefix="/mappings",
    description="Map vendor parameters to standard parameters",
)

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

@blp.route("/")
class MappingsList(MethodView):
    @blp.response(200, MappingSchema(many=True))
    @blp.doc(summary="List mappings", description="List mappings filtered by vendor_id or standard_parameter_key.")
    def get(self):
        cols = get_collections()
        page = int(request.args.get("page", 1))
        size = min(100, int(request.args.get("size", 20)))
        vendor_id = request.args.get("vendor_id")
        std_key = request.args.get("standard_parameter_key")
        search = request.args.get("search")
        q = {}
        if vendor_id:
            q["vendor_id"] = vendor_id
        if std_key:
            q["standard_parameter_key"] = std_key
        if search:
            q["$or"] = [
                {"vendor_parameter_name": {"$regex": search, "$options": "i"}},
                {"standard_parameter_key": {"$regex": search, "$options": "i"}},
            ]
        cursor = cols["mappings"].find(q).skip((page - 1) * size).limit(size)
        items = [to_str_id(x) for x in cursor]
        return items

    @blp.arguments(MappingCreateSchema)
    @blp.response(201, MappingSchema)
    @blp.doc(summary="Create mapping", description="Create a mapping of vendor parameter to standard parameter.")
    @audit(action="create", entity="mapping")
    def post(self, payload):
        cols = get_collections()
        res = cols["mappings"].insert_one(
            {
                "vendor_id": payload["vendor_id"],
                "vendor_parameter_id": payload["vendor_parameter_id"],
                "vendor_parameter_name": payload["vendor_parameter_name"],
                "standard_parameter_key": payload["standard_parameter_key"],
                "confidence": float(payload.get("confidence", 1.0)),
            }
        )
        doc = cols["mappings"].find_one({"_id": res.inserted_id})
        return to_str_id(doc)

@blp.route("/<string:mapping_id>")
class MappingItem(MethodView):
    @blp.response(200, MappingSchema)
    @blp.doc(summary="Get mapping", description="Fetch mapping by ID")
    def get(self, mapping_id: str):
        cols = get_collections()
        doc = cols["mappings"].find_one({"_id": ObjectId(mapping_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.arguments(MappingCreateSchema)
    @blp.response(200, MappingSchema)
    @blp.doc(summary="Update mapping", description="Update mapping by ID")
    @audit(action="update", entity="mapping")
    def put(self, payload, mapping_id: str):
        cols = get_collections()
        cols["mappings"].update_one(
            {"_id": ObjectId(mapping_id)},
            {
                "$set": {
                    "vendor_id": payload["vendor_id"],
                    "vendor_parameter_id": payload["vendor_parameter_id"],
                    "vendor_parameter_name": payload["vendor_parameter_name"],
                    "standard_parameter_key": payload["standard_parameter_key"],
                    "confidence": float(payload.get("confidence", 1.0)),
                }
            },
        )
        doc = cols["mappings"].find_one({"_id": ObjectId(mapping_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.response(204)
    @blp.doc(summary="Delete mapping", description="Delete mapping by ID")
    @audit(action="delete", entity="mapping")
    def delete(self, mapping_id: str):
        cols = get_collections()
        cols["mappings"].delete_one({"_id": ObjectId(mapping_id)})
        return "", 204

@blp.route("/suggest")
class MappingSuggest(MethodView):
    @blp.arguments(SuggestionQuerySchema, location="query")
    @blp.response(200, SuggestionResultsSchema)
    @blp.doc(
        summary="Suggest mappings",
        description="Suggest standard parameter keys for a vendor based on a text query."
    )
    def get(self, args):
        vendor_id = args["vendor_id"]
        query = args["query"]
        results = suggest_standard_keys(vendor_id, query)
        return {"results": results, "query": query}
