"""Main CLI entry point for QR Code Generator.

This module provides a command-line interface for generating QR codes.
"""

import argparse
import logging
import sys
from typing import NoReturn

from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

from .core.qr_generator import QRCodeGenerator
from .config.logging_config import setup_logging

def main() -> NoReturn:
    """Main entry point for the CLI application.

    Parses command-line arguments and generates QR codes accordingly.
    """
    parser = argparse.ArgumentParser(
        description="Generate QR codes from input data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main "https://example.com" -o qr_code.png
  python -m src.main "Hello World" --version 5 --error-correction H --box-size 15
  python -m src.main "Text data" -f JPEG --fill-color blue --back-color white
        """,
    )

    parser.add_argument(
        "data",
        type=str,
        help="The data to encode in the QR code (e.g., URL, text).",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output file path for the QR code image (e.g., qr_code.png).",
    )

    parser.add_argument(
        "-v", "--version",
        type=int,
        default=1,
        choices=range(1, 41),
        help="QR code version (1-40, default: 1).",
    )

    parser.add_argument(
        "-e", "--error-correction",
        type=str,
        default="M",
        choices=["L", "M", "Q", "H"],
        help="Error correction level (L, M, Q, H, default: M).",
    )

    parser.add_argument(
        "-b", "--box-size",
        type=int,
        default=10,
        help="Size of each box in pixels (default: 10).",
    )

    parser.add_argument(
        "-d", "--border",
        type=int,
        default=4,
        help="Border width in boxes (default: 4).",
    )

    parser.add_argument(
        "-f", "--fill-color",
        type=str,
        default="black",
        help="Fill color for QR modules (default: black).",
    )

    parser.add_argument(
        "-k", "--back-color",
        type=str,
        default="white",
        help="Background color (default: white).",
    )

    parser.add_argument(
        "-i", "--image-format",
        type=str,
        default="PNG",
        choices=["PNG", "JPEG", "BMP"],
        help="Output image format (PNG, JPEG, BMP, default: PNG).",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO).",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Map error correction string to int
    error_correction_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }

    try:
        logging.info(f"Creating QRCodeGenerator with data: '{args.data[:50]}...', version={args.version}, error_correction={args.error_correction}")
        generator = QRCodeGenerator(
            data=args.data,
            version=args.version,
            error_correction=error_correction_map[args.error_correction],
            box_size=args.box_size,
            border=args.border,
            fill_color=args.fill_color,
            back_color=args.back_color,
            image_format=args.image_format,
        )

        logging.info(f"Saving QR code to {args.output}")
        generator.save_qr_code(args.output)
        print(f"QR code generated successfully and saved to {args.output}")

    except ValueError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
