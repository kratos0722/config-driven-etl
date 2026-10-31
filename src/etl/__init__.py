"""Configuration-driven, multi-tenant ETL framework.

One codebase serves many tenants; each tenant's source schema, transformations and
destination are described entirely in JSON/YAML configuration — no code changes to
onboard a new tenant.
"""

from etl.config import PipelineConfig, load_pipeline_config
from etl.pipeline import Pipeline, PipelineResult

__all__ = ["PipelineConfig", "load_pipeline_config", "Pipeline", "PipelineResult"]
