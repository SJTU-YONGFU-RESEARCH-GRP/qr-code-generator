"""Logging configuration for the QR Code Generator.

This module sets up logging for the application with configurable levels.
"""

import logging
from typing import Literal

def setup_logging(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO") -> None:
    """Set up logging for the application.

    Args:
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR"]): The logging level to set.

    Raises:
        ValueError: If an invalid logging level is provided.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
