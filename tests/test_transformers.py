import polars as pl

from etl.config import (
    AggregateTransform,
    AggregationSpec,
    CastTransform,
    FilterTransform,
    RenameTransform,
)
from etl.transformers import apply_transform


def _lf() -> pl.LazyFrame:
    return pl.DataFrame({"a": [1, 2, 3], "b": ["10", "20", "30"], "g": ["x", "x", "y"]}).lazy()


def test_rename():
    out = apply_transform(_lf(), RenameTransform(op="rename", columns={"a": "id"})).collect()
    assert "id" in out.columns and "a" not in out.columns


def test_cast_string_to_float():
    out = apply_transform(_lf(), CastTransform(op="cast", columns={"b": "float"})).collect()
    assert out.schema["b"] == pl.Float64


def test_filter():
    out = apply_transform(_lf(), FilterTransform(op="filter", column="a", predicate=">", value=1)).collect()
    assert out.height == 2


def test_aggregate_sum_by_group():
    t = AggregateTransform(
        op="aggregate",
        group_by=["g"],
        aggregations=[AggregationSpec(column="a", func="sum", alias="total")],
    )
    out = apply_transform(_lf(), t).collect()
    assert out.filter(pl.col("g") == "x")["total"][0] == 3
