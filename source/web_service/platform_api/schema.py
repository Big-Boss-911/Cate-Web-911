"""Platform API v1 OpenAPI Schema Configuration

This module configures the OpenAPI schema generation for the public /api/v1 API surface,
keeping it separate from the internal IDE schema at /api/schema/.
"""

from __future__ import annotations


def exclude_v1_from_default(endpoints, **kwargs):
    """Filter out /api/v1 endpoints from the default schema.
    
    The default schema at /api/schema/ serves the internal IDE surface and should not
    include the public /api/v1 paths. This preprocessing hook removes them.
    
    Args:
        endpoints: List of (path, http_method, view) tuples from drf-spectacular
        **kwargs: Additional keyword arguments passed by drf-spectacular (ignored)
        
    Returns:
        Filtered list of endpoints excluding /api/v1 paths
        
    Raises:
        None - All errors are handled gracefully to prevent schema generation crashes
    """
    # Handle None/empty endpoints list safely
    if endpoints is None:
        return []
    
    if not isinstance(endpoints, (list, tuple)):
        # If endpoints is not iterable, return empty list to prevent crashes
        return []
    
    filtered = []
    
    for endpoint in endpoints:
        try:
            # Handle endpoint tuple structure: (path, http_method, view) or similar
            if isinstance(endpoint, (list, tuple)) and len(endpoint) > 0:
                # Safe extraction of path (first element)
                path = endpoint[0] if isinstance(endpoint[0], str) else str(endpoint[0])
                
                # Exclude /api/v1 paths from the default schema
                if not path.startswith("/api/v1/"):
                    filtered.append(endpoint)
            else:
                # If structure is unexpected, include it to avoid breaking the schema
                filtered.append(endpoint)
        except (AttributeError, TypeError, IndexError):
            # If any error occurs processing this endpoint, include it anyway
            # to prevent schema generation from failing completely
            filtered.append(endpoint)
    
    return filtered
