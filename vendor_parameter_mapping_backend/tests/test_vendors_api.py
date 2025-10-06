import os
os.environ["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://appuser:dbuser123@localhost:5000/?authSource=admin")
os.environ["DB_NAME"] = os.getenv("DB_NAME", "vendor_param_mapper_test")

from app import create_app

def test_vendors_crud_flow():
    app = create_app()
    client = app.test_client()

    # Create
    resp = client.post("/vendors/", json={"name": "VendorA", "description": "Test vendor"})
    assert resp.status_code in (200, 201)
    created = resp.get_json()
    vid = created["id"]

    # Get
    resp = client.get(f"/vendors/{vid}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "VendorA"

    # List/search
    resp = client.get("/vendors/?search=Vendor")
    assert resp.status_code == 200
    assert any(v["name"] == "VendorA" for v in resp.get_json())

    # Update
    resp = client.put(f"/vendors/{vid}", json={"name": "VendorA-Updated", "description": "Updated"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "VendorA-Updated"

    # Delete
    resp = client.delete(f"/vendors/{vid}")
    assert resp.status_code in (200, 204)
