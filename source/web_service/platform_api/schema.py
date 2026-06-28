"""drf-spectacular glue to keep the IDE schema and the v1 schema separate.

The default ``/api/schema/`` enumerates the whole root urlconf, which now includes
``/api/v1``. This preprocessing hook drops v1 paths from that (IDE) schema. The v1
schema view scopes itself by urlconf AND sets ``PREPROCESSING_HOOKS=[]`` so this
hook does not run there (it would otherwise strip every v1 path).
"""

from __future__ import annotations


def exclude_v1_from_default(endpoints, **kwargs):
    """Filter out /api/v1 endpoints from the default schema.
    
    Args:
        endpoints: List of (path, http_method, view) tuples from drf-spectacular
        **kwargs: Additional keyword arguments passed by drf-spectacular
        
    Returns:
        Filtered list of endpoints excluding v1 paths
    """
    if endpoints is None:
        return []
    
    filtered = []
    for endpoint in endpoints:
        # Handle endpoint tuple structure: (path, http_method, view)
        if isinstance(endpoint, (list, tuple)) and len(endpoint) > 0:
            path = endpoint[0] if isinstance(endpoint[0], str) else str(endpoint[0])
            # Exclude /api/v1 paths from the default schema
            if not path.startswith("/api/v1/"):
                filtered.append(endpoint)
        else:
            # If structure is unexpected, include it to avoid breaking the schema
            filtered.append(endpoint)
    
    return filtered
