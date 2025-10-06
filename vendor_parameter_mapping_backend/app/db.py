from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.collection import Collection
from typing import Dict
import os

# PUBLIC_INTERFACE
def get_db():
    """Get the MongoDB database connection using environment variables.

    Environment:
        MONGO_URI: Mongo connection string (default mongodb://appuser:dbuser123@localhost:5000/?authSource=admin)
        DB_NAME: Database name (default vendor_param_mapper)

    Returns:
        Database: PyMongo Database instance.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://appuser:dbuser123@localhost:5000/?authSource=admin")
    db_name = os.getenv("DB_NAME", "vendor_param_mapper")
    client = MongoClient(mongo_uri)
    return client[db_name]

def _ensure_indexes():
    """Create useful indexes if missing."""
    db = get_db()
    # Vendors unique name
    db.vendors.create_index([("name", ASCENDING)], unique=True)

    # Standard parameters unique key
    db.standard_parameters.create_index([("key", ASCENDING)], unique=True)

    # Vendor parameters index per vendor
    db.vendor_parameters.create_index([("vendor_id", ASCENDING), ("name", ASCENDING)], unique=True)

    # Mappings linking and text for suggestions
    db.mappings.create_index([("vendor_id", ASCENDING), ("vendor_parameter_id", ASCENDING)], unique=True)
    db.mappings.create_index([("standard_parameter_key", TEXT), ("vendor_parameter_name", TEXT)], name="mapping_text")

    # Audit logs timestamps
    db.audit_logs.create_index([("created_at", ASCENDING)])

# Ensure indexes at import time (safe to call multiple times)
try:
    _ensure_indexes()
except Exception:
    # Avoid crashing on startup if DB isn't available; runtime actions will recreate as needed.
    pass

# PUBLIC_INTERFACE
def get_collections() -> Dict[str, Collection]:
    """Return typed dict of commonly used collections."""
    db = get_db()
    return {
        "vendors": db.vendors,
        "standard_parameters": db.standard_parameters,
        "vendor_parameters": db.vendor_parameters,
        "mappings": db.mappings,
        "audit_logs": db.audit_logs,
    }
