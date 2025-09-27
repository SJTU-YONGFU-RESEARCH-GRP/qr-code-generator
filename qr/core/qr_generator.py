"""QR Code Generator Module.

This module provides functionality to generate QR codes from input data with pattern customization.
"""

import csv
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

try:
    from PIL import Image as PILImage
    PYZBAR_AVAILABLE = True
    # Import pyzbar only when needed to avoid Windows DLL issues
    def _import_pyzbar():
        from pyzbar.pyzbar import decode as pyzbar_decode
        return pyzbar_decode
except ImportError:
    PYZBAR_AVAILABLE = False
    def _import_pyzbar():
        raise ImportError("pyzbar not available")

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """A class for generating QR codes with customizable options and pattern control.

    This class handles the creation of QR codes from text data, supporting
    various error correction levels, box sizes, output formats, and pattern customization
    for testing and analysis purposes.

    Attributes:
        data (str): The data to encode in the QR code.
        version (int): The QR code version (1-39*). *Version 40 not supported by OpenCV decoder.
        error_correction (qrcode.constants.ERROR_CORRECT): Error correction level.
        box_size (int): Size of each box in pixels.
        border (int): Border width in boxes.
        fill_color (str): Color for the QR code modules.
        back_color (str): Background color.
        image_format (str): Output image format (e.g., 'PNG', 'JPEG').
        finder_patterns (bool): Whether to include finder patterns (corner squares).
        alignment_patterns (bool): Whether to include alignment patterns.
        timing_patterns (bool): Whether to include timing patterns.
        version_info (bool): Whether to include version information.
        format_info (bool): Whether to include format information.
    """

    def __init__(
        self,
        data: str,
        version: int = 1,
        error_correction: int = ERROR_CORRECT_M,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        image_format: str = "PNG",
        finder_patterns: bool = True,
        alignment_patterns: bool = True,
        timing_patterns: bool = True,
        version_info: bool = True,
        format_info: bool = True,
    ) -> None:
        """Initialize the QR Code Generator.

        Args:
            data (str): The data to encode in the QR code.
            version (int): QR code version (1-39, default: 1). Version 40 not supported by OpenCV decoder.
            error_correction (int): Error correction level (0=L, 1=M, 2=Q, 3=H, default: 1).
            box_size (int): Size of each box in pixels (default: 10).
            border (int): Border width in boxes (default: 4).
            fill_color (str): Color for QR modules (default: "black").
            back_color (str): Background color (default: "white").
            image_format (str): Output image format (default: "PNG").
            finder_patterns (bool): Whether to include finder patterns (default: True).
            alignment_patterns (bool): Whether to include alignment patterns (default: True).
            timing_patterns (bool): Whether to include timing patterns (default: True).
            version_info (bool): Whether to include version information (default: True).
            format_info (bool): Whether to include format information (default: True).

        Raises:
            ValueError: If version is not between 1 and 39, or if box_size/border are non-positive.
        """
        if not (1 <= version <= 39):
            raise ValueError("Version must be between 1 and 39. Version 40 is not supported by OpenCV decoder.")
        if box_size <= 0:
            raise ValueError("Box size must be positive.")
        if border <= 0:
            raise ValueError("Border must be positive.")
        if error_correction not in [ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H]:
            raise ValueError("Invalid error correction level.")

        self.data = data
        self.version = version
        self.error_correction = error_correction
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color
        self.image_format = image_format
        self.finder_patterns = finder_patterns
        self.alignment_patterns = alignment_patterns
        self.timing_patterns = timing_patterns
        self.version_info = version_info
        self.format_info = format_info

        logger.info(
            f"QRCodeGenerator initialized for data: '{data[:50]}...' with version {version}, "
            f"error correction {['L', 'M', 'Q', 'H'][error_correction]}, box_size {box_size}, border {border}, "
            f"fill_color {fill_color}, back_color {back_color}, format {image_format}, "
            f"patterns: finder={finder_patterns}, alignment={alignment_patterns}, timing={timing_patterns}, "
            f"version_info={version_info}, format_info={format_info}."
        )

    def generate_qr_code(self) -> qrcode.QRCode:
        """Generate the QR code object.

        Returns:
            qrcode.QRCode: The generated QR code object.

        Raises:
            qrcode.exceptions.DataOverflowError: If data is too large for the specified version.
            ValueError: If invalid parameters are provided.
        """
        try:
            logger.debug(f"Creating QRCode object with version={self.version}, error_correction={self.error_correction}, box_size={self.box_size}, border={self.border}")
            qr = qrcode.QRCode(
                version=self.version,
                error_correction=self.error_correction,
                box_size=self.box_size,
                border=self.border,
            )
            logger.debug(f"Adding data to QR code: '{self.data[:50]}...'")
            qr.add_data(self.data)
            logger.debug("Making QR code with fit=True")
            qr.make(fit=True)

            logger.info("QR code generated successfully.")
            return qr

        except qrcode.exceptions.DataOverflowError as e:
            logger.error(f"Data overflow error: {e}")
            raise ValueError(f"Data too large for version {self.version}. Try increasing the version.") from e
        except Exception as e:
            logger.error(f"Unexpected error generating QR code: {e}")
            raise ValueError("Failed to generate QR code due to invalid parameters.") from e

    def save_qr_code(self, output_path: Union[str, Path]) -> None:
        """Save the QR code to an image file.

        Args:
            output_path (Union[str, Path]): Path to save the image file.

        Raises:
            ValueError: If the image cannot be saved.
        """
        qr = self.generate_qr_code()
        output_path = Path(output_path)

        try:
            # Generate QR code matrix and apply pattern customizations
            qr_matrix = np.array(qr.get_matrix(), dtype=np.uint8)

            # Apply pattern customizations if any patterns are disabled
            if not (self.finder_patterns and self.alignment_patterns and
                    self.timing_patterns and self.version_info and self.format_info):
                qr_matrix = self._apply_pattern_customizations(qr_matrix)

            logger.debug(f"Creating image with fill_color={self.fill_color}, back_color={self.back_color}")
            # Create image from the modified matrix
            img = self._create_image_from_matrix(qr_matrix)
            logger.debug(f"Saving image to {output_path} in format {self.image_format}")
            img.save(output_path, self.image_format)
            logger.info(f"QR code saved successfully to {output_path}.")
        except Exception as e:
            logger.error(f"Error saving QR code to {output_path}: {e}")
            raise ValueError(f"Failed to save QR code to {output_path}.") from e

    def get_qr_code_image(self) -> Image.Image:
        """Get the QR code as a PIL Image object.

        Returns:
            Image.Image: The QR code image.

        Raises:
            ValueError: If the image cannot be generated.
        """
        qr = self.generate_qr_code()

        try:
            # Generate QR code matrix and apply pattern customizations
            qr_matrix = np.array(qr.get_matrix(), dtype=np.uint8)

            # Apply pattern customizations if any patterns are disabled
            if not (self.finder_patterns and self.alignment_patterns and
                    self.timing_patterns and self.version_info and self.format_info):
                qr_matrix = self._apply_pattern_customizations(qr_matrix)

            logger.debug(f"Creating image object with fill_color={self.fill_color}, back_color={self.back_color}")
            # Create image from the modified matrix
            img = self._create_image_from_matrix(qr_matrix)
            logger.info(f"QR code image generated successfully (size: {img.size}).")
            return img
        except Exception as e:
            logger.error(f"Error generating QR code image: {e}")
            raise ValueError("Failed to generate QR code image.") from e

    def _create_image_from_matrix(self, qr_matrix: np.ndarray) -> Image.Image:
        """Create PIL Image from QR code matrix with colors.

        Args:
            qr_matrix (np.ndarray): QR code matrix (0=white, 1=black).

        Returns:
            Image.Image: PIL Image object.
        """
        # Create image from matrix
        height, width = qr_matrix.shape
        img_array = np.zeros((height * self.box_size, width * self.box_size), dtype=np.uint8)

        # Fill image array based on matrix values
        for i in range(height):
            for j in range(width):
                if qr_matrix[i, j] == 1:  # Black/dark module
                    fill_value = 0  # Black
                else:  # White/light module
                    fill_value = 255  # White

                # Fill the corresponding block
                img_array[i * self.box_size:(i + 1) * self.box_size,
                         j * self.box_size:(j + 1) * self.box_size] = fill_value

        # Create PIL image
        img = Image.fromarray(img_array, mode='L')

        # Apply colors if specified (convert to RGB for colored output)
        if self.fill_color != "black" or self.back_color != "white":
            # Convert to RGB
            img = img.convert('RGB')

            # Create color mapping
            pixels = img.load()
            for i in range(img.size[0]):
                for j in range(img.size[1]):
                    if pixels[i, j] == (0, 0, 0):  # Black pixel
                        # Parse fill_color (could be "black", "blue", "#FF0000", etc.)
                        try:
                            from PIL import ImageColor
                            pixels[i, j] = ImageColor.getrgb(self.fill_color)
                        except:
                            pixels[i, j] = (0, 0, 0)  # Fallback to black
                    else:  # White pixel
                        # Parse back_color
                        try:
                            from PIL import ImageColor
                            pixels[i, j] = ImageColor.getrgb(self.back_color)
                        except:
                            pixels[i, j] = (255, 255, 255)  # Fallback to white

        return img

    def _apply_pattern_customizations(self, qr_matrix: np.ndarray) -> np.ndarray:
        """Apply pattern customizations to the QR code matrix.

        Args:
            qr_matrix (np.ndarray): The QR code matrix to modify.

        Returns:
            np.ndarray: The modified QR code matrix with pattern customizations applied.
        """
        logger.debug("Applying pattern customizations to QR matrix")

        # Finder patterns are the 3 corner squares (7x7 for version 1, larger for higher versions)
        # They consist of a 3x3 black square with a 5x5 white border and 7x7 black border
        matrix_size = len(qr_matrix)

        if not self.finder_patterns:
            logger.debug("Removing finder patterns")
            self._remove_finder_patterns(qr_matrix, matrix_size)

        if not self.alignment_patterns and self.version > 1:
            logger.debug("Removing alignment patterns")
            self._remove_alignment_patterns(qr_matrix, matrix_size)

        if not self.timing_patterns:
            logger.debug("Removing timing patterns")
            self._remove_timing_patterns(qr_matrix, matrix_size)

        if not self.version_info and self.version >= 7:
            logger.debug("Removing version information")
            self._remove_version_info(qr_matrix, matrix_size)

        if not self.format_info:
            logger.debug("Removing format information")
            self._remove_format_info(qr_matrix, matrix_size)

        return qr_matrix

    def _remove_finder_patterns(self, qr_matrix: np.ndarray, matrix_size: int) -> None:
        """Remove finder patterns from QR code matrix.

        Args:
            qr_matrix (np.ndarray): QR code matrix to modify.
            matrix_size (int): Size of the matrix.
        """
        # Finder patterns are located at:
        # - Top-left: rows 0-8, cols 0-8 (for version 1)
        # - Top-right: rows 0-8, cols matrix_size-9 to matrix_size-1
        # - Bottom-left: rows matrix_size-9 to matrix_size-1, cols 0-8

        finder_size = 9  # Standard finder pattern size including quiet zone

        # Top-left finder pattern
        qr_matrix[0:finder_size, 0:finder_size] = 0

        # Top-right finder pattern
        qr_matrix[0:finder_size, matrix_size-finder_size:matrix_size] = 0

        # Bottom-left finder pattern
        qr_matrix[matrix_size-finder_size:matrix_size, 0:finder_size] = 0

    def _remove_alignment_patterns(self, qr_matrix: np.ndarray, matrix_size: int) -> None:
        """Remove alignment patterns from QR code matrix.

        Args:
            qr_matrix (np.ndarray): QR code matrix to modify.
            matrix_size (int): Size of the matrix.
        """
        # Alignment patterns appear in QR codes version 2 and above
        # They are 5x5 patterns for most versions
        if self.version < 2:
            return

        # Get alignment pattern positions for this version
        alignment_positions = self._get_alignment_pattern_positions()

        for row, col in alignment_positions:
            if 0 <= row < matrix_size and 0 <= col < matrix_size:
                # Remove 5x5 alignment pattern centered at (row, col)
                start_row = max(0, row - 2)
                end_row = min(matrix_size, row + 3)
                start_col = max(0, col - 2)
                end_col = min(matrix_size, col + 3)

                qr_matrix[start_row:end_row, start_col:end_col] = 0

    def _get_alignment_pattern_positions(self) -> List[Tuple[int, int]]:
        """Get alignment pattern positions for the current QR code version.

        Returns:
            List[Tuple[int, int]]: List of (row, col) positions for alignment patterns.
        """
        # Standard QR code alignment pattern positions
        # For version 1: no alignment patterns
        # For version 2+: positions depend on version

        if self.version == 1:
            return []

        # Simplified alignment pattern positions for common versions
        alignment_patterns = {
            2: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7)],
            3: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7), (matrix_size - 7, matrix_size - 7)],
            4: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7)],
            5: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7), (matrix_size - 7, matrix_size - 7)],
            6: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7)],
            7: [(6, 6), (matrix_size - 7, 6), (6, matrix_size - 7), (matrix_size - 7, matrix_size - 7)],
        }

        matrix_size = 21 + (self.version - 1) * 4  # Calculate actual matrix size
        positions = alignment_patterns.get(self.version, [])

        # Add center alignment pattern for larger versions
        if self.version >= 8:
            center_pos = matrix_size // 2
            if (center_pos, center_pos) not in positions:
                positions.append((center_pos, center_pos))

        return positions

    def _remove_timing_patterns(self, qr_matrix: np.ndarray, matrix_size: int) -> None:
        """Remove timing patterns from QR code matrix.

        Args:
            qr_matrix (np.ndarray): QR code matrix to modify.
            matrix_size (int): Size of the matrix.
        """
        # Timing patterns are alternating black/white lines between finder patterns
        # Horizontal timing pattern: row 6, columns 8 to matrix_size-9
        # Vertical timing pattern: column 6, rows 8 to matrix_size-9

        # Horizontal timing pattern (skip finder pattern areas)
        for col in range(8, matrix_size - 8):
            if col != 6:  # Skip the vertical timing pattern intersection
                qr_matrix[6, col] = 0

        # Vertical timing pattern (skip finder pattern areas)
        for row in range(8, matrix_size - 8):
            if row != 6:  # Skip the horizontal timing pattern intersection
                qr_matrix[row, 6] = 0

    def _remove_version_info(self, qr_matrix: np.ndarray, matrix_size: int) -> None:
        """Remove version information from QR code matrix.

        Args:
            qr_matrix (np.ndarray): QR code matrix to modify.
            matrix_size (int): Size of the matrix.
        """
        # Version information appears in version 7+ QR codes
        # Located at: rows 0-5, columns matrix_size-11 to matrix_size-9 (top-right)
        # And: columns 0-5, rows matrix_size-11 to matrix_size-9 (bottom-left)

        if self.version < 7:
            return

        # Top-right version info
        qr_matrix[0:6, matrix_size-11:matrix_size-8] = 0

        # Bottom-left version info
        qr_matrix[matrix_size-11:matrix_size-8, 0:6] = 0

    def _remove_format_info(self, qr_matrix: np.ndarray, matrix_size: int) -> None:
        """Remove format information from QR code matrix.

        Args:
            qr_matrix (np.ndarray): QR code matrix to modify.
            matrix_size (int): Size of the matrix.
        """
        # Format information is located near finder patterns
        # Top: row 8, columns 0-8 (but skip finder pattern)
        # Bottom: column 8, rows matrix_size-8 to matrix_size-1 (but skip finder pattern)
        # Left: column 8, rows 0-8 (but skip finder pattern)
        # Right: row 8, columns matrix_size-8 to matrix_size-1 (but skip finder pattern)

        # Remove format info areas (set to 0 = white)
        # Top format info (row 8, columns 0-5 and 7-8)
        qr_matrix[8, 0:6] = 0
        qr_matrix[8, 7:9] = 0

        # Bottom format info (column 8, rows matrix_size-8 to matrix_size-1, but skip last 8)
        bottom_start = matrix_size - 8
        qr_matrix[bottom_start:matrix_size-1, 8] = 0

        # Left format info (column 8, rows 0-5 and 7-8)
        qr_matrix[0:6, 8] = 0
        qr_matrix[7:9, 8] = 0

        # Right format info (row 8, columns matrix_size-8 to matrix_size-1, but skip first 8)
        right_start = matrix_size - 8
        qr_matrix[8, right_start:matrix_size-1] = 0

    def save_qr_code_with_csv(
        self,
        image_path: Union[str, Path],
        csv_path: Optional[Union[str, Path]] = None,
        include_metadata: bool = True,
    ) -> None:
        """Save QR code image and optionally generate CSV metadata.

        Args:
            image_path (Union[str, Path]): Path to save the QR code image.
            csv_path (Optional[Union[str, Path]]): Path to save CSV metadata.
            include_metadata (bool): Whether to include file metadata in CSV.

        Raises:
            ValueError: If saving fails.
        """
        # Save the image first
        self.save_qr_code(image_path)

        # Generate CSV if requested
        if csv_path:
            self._save_metadata_to_csv(csv_path, image_path, include_metadata)

    def _save_metadata_to_csv(
        self,
        csv_path: Union[str, Path],
        image_path: Union[str, Path],
        include_metadata: bool,
    ) -> None:
        """Save QR code metadata to CSV file.

        Args:
            csv_path (Union[str, Path]): Path to the CSV file.
            image_path (Union[str, Path]): Path to the associated image file.
            include_metadata (bool): Whether to include file metadata.
        """
        import os
        from datetime import datetime

        csv_path = Path(csv_path)
        image_path = Path(image_path)

        # Map error correction level back to string
        error_correction_map = {
            ERROR_CORRECT_L: "L",
            ERROR_CORRECT_M: "M",
            ERROR_CORRECT_Q: "Q",
            ERROR_CORRECT_H: "H",
        }

        # Prepare CSV data
        csv_data = {
            "data": self.data,
            "version": self.version,
            "error_correction": error_correction_map.get(self.error_correction, str(self.error_correction)),
            "box_size": self.box_size,
            "border": self.border,
            "fill_color": self.fill_color,
            "back_color": self.back_color,
            "image_format": self.image_format,
            "finder_patterns": self.finder_patterns,
            "alignment_patterns": self.alignment_patterns,
            "timing_patterns": self.timing_patterns,
            "version_info": self.version_info,
            "format_info": self.format_info,
            "image_path": str(image_path),
        }

        if include_metadata and image_path.exists():
            stat = os.stat(image_path)
            csv_data.update({
                "file_size_bytes": stat.st_size,
                "created_timestamp": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        # Write to CSV
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = csv_path.exists()

        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(csv_data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(csv_data)

        logger.info(f"QR code metadata saved to {csv_path}")

    @classmethod
    def from_csv_row(cls, csv_row: dict) -> "QRCodeGenerator":
        """Create QRCodeGenerator from CSV row data.

        Args:
            csv_row (dict): Dictionary containing QR code parameters.

        Returns:
            QRCodeGenerator: Configured QR code generator.

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        # Map error correction string to int
        error_correction_map = {
            "L": ERROR_CORRECT_L,
            "M": ERROR_CORRECT_M,
            "Q": ERROR_CORRECT_Q,
            "H": ERROR_CORRECT_H,
        }

        required_fields = ["data", "version", "error_correction"]
        for field in required_fields:
            if field not in csv_row:
                raise ValueError(f"Required field '{field}' missing from CSV row")

        # Parse parameters with defaults
        params = {
            "data": csv_row["data"],
            "version": int(csv_row.get("version", 1)),
            "error_correction": error_correction_map.get(
                csv_row.get("error_correction", "M"), ERROR_CORRECT_M
            ),
            "box_size": int(csv_row.get("box_size", 10)),
            "border": int(csv_row.get("border", 4)),
            "fill_color": csv_row.get("fill_color", "black"),
            "back_color": csv_row.get("back_color", "white"),
            "image_format": csv_row.get("image_format", "PNG"),
            "finder_patterns": csv_row.get("finder_patterns", "True").lower() == "true",
            "alignment_patterns": csv_row.get("alignment_patterns", "True").lower() == "true",
            "timing_patterns": csv_row.get("timing_patterns", "True").lower() == "true",
            "version_info": csv_row.get("version_info", "True").lower() == "true",
            "format_info": csv_row.get("format_info", "True").lower() == "true",
        }

        return cls(**params)

    @classmethod
    def from_image(cls, image_path: Union[str, Path], **kwargs) -> "QRCodeGenerator":
        """Create QRCodeGenerator by decoding an existing QR code image.

        Args:
            image_path (Union[str, Path]): Path to QR code image to decode.
            **kwargs: Additional parameters to override (version, error_correction, etc.).

        Returns:
            QRCodeGenerator: QR code generator with decoded data.

        Raises:
            ValueError: If image cannot be decoded.
        """
        decoded_data = cls.decode_qr_code(image_path)
        if decoded_data is None:
            raise ValueError(f"Could not decode QR code from {image_path}")

        # Use default parameters, override with any provided kwargs
        default_params = {
            "data": decoded_data,
            "version": 1,  # Will auto-scale if needed
            "error_correction": ERROR_CORRECT_M,
            "box_size": 10,
            "border": 4,
            "fill_color": "black",
            "back_color": "white",
            "image_format": "PNG",
            "finder_patterns": True,
            "alignment_patterns": True,
            "timing_patterns": True,
            "version_info": True,
            "format_info": True,
        }
        default_params.update(kwargs)

        return cls(**default_params)

    @staticmethod
    def process_csv_batch(
        csv_input_path: Union[str, Path],
        output_dir: Union[str, Path] = "output",
        csv_output_path: Optional[Union[str, Path]] = None,
        image_prefix: str = "qr_",
    ) -> int:
        """Process a CSV file to batch generate QR codes.

        Args:
            csv_input_path (Union[str, Path]): Path to input CSV file.
            output_dir (Union[str, Path]): Directory to save generated QR codes.
            csv_output_path (Optional[Union[str, Path]]): Path to save metadata CSV.
            image_prefix (str): Prefix for generated image filenames.

        Returns:
            int: Number of QR codes successfully generated.

        Raises:
            ValueError: If CSV file cannot be read or processed.
        """
        import uuid

        csv_input_path = Path(csv_input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        successful_generations = 0

        try:
            with open(csv_input_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                    try:
                        # Create generator from CSV row
                        generator = QRCodeGenerator.from_csv_row(row)

                        # Generate unique filename
                        unique_id = str(uuid.uuid4())[:8]
                        image_filename = f"{image_prefix}{row_num}_{unique_id}.png"
                        image_path = output_dir / image_filename

                        # Save QR code and optionally CSV metadata
                        if csv_output_path:
                            generator.save_qr_code_with_csv(image_path, csv_output_path)
                        else:
                            generator.save_qr_code(image_path)

                        successful_generations += 1
                        logger.info(f"Generated QR code {row_num}: {image_path}")

                    except Exception as e:
                        logger.error(f"Failed to generate QR code for row {row_num}: {e}")
                        continue

        except Exception as e:
            raise ValueError(f"Failed to process CSV file {csv_input_path}: {e}")

        logger.info(f"Successfully generated {successful_generations} QR codes from {csv_input_path}")
        return successful_generations

    @staticmethod
    def regenerate_from_images(
        input_dir: Union[str, Path],
        output_dir: Union[str, Path] = "regenerated",
        **override_params
    ) -> int:
        """Regenerate QR codes from existing QR code images.

        Args:
            input_dir (Union[str, Path]): Directory containing QR code images.
            output_dir (Union[str, Path]): Directory to save regenerated QR codes.
            **override_params: Parameters to override in regenerated QR codes.

        Returns:
            int: Number of QR codes successfully regenerated.
        """
        import glob

        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        successful_regenerations = 0

        # Find all image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(str(input_dir / ext)))
            image_files.extend(glob.glob(str(input_dir / ext.upper())))

        for image_file in image_files:
            try:
                # Create generator from existing QR code
                generator = QRCodeGenerator.from_image(image_file, **override_params)

                # Generate new filename
                input_path = Path(image_file)
                output_filename = f"regenerated_{input_path.stem}.png"
                output_path = output_dir / output_filename

                # Save regenerated QR code
                generator.save_qr_code(output_path)

                successful_regenerations += 1
                logger.info(f"Regenerated QR code: {input_path} -> {output_path}")

            except Exception as e:
                logger.error(f"Failed to regenerate QR code from {image_file}: {e}")
                continue

        logger.info(f"Successfully regenerated {successful_regenerations} QR codes")
        return successful_regenerations

    @staticmethod
    def decode_qr_code(image_path: Union[str, Path]) -> Optional[str]:
        """Decode a QR code from an image file.

        Args:
            image_path (Union[str, Path]): Path to the QR code image file.

        Returns:
            Optional[str]: The decoded text if successful, None otherwise.

        Raises:
            ValueError: If the image cannot be read or decoded.
        """
        image_path = Path(image_path)

        try:
            logger.debug(f"Loading image from {image_path}")
            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Could not read image from {image_path}")

            # Preprocess image for better QR code detection
            # Convert to grayscale for better contrast analysis
            if len(img.shape) == 3:  # Color image
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:  # Already grayscale
                gray = img

            # Enhanced preprocessing for better QR code detection
            logger.debug(f"Image shape: {gray.shape}")

            # For very large images (version 20+), use specialized processing
            if gray.shape[0] > 1000 or gray.shape[1] > 1000:
                logger.debug(f"Large image detected ({gray.shape}), using enhanced processing")
                # For large images, use more sophisticated preprocessing

                # Step 1: Apply bilateral filtering to preserve edges while reducing noise
                blurred = cv2.bilateralFilter(gray, 9, 75, 75)

                # Step 2: Use adaptive thresholding with optimized parameters
                block_size = min(gray.shape[0], gray.shape[1]) // 8
                if block_size % 2 == 0:  # Must be odd
                    block_size += 1
                block_size = max(11, min(block_size, 51))  # Keep within reasonable bounds

                binary = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 2
                )

                # Step 3: Apply morphological operations to clean up
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                # Additional opening to remove small noise
                cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            else:
                # Standard preprocessing for smaller images
                # Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(gray, (3, 3), 0)

                # Use adaptive thresholding for better binary conversion
                binary = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )

                # Clean up the binary image with morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            logger.debug(f"Decoding QR code from preprocessed image (shape: {cleaned.shape})")

            # Use OpenCV's built-in QR code detector with enhanced parameters
            qr_detector = cv2.QRCodeDetector()

            # Try multiple decoding approaches with different preprocessing methods
            approaches = [
                ("cleaned_binary", cleaned),
                ("original_binary", binary),
                ("blurred_grayscale", blurred),
                ("original_grayscale", gray),
                ("original_color", img),
            ]

            # For large images, add Otsu thresholding as additional approach
            if gray.shape[0] > 1000 or gray.shape[1] > 1000:
                _, otsu_binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                approaches.insert(1, ("otsu_binary", otsu_binary))

            # Try inverted approaches for white-on-black QR codes
            inverted_approaches = []
            for name, img_data in approaches:
                if name in ["cleaned_binary", "original_grayscale", "original_color"]:
                    if name == "cleaned_binary":
                        inverted = cv2.bitwise_not(img_data)
                        inverted_approaches.append(("inverted_cleaned", inverted))
                    elif name == "original_grayscale":
                        inverted_gray = cv2.bitwise_not(img_data)
                        inverted_approaches.append(("inverted_grayscale", inverted_gray))
                    elif name == "original_color":
                        inverted_color = cv2.bitwise_not(img_data)
                        inverted_approaches.append(("inverted_color", inverted_color))

            all_approaches = approaches + inverted_approaches

            decoded_data = None
            for approach_name, processed_img in all_approaches:
                logger.debug(f"Trying {approach_name} approach")
                try:
                    decoded_data, points, _ = qr_detector.detectAndDecode(processed_img)
                    if decoded_data and len(decoded_data.strip()) > 0:
                        logger.debug(f"Successfully decoded using {approach_name} approach")
                        break
                except Exception as e:
                    logger.debug(f"Approach {approach_name} failed: {e}")
                    continue

            if not decoded_data or len(decoded_data.strip()) == 0:
                # Try pyzbar as a fallback if available
                if PYZBAR_AVAILABLE:
                    logger.debug("Trying pyzbar as fallback decoder")
                    try:
                        pyzbar_decode = _import_pyzbar()
                        pil_img = PILImage.open(image_path)
                        decoded_objects = pyzbar_decode(pil_img)
                        if decoded_objects:
                            decoded_data = decoded_objects[0].data.decode('utf-8')
                            logger.debug(f"Successfully decoded using pyzbar fallback")
                        else:
                            raise ValueError(f"Could not decode QR code from {image_path} using any approach")
                    except Exception as e:
                        logger.debug(f"Pyzbar fallback also failed: {e}")
                        raise ValueError(f"Could not decode QR code from {image_path} using any approach")
                else:
                    raise ValueError(f"Could not decode QR code from {image_path} using any approach")

            logger.info(f"QR code decoded successfully from {image_path}: '{decoded_data[:50]}...'")
            return decoded_data

        except Exception as e:
            logger.error(f"Error decoding QR code from {image_path}: {e}")
            raise ValueError(f"Failed to decode QR code from {image_path}.") from e

    @staticmethod
    def image_to_csv_matrix(image_path: Union[str, Path], csv_path: Union[str, Path]) -> None:
        """Convert QR code image to CSV matrix format with 1s and 0s.

        This method extracts the binary pattern from a QR code image and saves it
        as a CSV file where each cell represents a module (1 for black/dark, 0 for white/light).

        Args:
            image_path (Union[str, Path]): Path to the QR code image file.
            csv_path (Union[str, Path]): Path to save the CSV matrix file.

        Raises:
            ValueError: If the image cannot be processed or saved.
        """
        import csv
        import numpy as np

        image_path = Path(image_path)
        csv_path = Path(csv_path)

        try:
            logger.debug(f"Loading image from {image_path} for CSV conversion")

            # Load image with PIL for better compatibility
            pil_img = Image.open(image_path).convert('L')  # Convert to grayscale
            img_array = np.array(pil_img)

            # Threshold to get binary pattern (black=1, white=0)
            # Use a threshold that works well for QR codes (typically dark modules on light background)
            threshold = 128
            binary_matrix = (img_array < threshold).astype(int)

            # Find the QR code bounds by looking for the actual QR pattern
            # QR codes have finder patterns at corners, so we look for the border
            height, width = binary_matrix.shape

            # Find left edge of QR code (first column with many black pixels)
            left = 0
            for col in range(width):
                if np.sum(binary_matrix[:, col]) > height * 0.1:  # At least 10% black pixels
                    left = col
                    break

            # Find right edge of QR code (last column with many black pixels)
            right = width - 1
            for col in range(width - 1, -1, -1):
                if np.sum(binary_matrix[:, col]) > height * 0.1:
                    right = col
                    break

            # Find top edge of QR code (first row with many black pixels)
            top = 0
            for row in range(height):
                if np.sum(binary_matrix[row, :]) > width * 0.1:
                    top = row
                    break

            # Find bottom edge of QR code (last row with many black pixels)
            bottom = height - 1
            for row in range(height - 1, -1, -1):
                if np.sum(binary_matrix[row, :]) > width * 0.1:
                    bottom = row
                    break

            # Extract the QR code matrix (remove borders and get just the data area)
            # Add some padding to ensure we capture the full QR pattern
            padding = 2
            qr_matrix = binary_matrix[
                max(0, top - padding):min(height, bottom + padding + 1),
                max(0, left - padding):min(width, right + padding + 1)
            ]

            logger.debug(f"Extracted QR matrix shape: {qr_matrix.shape}")

            # Ensure the matrix is square (QR codes are square)
            min_dim = min(qr_matrix.shape)
            qr_matrix = qr_matrix[:min_dim, :min_dim]

            # Create CSV directory if it doesn't exist
            csv_path.parent.mkdir(parents=True, exist_ok=True)

            # Save matrix to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in qr_matrix:
                    writer.writerow(row.tolist())

            logger.info(f"QR code matrix saved to CSV: {csv_path} (shape: {qr_matrix.shape})")

        except Exception as e:
            logger.error(f"Error converting image to CSV matrix: {e}")
            raise ValueError(f"Failed to convert image {image_path} to CSV matrix.") from e

    @staticmethod
    def csv_matrix_to_image(csv_path: Union[str, Path], image_path: Union[str, Path], box_size: int = 1) -> None:
        """Convert CSV matrix format to QR code image.

        This method reads a CSV file containing a binary matrix (1s and 0s)
        and generates a QR code image from it.

        Args:
            csv_path (Union[str, Path]): Path to the CSV matrix file.
            image_path (Union[str, Path]): Path to save the QR code image.
            box_size (int): Size of each module in pixels (default: 1).

        Raises:
            ValueError: If the CSV cannot be read or the image cannot be generated.
        """
        import csv
        import numpy as np

        csv_path = Path(csv_path)
        image_path = Path(image_path)

        try:
            logger.debug(f"Loading CSV matrix from {csv_path} for image conversion")

            # Read CSV matrix
            matrix = []
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:  # Skip empty rows
                        matrix.append([int(cell) for cell in row])

            if not matrix:
                raise ValueError("CSV file is empty or contains no valid data")

            # Convert to numpy array
            qr_matrix = np.array(matrix, dtype=np.uint8)

            # Ensure matrix is square
            if qr_matrix.shape[0] != qr_matrix.shape[1]:
                logger.warning(f"Matrix is not square ({qr_matrix.shape}), using largest dimension")
                min_dim = min(qr_matrix.shape)
                qr_matrix = qr_matrix[:min_dim, :min_dim]

            # Create image from matrix
            height, width = qr_matrix.shape
            img_array = np.zeros((height * box_size, width * box_size), dtype=np.uint8)

            # Fill image array based on matrix values
            for i in range(height):
                for j in range(width):
                    if qr_matrix[i, j] == 1:  # Black/dark module
                        fill_value = 0  # Black
                    else:  # White/light module
                        fill_value = 255  # White

                    # Fill the corresponding block
                    img_array[i * box_size:(i + 1) * box_size,
                             j * box_size:(j + 1) * box_size] = fill_value

            # Create PIL image and save
            img = Image.fromarray(img_array, mode='L')

            # Create output directory if it doesn't exist
            image_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            img.save(image_path)
            logger.info(f"QR code image generated from CSV matrix: {image_path} (size: {img.size})")

        except Exception as e:
            logger.error(f"Error converting CSV matrix to image: {e}")
            raise ValueError(f"Failed to convert CSV matrix {csv_path} to image.") from e
