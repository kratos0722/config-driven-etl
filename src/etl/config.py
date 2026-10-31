"""Pydantic models describing a tenant's ETL pipeline, loaded from JSON or YAML.

The whole pipeline — source, ordered transforms, destination and an optional
expected output schema — is data, so a new tenant is onboarded by adding a config
file, never by changing code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["csv", "json"]
    path: str
    options: dict[str, Any] = Field(default_factory=dict)


class RenameTransform(BaseModel):
    op: Literal["rename"]
    columns: dict[str, str]


class SelectTransform(BaseModel):
    op: Literal["select"]
    columns: list[str]


class CastTransform(BaseModel):
    op: Literal["cast"]
    columns: dict[str, str]  # column -> dtype name


class FilterTransform(BaseModel):
    op: Literal["filter"]
    column: str
    predicate: Literal["==", "!=", ">", "<", ">=", "<="]
    value: Any


class AggregationSpec(BaseModel):
    column: str
    func: Literal["sum", "mean", "min", "max", "count"]
    alias: str


class AggregateTransform(BaseModel):
    op: Literal["aggregate"]
    group_by: list[str]
    aggregations: list[AggregationSpec]


Transform = Annotated[
    Union[
        RenameTransform,
        SelectTransform,
        CastTransform,
        FilterTransform,
        AggregateTransform,
    ],
    Field(discriminator="op"),
]


class DestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["duckdb", "parquet"]
    path: str
    table: str | None = None
    mode: Literal["overwrite", "append"] = "overwrite"


class PipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant: str
    source: SourceConfig
    transforms: list[Transform] = Field(default_factory=list)
    destination: DestinationConfig
    expected_schema: dict[str, str] | None = None


def load_pipeline_config(path: str | Path) -> PipelineConfig:
    """Load and validate a pipeline config from a JSON or YAML file."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if p.suffix in {".yaml", ".yml"} else json.loads(text)
    return PipelineConfig.model_validate(data)
