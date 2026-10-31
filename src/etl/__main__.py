"""CLI entry point: run one config file or every config in a directory (multi-tenant)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from etl.config import load_pipeline_config
from etl.logging_setup import get_logger
from etl.pipeline import Pipeline

log = get_logger("etl")


def _collect_configs(args: argparse.Namespace) -> list[Path]:
    if args.config:
        return [Path(args.config)]
    directory = Path(args.configs_dir)
    return sorted(p for p in directory.iterdir() if p.suffix in {".yaml", ".yml", ".json"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="etl", description="Run config-driven ETL pipelines.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", help="Path to a single pipeline config file.")
    group.add_argument("--configs-dir", help="Directory of pipeline config files (one per tenant).")
    args = parser.parse_args(argv)

    exit_code = 0
    for path in _collect_configs(args):
        try:
            result = Pipeline(load_pipeline_config(path)).run()
            log.info(
                "tenant.ok",
                extra={"extra_fields": {"tenant": result.tenant, "rows": result.rows_loaded}},
            )
        except Exception as exc:  # noqa: BLE001 - report and continue other tenants
            exit_code = 1
            log.error(
                "tenant.failed",
                extra={"extra_fields": {"config": str(path), "error": str(exc)}},
            )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
