from marshmallow import Schema, fields

# Shared pagination metadata schema
class PaginationMetadata(Schema):
    total = fields.Int()
    total_pages = fields.Int()
    first_page = fields.Int()
    last_page = fields.Int()
    page = fields.Int()
    previous_page = fields.Int(allow_none=True)
    next_page = fields.Int(allow_none=True)

# Vendors
class VendorSchema(Schema):
    id = fields.Str(dump_only=True, description="Vendor ID as string")
    name = fields.Str(required=True, description="Vendor name")
    description = fields.Str(allow_none=True, description="Optional vendor description")

class VendorCreateSchema(Schema):
    name = fields.Str(required=True, description="Vendor name")
    description = fields.Str(allow_none=True, description="Optional vendor description")

# Standard Parameters
class StandardParameterSchema(Schema):
    id = fields.Str(dump_only=True)
    key = fields.Str(required=True, description="Unique standard parameter key")
    label = fields.Str(required=True, description="Human-friendly label")
    description = fields.Str(allow_none=True)

class StandardParameterCreateSchema(Schema):
    key = fields.Str(required=True)
    label = fields.Str(required=True)
    description = fields.Str(allow_none=True)

# Vendor Parameters
class VendorParameterSchema(Schema):
    id = fields.Str(dump_only=True)
    vendor_id = fields.Str(required=True, description="Vendor ID")
    name = fields.Str(required=True, description="Parameter name at vendor")
    label = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)

class VendorParameterCreateSchema(Schema):
    vendor_id = fields.Str(required=True)
    name = fields.Str(required=True)
    label = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)

# Mappings
class MappingSchema(Schema):
    id = fields.Str(dump_only=True)
    vendor_id = fields.Str(required=True)
    vendor_parameter_id = fields.Str(required=True)
    vendor_parameter_name = fields.Str(required=True, description="Cached name for suggestions/search")
    standard_parameter_key = fields.Str(required=True)
    confidence = fields.Float(required=True, description="Confidence score between 0 and 1")

class MappingCreateSchema(Schema):
    vendor_id = fields.Str(required=True)
    vendor_parameter_id = fields.Str(required=True)
    vendor_parameter_name = fields.Str(required=True)
    standard_parameter_key = fields.Str(required=True)
    confidence = fields.Float(missing=1.0)

# Suggestion
class SuggestionQuerySchema(Schema):
    vendor_id = fields.Str(required=True)
    query = fields.Str(required=True, description="Text of parameter input to match")

class SuggestionResultItemSchema(Schema):
    standard_parameter_key = fields.Str()
    confidence = fields.Float()
    vendor_parameter_name = fields.Str()

class SuggestionResultsSchema(Schema):
    results = fields.List(fields.Nested(SuggestionResultItemSchema))
    query = fields.Str()

# Audit Logs
class AuditLogSchema(Schema):
    id = fields.Str(dump_only=True)
    action = fields.Str(required=True)
    entity = fields.Str(required=True)
    entity_id = fields.Str(required=True)
    metadata = fields.Dict()
    created_at = fields.DateTime()

class AuditLogCreateSchema(Schema):
    action = fields.Str(required=True)
    entity = fields.Str(required=True)
    entity_id = fields.Str(required=True)
    metadata = fields.Dict()
