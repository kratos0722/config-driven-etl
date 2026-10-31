"""Structured (JSON) logging so pipeline runs are machine-parseable in log aggregators."""

from __future__ import annotations

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Emits one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload)


def get_logger(name: str = "etl") -> logging.Logger:
    """Return a process-wide JSON logger, configured once."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
