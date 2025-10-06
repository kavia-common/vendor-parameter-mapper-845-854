from functools import wraps
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from ..db import get_collections

def _insert_audit(action: str, entity: str, entity_id: str, metadata: Optional[Dict[str, Any]] = None):
    cols = get_collections()
    cols["audit_logs"].insert_one(
        {
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }
    )

# PUBLIC_INTERFACE
def audit(action: str, entity: str):
    """Decorator to record audit events around a route handler's successful result.

    Args:
        action: e.g., "create", "update", "delete"
        entity: e.g., "vendor", "standard_parameter", "vendor_parameter", "mapping"

    Returns:
        Callable: decorator
    """
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            # attempt to find an id in result or kwargs
            entity_id = None
            if isinstance(result, tuple):
                data = result[0]
            else:
                data = result
            if isinstance(data, dict):
                entity_id = str(data.get("id") or data.get("_id") or kwargs.get("id") or kwargs.get("_id") or "")
            else:
                entity_id = str(kwargs.get("id") or "")

            try:
                _insert_audit(action, entity, entity_id, {"kwargs": kwargs})
            except Exception:
                # Auditing should not break main flow
                pass
            return result
        return wrapper
    return decorator
