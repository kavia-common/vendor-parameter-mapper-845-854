from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from ..db import get_collections

blp = Blueprint(
    "Audit Logs",
    "audit_logs",
    url_prefix="/audit-logs",
    description="Read-only audit logs",
)

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc

@blp.route("/")
class AuditLogsList(MethodView):
    @blp.response(200)
    @blp.doc(summary="List audit logs", description="List audit logs with pagination.")
    def get(self):
        cols = get_collections()
        page = int(request.args.get("page", 1))
        size = min(100, int(request.args.get("size", 20)))
        cursor = cols["audit_logs"].find({}).sort("created_at", -1).skip((page - 1) * size).limit(size)
        items = [to_str_id(x) for x in cursor]
        return items
