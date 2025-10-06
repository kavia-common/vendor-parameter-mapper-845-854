from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from bson import ObjectId
from ..db import get_collections
from ..models.schemas import VendorSchema, VendorCreateSchema
from ..services.audit_service import audit

blp = Blueprint(
    "Vendors",
    "vendors",
    url_prefix="/vendors",
    description="CRUD operations for vendors",
)

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

@blp.route("/")
class VendorsList(MethodView):
    @blp.response(200, VendorSchema(many=True))
    @blp.doc(summary="List vendors", description="List vendors with pagination and optional search by name.")
    def get(self):
        cols = get_collections()
        page = int(request.args.get("page", 1))
        size = min(100, int(request.args.get("size", 20)))
        search = request.args.get("search")
        q = {}
        if search:
            q["name"] = {"$regex": search, "$options": "i"}
        cursor = cols["vendors"].find(q).skip((page - 1) * size).limit(size)
        items = [to_str_id(x) for x in cursor]
        return items

    @blp.arguments(VendorCreateSchema)
    @blp.response(201, VendorSchema)
    @blp.doc(summary="Create vendor", description="Create a new vendor with unique name.")
    @audit(action="create", entity="vendor")
    def post(self, payload):
        cols = get_collections()
        res = cols["vendors"].insert_one(
            {"name": payload["name"], "description": payload.get("description")}
        )
        doc = cols["vendors"].find_one({"_id": res.inserted_id})
        return to_str_id(doc)

@blp.route("/<string:vendor_id>")
class VendorItem(MethodView):
    @blp.response(200, VendorSchema)
    @blp.doc(summary="Get vendor", description="Fetch vendor by ID")
    def get(self, vendor_id: str):
        cols = get_collections()
        doc = cols["vendors"].find_one({"_id": ObjectId(vendor_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.arguments(VendorCreateSchema)
    @blp.response(200, VendorSchema)
    @blp.doc(summary="Update vendor", description="Update vendor by ID")
    @audit(action="update", entity="vendor")
    def put(self, payload, vendor_id: str):
        cols = get_collections()
        cols["vendors"].update_one(
            {"_id": ObjectId(vendor_id)},
            {"$set": {"name": payload["name"], "description": payload.get("description")}},
        )
        doc = cols["vendors"].find_one({"_id": ObjectId(vendor_id)})
        if not doc:
            return {"message": "Not found"}, 404
        return to_str_id(doc)

    @blp.response(204)
    @blp.doc(summary="Delete vendor", description="Delete vendor by ID")
    @audit(action="delete", entity="vendor")
    def delete(self, vendor_id: str):
        cols = get_collections()
        cols["vendors"].delete_one({"_id": ObjectId(vendor_id)})
        return "", 204
