import pytest
from pydantic import ValidationError

from etl.config import PipelineConfig, load_pipeline_config


def test_load_yaml_config():
    cfg = load_pipeline_config("configs/acme.yaml")
    assert cfg.tenant == "acme"
    assert cfg.source.type == "csv"
    assert len(cfg.transforms) == 3
    assert cfg.destination.table == "dim_customer"


def test_unknown_transform_op_rejected():
    with pytest.raises(ValidationError):
        PipelineConfig.model_validate(
            {
                "tenant": "x",
                "source": {"type": "csv", "path": "p"},
                "transforms": [{"op": "explode"}],
                "destination": {"type": "parquet", "path": "o"},
            }
        )


def test_extra_source_field_rejected():
    with pytest.raises(ValidationError):
        PipelineConfig.model_validate(
            {
                "tenant": "x",
                "source": {"type": "csv", "path": "p", "bogus": 1},
                "destination": {"type": "parquet", "path": "o"},
            }
        )
