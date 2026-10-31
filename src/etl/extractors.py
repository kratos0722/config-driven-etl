"""Source extractors. Each returns a Polars ``LazyFrame`` so the transform plan stays
lazy and Polars can optimize it before any data is materialized."""

from __future__ import annotations

from abc import ABC, abstractmethod

import polars as pl

from etl.config import SourceConfig


class Extractor(ABC):
    """Reads a source into a lazy frame."""

    @abstractmethod
    def extract(self) -> pl.LazyFrame: ...


class CsvExtractor(Extractor):
    def __init__(self, path: str, options: dict | None = None) -> None:
        self.path = path
        self.options = options or {}

    def extract(self) -> pl.LazyFrame:
        return pl.scan_csv(self.path, **self.options)


class JsonExtractor(Extractor):
    def __init__(self, path: str, options: dict | None = None) -> None:
        self.path = path
        self.options = options or {}

    def extract(self) -> pl.LazyFrame:
        # Polars reads a JSON array eagerly; make it lazy to share one transform path.
        return pl.read_json(self.path, **self.options).lazy()


def make_extractor(config: SourceConfig) -> Extractor:
    """Factory: resolve the extractor for a source config."""
    match config.type:
        case "csv":
            return CsvExtractor(config.path, config.options)
        case "json":
            return JsonExtractor(config.path, config.options)
    raise ValueError(f"Unsupported source type '{config.type}'.")
