# vendor-parameter-mapper-845-854

Integration notes:
- Database: Ensure MongoDB is running (default dev port 5000). Provide credentials matching your MONGO_URI user.
- Backend env (.env in vendor_parameter_mapping_backend):
  - MONGO_URI=mongodb://appuser:dbuser123@localhost:5000/?authSource=admin
  - DB_NAME=myapp
  - CORS_ORIGINS=http://localhost:3000
- Generate OpenAPI: from vendor_parameter_mapping_backend run `python generate_openapi.py` to refresh interfaces/openapi.json.
- Frontend env (.env in vendor_parameter_mapping_frontend):
  - REACT_APP_API_BASE=http://localhost:3001
- Notes:
  - Flask app serves API and docs at /docs. CORS will allow the configured origin.
  - Update env variables via .env without changing code.