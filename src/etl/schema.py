"""Output schema validation. Catches schema drift before loading to the warehouse."""

from __future__ import annotations

import polars as pl

from etl.dtypes import resolve_dtype


class SchemaValidationError(Exception):
    """Raised when the transformed frame does not match the expected schema."""


def validate_schema(lf: pl.LazyFrame, expected: dict[str, str]) -> None:
    """Validate the lazy frame's schema against ``expected`` (column -> dtype name).

    Uses ``collect_schema()`` so validation runs on the query plan without
    materializing the data.
    """
    actual = lf.collect_schema()
    actual_names = set(actual.names())

    missing = [c for c in expected if c not in actual_names]
    if missing:
        raise SchemaValidationError(f"Missing expected columns: {missing}")

    mismatched = []
    for col, dtype_name in expected.items():
        want = resolve_dtype(dtype_name)
        got = actual[col]
        if got != want:
            mismatched.append(f"{col}: expected {want}, got {got}")
    if mismatched:
        raise SchemaValidationError("Dtype mismatch - " + "; ".join(mismatched))
