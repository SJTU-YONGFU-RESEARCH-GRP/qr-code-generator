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
  python -m qr.main "https://example.com" -o qr_code.png
  python -m qr.main "Hello World" --version 5 --error-correction H --box-size 15
  python -m qr.main "Text data" -f JPEG --fill-color blue --back-color white
  python -m qr.main --image-to-csv qr_code.png --csv-output qr_matrix.csv
  python -m qr.main --csv-to-image qr_matrix.csv --output qr_from_matrix.png --box-size 5
        """,
    )

    parser.add_argument(
        "data",
        type=str,
        nargs='?',
        help="The data to encode in the QR code (e.g., URL, text). Not required when using --csv-input, --from-image, or --regenerate-dir.",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path for the QR code image (e.g., qr_code.png). Required for single QR generation and --from-image.",
    )

    parser.add_argument(
        "-v", "--version",
        type=int,
        default=1,
        choices=range(1, 40),
        help="QR code version (1-39, default: 1). Note: Version 40 not supported by OpenCV decoder.",
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

    # CSV functionality
    parser.add_argument(
        "--csv-output",
        type=str,
        help="Path to save CSV metadata file alongside the QR code image.",
    )

    parser.add_argument(
        "--csv-input",
        type=str,
        help="Path to CSV file containing QR code parameters for batch generation.",
    )

    parser.add_argument(
        "--csv-batch-output",
        type=str,
        help="Output directory for batch CSV processing (used with --csv-input).",
    )

    # Image input functionality
    parser.add_argument(
        "--from-image",
        type=str,
        help="Path to existing QR code image to decode and regenerate.",
    )

    parser.add_argument(
        "--regenerate-dir",
        type=str,
        help="Directory containing QR code images to regenerate.",
    )

    parser.add_argument(
        "--regenerate-output",
        type=str,
        default="regenerated",
        help="Output directory for regenerated QR codes (default: regenerated).",
    )

    # Binary matrix conversion functionality
    parser.add_argument(
        "--image-to-csv",
        type=str,
        help="Convert QR code image to CSV binary matrix format (requires --csv-output).",
    )

    parser.add_argument(
        "--csv-to-image",
        type=str,
        help="Convert CSV binary matrix to QR code image (requires --output).",
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

    # Handle different operation modes
    if args.csv_input:
        # Batch processing from CSV
        try:
            output_dir = args.csv_batch_output or "qr_batch_output"
            csv_output = args.csv_output if hasattr(args, 'csv_output') and args.csv_output else None

            logging.info(f"Processing CSV batch from {args.csv_input}")
            successful = QRCodeGenerator.process_csv_batch(
                csv_input_path=args.csv_input,
                output_dir=output_dir,
                csv_output_path=csv_output
            )
            print(f"Successfully processed {successful} QR codes from CSV")

        except ValueError as e:
            logging.error(f"CSV processing error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during CSV processing: {e}")
            sys.exit(1)

    elif args.regenerate_dir:
        # Regenerate from directory of images
        try:
            # Extract override parameters from args
            override_params = {}
            if hasattr(args, 'version') and args.version != 1:
                override_params['version'] = args.version
            if hasattr(args, 'error_correction'):
                override_params['error_correction'] = error_correction_map[args.error_correction]
            if hasattr(args, 'box_size') and args.box_size != 10:
                override_params['box_size'] = args.box_size
            if hasattr(args, 'border') and args.border != 4:
                override_params['border'] = args.border
            if hasattr(args, 'fill_color') and args.fill_color != "black":
                override_params['fill_color'] = args.fill_color
            if hasattr(args, 'back_color') and args.back_color != "white":
                override_params['back_color'] = args.back_color
            if hasattr(args, 'image_format') and args.image_format != "PNG":
                override_params['image_format'] = args.image_format

            logging.info(f"Regenerating QR codes from directory {args.regenerate_dir}")
            successful = QRCodeGenerator.regenerate_from_images(
                input_dir=args.regenerate_dir,
                output_dir=args.regenerate_output,
                **override_params
            )
            print(f"Successfully regenerated {successful} QR codes")

        except ValueError as e:
            logging.error(f"Image regeneration error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during image regeneration: {e}")
            sys.exit(1)

    elif args.from_image:
        # Regenerate from single image
        try:
            logging.info(f"Decoding QR code from {args.from_image}")

            # Extract override parameters
            override_params = {}
            if args.version != 1:
                override_params['version'] = args.version
            if args.error_correction != "M":
                override_params['error_correction'] = error_correction_map[args.error_correction]
            if args.box_size != 10:
                override_params['box_size'] = args.box_size
            if args.border != 4:
                override_params['border'] = args.border
            if args.fill_color != "black":
                override_params['fill_color'] = args.fill_color
            if args.back_color != "white":
                override_params['back_color'] = args.back_color
            if args.image_format != "PNG":
                override_params['image_format'] = args.image_format

            generator = QRCodeGenerator.from_image(args.from_image, **override_params)

            logging.info(f"Regenerating QR code to {args.output}")
            if args.csv_output:
                generator.save_qr_code_with_csv(args.output, args.csv_output)
            else:
                generator.save_qr_code(args.output)
            print(f"QR code regenerated successfully and saved to {args.output}")

        except ValueError as e:
            logging.error(f"Image regeneration error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during image regeneration: {e}")
            sys.exit(1)

    elif args.image_to_csv:
        # Convert QR code image to CSV matrix
        try:
            if not args.csv_output:
                parser.error("--csv-output is required when using --image-to-csv")

            logging.info(f"Converting QR code image {args.image_to_csv} to CSV matrix")
            QRCodeGenerator.image_to_csv_matrix(args.image_to_csv, args.csv_output)
            print(f"QR code image converted to CSV matrix successfully: {args.csv_output}")

        except ValueError as e:
            logging.error(f"Image to CSV conversion error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during image to CSV conversion: {e}")
            sys.exit(1)

    elif args.csv_to_image:
        # Convert CSV matrix to QR code image
        try:
            if not args.output:
                parser.error("--output is required when using --csv-to-image")

            # Extract box_size from args if provided
            box_size = getattr(args, 'box_size', 1) if hasattr(args, 'box_size') else 1

            logging.info(f"Converting CSV matrix {args.csv_to_image} to QR code image")
            QRCodeGenerator.csv_matrix_to_image(args.csv_to_image, args.output, box_size)
            print(f"CSV matrix converted to QR code image successfully: {args.output}")

        except ValueError as e:
            logging.error(f"CSV to image conversion error: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error during CSV to image conversion: {e}")
            sys.exit(1)

    else:
        # Standard single QR code generation
        if not args.data:
            parser.error("--data is required for single QR code generation")
        if not args.output:
            parser.error("--output is required for single QR code generation")

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
            if args.csv_output:
                generator.save_qr_code_with_csv(args.output, args.csv_output)
            else:
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
