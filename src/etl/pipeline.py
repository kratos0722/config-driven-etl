"""Pipeline orchestration: extract -> transform -> validate -> load, with structured
logging and graceful error reporting."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from etl.config import PipelineConfig
from etl.extractors import make_extractor
from etl.loaders import make_loader
from etl.logging_setup import get_logger
from etl.schema import validate_schema
from etl.transformers import apply_all


@dataclass(frozen=True)
class PipelineResult:
    tenant: str
    rows_loaded: int
    columns: list[str]


class Pipeline:
    """Runs one tenant's configured ETL pipeline."""

    def __init__(self, config: PipelineConfig, logger: logging.Logger | None = None) -> None:
        self.config = config
        self.log = logger or get_logger("etl.pipeline")

    def run(self) -> PipelineResult:
        tenant = self.config.tenant
        self._info("pipeline.start", tenant=tenant, source=self.config.source.type)

        lf = make_extractor(self.config.source).extract()
        lf = apply_all(lf, self.config.transforms)

        if self.config.expected_schema:
            validate_schema(lf, self.config.expected_schema)
            self._info("schema.validated", tenant=tenant)

        df = lf.collect()

        rows = make_loader(self.config.destination).load(df)
        self._info(
            "pipeline.done",
            tenant=tenant,
            rows_loaded=rows,
            destination=self.config.destination.type,
        )
        return PipelineResult(tenant=tenant, rows_loaded=rows, columns=df.columns)

    def _info(self, msg: str, **fields) -> None:
        self.log.info(msg, extra={"extra_fields": fields})
