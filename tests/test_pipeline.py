import duckdb
import polars as pl

from etl.config import DestinationConfig, load_pipeline_config
from etl.pipeline import Pipeline


def test_acme_pipeline_filters_and_loads_to_duckdb(tmp_path):
    cfg = load_pipeline_config("configs/acme.yaml")
    db = tmp_path / "acme.duckdb"
    cfg = cfg.model_copy(
        update={"destination": DestinationConfig(type="duckdb", path=str(db), table="dim_customer")}
    )

    result = Pipeline(cfg).run()

    # Only the 3 customers with revenue > 1000 survive the filter.
    assert result.rows_loaded == 3
    assert "customer_id" in result.columns

    con = duckdb.connect(str(db))
    try:
        count = con.execute("SELECT count(*) FROM dim_customer").fetchone()[0]
    finally:
        con.close()
    assert count == 3


def test_globex_pipeline_aggregates_to_parquet(tmp_path):
    cfg = load_pipeline_config("configs/globex.yaml")
    out = tmp_path / "globex.parquet"
    cfg = cfg.model_copy(update={"destination": DestinationConfig(type="parquet", path=str(out))})

    result = Pipeline(cfg).run()

    # Paid orders aggregate to 3 regions: EMEA, APAC, AMER.
    assert result.rows_loaded == 3
    df = pl.read_parquet(out)
    emea_total = df.filter(pl.col("region") == "EMEA")["total_amount"][0]
    assert emea_total == 200.5  # 120.50 + 80.00, refunded order excluded
