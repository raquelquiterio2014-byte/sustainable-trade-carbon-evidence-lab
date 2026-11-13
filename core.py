"""Deterministic educational calculations and evidence checks; no compliance certification."""
import hashlib
import json
from urllib.parse import urlparse
import pandas as pd
from pydantic import BaseModel, Field, field_validator

REQUIRED = {"record_id", "product", "origin", "destination", "quantity_tonnes", "production_tco2e_per_tonne", "transport_tco2e", "source_label", "source_url", "evidence_status"}

class Claim(BaseModel):
    claim: str = Field(min_length=1)
    supporting_excerpt: str = ""
    source_url: str = ""
    evidence_status: str = "unverified"
    caveats: list[str] = Field(default_factory=list)

    @field_validator("caveats", mode="before")
    @classmethod
    def normalize_caveats(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        return value

class AIResponse(BaseModel):
    summary: str
    claims: list[Claim]
    missing_evidence: list[str]
    limitations: list[str]

def is_public_http_url(value: str) -> bool:
    try:
        u = urlparse(value.strip())
        return u.scheme in ("https", "http") and bool(u.hostname) and u.hostname not in ("localhost", "127.0.0.1")
    except (ValueError, AttributeError):
        return False

def validate_trade(df: pd.DataFrame) -> list[str]:
    errors = []
    missing = REQUIRED - set(df.columns)
    if missing:
        return [f"Missing columns: {', '.join(sorted(missing))}"]
    if df.record_id.isna().any() or df.record_id.astype(str).duplicated().any():
        errors.append("Missing or duplicate record IDs")
    for col in ("quantity_tonnes", "production_tco2e_per_tonne", "transport_tco2e"):
        nums = pd.to_numeric(df[col], errors="coerce")
        if nums.isna().any() or (~nums.map(lambda x: pd.notna(x) and x >= 0 and x < float('inf'))).any():
            errors.append(f"Invalid or negative values: {col}")
    return errors

def calculate(df: pd.DataFrame) -> pd.DataFrame:
    errors = validate_trade(df)
    if errors:
        raise ValueError('; '.join(errors))
    out = df.copy()
    for col in ("quantity_tonnes", "production_tco2e_per_tonne", "transport_tco2e"):
        out[col] = pd.to_numeric(out[col])
    out["production_tco2e"] = out.quantity_tonnes * out.production_tco2e_per_tonne
    out["illustrative_total_tco2e"] = out.production_tco2e + out.transport_tco2e
    return out

def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def stable_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
