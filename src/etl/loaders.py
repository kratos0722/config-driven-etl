"""Destination loaders. Each takes a materialized Polars frame and persists it,
returning the number of rows written."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import duckdb
import polars as pl

from etl.config import DestinationConfig


class Loader(ABC):
    @abstractmethod
    def load(self, df: pl.DataFrame) -> int: ...


class DuckDbLoader(Loader):
    """Loads into a DuckDB table (the local analytical warehouse)."""

    def __init__(self, path: str, table: str, mode: str = "overwrite") -> None:
        if not table:
            raise ValueError("DuckDB destination requires a 'table'.")
        self.path = path
        self.table = table
        self.mode = mode

    def load(self, df: pl.DataFrame) -> int:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect(self.path)
        try:
            # DuckDB scans the local Polars frame `df` directly (replacement scan).
            if self.mode == "overwrite":
                con.execute(f'CREATE OR REPLACE TABLE "{self.table}" AS SELECT * FROM df')
            else:  # append
                con.execute(f'CREATE TABLE IF NOT EXISTS "{self.table}" AS SELECT * FROM df WHERE 1=0')
                con.execute(f'INSERT INTO "{self.table}" SELECT * FROM df')
            return df.height
        finally:
            con.close()


class ParquetLoader(Loader):
    """Writes the frame to a Parquet file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def load(self, df: pl.DataFrame) -> int:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(self.path)
        return df.height


def make_loader(config: DestinationConfig) -> Loader:
    """Factory: resolve the loader for a destination config."""
    match config.type:
        case "duckdb":
            return DuckDbLoader(config.path, config.table or "", config.mode)
        case "parquet":
            return ParquetLoader(config.path)
    raise ValueError(f"Unsupported destination type '{config.type}'.")
