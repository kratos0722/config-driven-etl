"""Mapping from configuration dtype names to Polars dtypes."""

from __future__ import annotations

import polars as pl

_DTYPES: dict[str, pl.DataType] = {
    "int": pl.Int64,
    "float": pl.Float64,
    "str": pl.Utf8,
    "bool": pl.Boolean,
    "date": pl.Date,
    "datetime": pl.Datetime,
}


def resolve_dtype(name: str) -> pl.DataType:
    """Return the Polars dtype for a configuration dtype name."""
    try:
        return _DTYPES[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown dtype '{name}'. Supported: {', '.join(sorted(_DTYPES))}."
        ) from exc
