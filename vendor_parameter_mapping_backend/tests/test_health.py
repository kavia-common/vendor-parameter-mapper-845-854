import os
os.environ["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://appuser:dbuser123@localhost:5000/?authSource=admin")
os.environ["DB_NAME"] = os.getenv("DB_NAME", "vendor_param_mapper_test")

from app import create_app

def test_health_ok():
    app = create_app()
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert r.json.get("message") == "Healthy"
