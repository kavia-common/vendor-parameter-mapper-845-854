from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from dotenv import load_dotenv
import os

# Import blueprints lazily inside create_app to avoid circular imports
# PUBLIC_INTERFACE
def create_app() -> Flask:
    """Create and configure the Flask application with CORS, OpenAPI, and blueprints.
    Returns:
        Flask: Configured Flask application.
    """
    load_dotenv()

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # OpenAPI / Swagger config
    app.config["API_TITLE"] = "Vendor Parameter Mapping API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # CORS - allow localhost:3000
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS(app, resources={r"/*": {"origins": cors_origins}})

    api = Api(app)

    # Register blueprints
    from .routes.health import blp as health_blp
    from .routes.vendors import blp as vendors_blp
    from .routes.standard_parameters import blp as std_params_blp
    from .routes.vendor_parameters import blp as vendor_params_blp
    from .routes.mappings import blp as mappings_blp
    from .routes.audit_logs import blp as audit_logs_blp

    api.register_blueprint(health_blp)
    api.register_blueprint(vendors_blp)
    api.register_blueprint(std_params_blp)
    api.register_blueprint(vendor_params_blp)
    api.register_blueprint(mappings_blp)
    api.register_blueprint(audit_logs_blp)

    # Expose api for OpenAPI generation modules
    app.extensions["smorest_api"] = api
    return app

# Keep backward compatibility for modules importing app/api directly
app = create_app()
api = app.extensions["smorest_api"]
