"""Config-driven transforms applied to a Polars ``LazyFrame``.

Each transform maps a validated config model to a lazy operation, so the whole chain
builds a single query plan that Polars optimizes on ``collect()``.
"""

from __future__ import annotations

import operator

import polars as pl

from etl.config import (
    AggregateTransform,
    CastTransform,
    FilterTransform,
    RenameTransform,
    SelectTransform,
    Transform,
)
from etl.dtypes import resolve_dtype

_PREDICATES = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}

_AGG_FUNCS = {
    "sum": lambda col: col.sum(),
    "mean": lambda col: col.mean(),
    "min": lambda col: col.min(),
    "max": lambda col: col.max(),
    "count": lambda col: col.count(),
}


def apply_transform(lf: pl.LazyFrame, t: Transform) -> pl.LazyFrame:
    """Apply a single transform to the lazy frame."""
    if isinstance(t, RenameTransform):
        return lf.rename(t.columns)
    if isinstance(t, SelectTransform):
        return lf.select(t.columns)
    if isinstance(t, CastTransform):
        return lf.with_columns(
            [pl.col(c).cast(resolve_dtype(d)) for c, d in t.columns.items()]
        )
    if isinstance(t, FilterTransform):
        return lf.filter(_PREDICATES[t.predicate](pl.col(t.column), t.value))
    if isinstance(t, AggregateTransform):
        exprs = [
            _AGG_FUNCS[a.func](pl.col(a.column)).alias(a.alias)
            for a in t.aggregations
        ]
        return lf.group_by(t.group_by).agg(exprs)
    raise TypeError(f"Unsupported transform: {type(t).__name__}")


def apply_all(lf: pl.LazyFrame, transforms: list[Transform]) -> pl.LazyFrame:
    """Apply an ordered list of transforms."""
    for t in transforms:
        lf = apply_transform(lf, t)
    return lf
