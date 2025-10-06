from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from bson import ObjectId
from ..db import get_collections
from ..models.schemas import VendorParameterSchema, VendorParameterCreateSchema
from ..services.audit_service import audit

blp = Blueprint(
    "Vendor Parameters",
    "vendor_parameters",
    url_prefix="/vendor-parameters",
    description="CRUD for vendor specific parameters",
)

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

@blp.route("/")
class VendorParametersList(MethodView):
    @blp.response(200, VendorParameterSchema(many=True))
    @blp.doc(summary="List vendor parameters", description="List by vendor_id with pagination and search by name.")
    def get(self):
        cols = get_collections()
        page = int(request.args.get("page", 1))
        size = min(100, int(request.args.get("size", 20)))
        vendor_id = request.args.get("vendor_id")
        search = request.args.get("search")
        q = {}
        if vendor_id:
            q["vendor_id"] = vendor_id
        if search:
            q["name"] = {"$regex": search, "$options": "i"}
        cursor = cols["vendor_parameters"].find(q).skip((page - 1) * size).limit(size)
        items = [to_str_id(x) for x in cursor]
        return items

    @blp.arguments(VendorParameterCreateSchema)
    @blp.response(201, VendorParameterSchema)
    @blp.doc(summary="Create vendor parameter", description="Create a new vendor parameter for a vendor.")
    @audit(action="create", entity="vendor_parameter")
    def post(self, payload):
        cols = get_collections()
        res = cols["vendor_parameters"].insert_one(
            {
                "vendor_id": payload["vendor_id"],
                "name": payload["name"],
                "label": payload.get("label"),
                "description": payload.get("description"),
            }
        )
        doc = cols["vendor_parameters"].find_one({"_id": res.inserted_id})
        return to_str_id(doc)

@blp.route("/<string:vp_id>")
class VendorParameterItem(MethodView):
    @blp.response(200, VendorParameterSchema)
    @blp.doc(summary="Get vendor parameter", description="Fetch by ID")
    def get(self, vp_id: str):
        cols = get_collections()
        doc = cols["vendor_parameters"].find_one({"_id": ObjectId(vp_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.arguments(VendorParameterCreateSchema)
    @blp.response(200, VendorParameterSchema)
    @blp.doc(summary="Update vendor parameter", description="Update by ID")
    @audit(action="update", entity="vendor_parameter")
    def put(self, payload, vp_id: str):
        cols = get_collections()
        cols["vendor_parameters"].update_one(
            {"_id": ObjectId(vp_id)},
            {
                "$set": {
                    "vendor_id": payload["vendor_id"],
                    "name": payload["name"],
                    "label": payload.get("label"),
                    "description": payload.get("description"),
                }
            },
        )
        doc = cols["vendor_parameters"].find_one({"_id": ObjectId(vp_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.response(204)
    @blp.doc(summary="Delete vendor parameter", description="Delete by ID")
    @audit(action="delete", entity="vendor_parameter")
    def delete(self, vp_id: str):
        cols = get_collections()
        cols["vendor_parameters"].delete_one({"_id": ObjectId(vp_id)})
        return "", 204
