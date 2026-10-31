import polars as pl
import pytest

from etl.schema import SchemaValidationError, validate_schema


def _lf() -> pl.LazyFrame:
    return pl.DataFrame({"id": [1], "name": ["a"]}).lazy()


def test_valid_schema_passes():
    validate_schema(_lf(), {"id": "int", "name": "str"})  # should not raise


def test_missing_column_fails():
    with pytest.raises(SchemaValidationError):
        validate_schema(_lf(), {"id": "int", "missing": "str"})


def test_dtype_mismatch_fails():
    with pytest.raises(SchemaValidationError):
        validate_schema(_lf(), {"id": "str"})
