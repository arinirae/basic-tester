from __future__ import annotations

from typing import Any, Dict, List


def generate_value(field: Dict[str, Any]) -> Any:
    field_type = str(field.get("type", "text")).lower()
    field_name = str(field.get("name", "")).lower()
    placeholder = str(field.get("placeholder", ""))

    if any(k in field_name for k in ["email"]):
        return "test@example.com"
    if any(k in field_name for k in ["phone", "tel", "hp", "mobile"]):
        return "+628123456789"
    if any(k in field_name for k in ["name", "nama", "fullname"]):
        return "John Doe"
    if any(k in field_name for k in ["address", "alamat"]):
        return "Jl. Contoh No. 123, Jakarta"
    if any(k in field_name for k in ["city", "kota"]):
        return "Jakarta"

    type_map = {
        "email": "test@example.com",
        "password": "Test@12345",
        "number": 42,
        "tel": "+628123456789",
        "url": "https://test.com",
        "date": "2025-01-01",
        "checkbox": True,
        "textarea": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "text": placeholder or "Sample text",
        "select": None,
    }
    return type_map.get(field_type, placeholder or "test value")


def generate_values(fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    values = {}
    for field in fields:
        name = field.get("name")
        if not name:
            continue
        values[name] = generate_value(field)
    return values
