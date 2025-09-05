import requests
import jsonschema

_schema_cache = {}


def _load_schema(schema_type: str):
    """Fetch JSON Schema for a given schema.org type."""
    if schema_type in _schema_cache:
        return _schema_cache[schema_type]
    url = f"https://schema.org/{schema_type}.schema.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            schema = response.json()
            _schema_cache[schema_type] = schema
            return schema
    except Exception:
        pass
    return None


def validate(data: dict):
    """Validate structured data dict using schema.org definitions.

    Parameters
    ----------
    data: dict
        Structured data item in JSON-LD format.

    Returns
    -------
    list[str]
        List of validation error messages. Empty if valid or schema missing.
    """
    schema_type = data.get("@type")
    if isinstance(schema_type, list):
        schema_type = schema_type[0]
    if not schema_type:
        return ["Missing @type"]

    schema = _load_schema(schema_type)
    if not schema:
        return [f"Schema for {schema_type} not found at schema.org"]

    validator = jsonschema.Draft2020Validator(schema)
    return [error.message for error in validator.iter_errors(data)]
