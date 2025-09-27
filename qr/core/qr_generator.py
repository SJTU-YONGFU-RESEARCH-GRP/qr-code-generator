"""QR Code Generator Module.

This module provides functionality to generate QR codes from input data.
"""

import logging
from pathlib import Path
from typing import Optional, Union

import cv2
import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """A class for generating QR codes with customizable options.

    This class handles the creation of QR codes from text data, supporting
    various error correction levels, box sizes, and output formats.

    Attributes:
        data (str): The data to encode in the QR code.
        version (int): The QR code version (1-40).
        error_correction (qrcode.constants.ERROR_CORRECT): Error correction level.
        box_size (int): Size of each box in pixels.
        border (int): Border width in boxes.
        fill_color (str): Color for the QR code modules.
        back_color (str): Background color.
        image_format (str): Output image format (e.g., 'PNG', 'JPEG').
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
    ) -> None:
        """Initialize the QR Code Generator.

        Args:
            data (str): The data to encode in the QR code.
            version (int): QR code version (1-40, default: 1).
            error_correction (int): Error correction level (0=L, 1=M, 2=Q, 3=H, default: 1).
            box_size (int): Size of each box in pixels (default: 10).
            border (int): Border width in boxes (default: 4).
            fill_color (str): Color for QR modules (default: "black").
            back_color (str): Background color (default: "white").
            image_format (str): Output image format (default: "PNG").

        Raises:
            ValueError: If version is not between 1 and 40, or if box_size/border are non-positive.
        """
        if not (1 <= version <= 40):
            raise ValueError("Version must be between 1 and 40.")
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

        logger.info(
            f"QRCodeGenerator initialized for data: '{data[:50]}...' with version {version}, "
            f"error correction {['L', 'M', 'Q', 'H'][error_correction]}, box_size {box_size}, border {border}, "
            f"fill_color {fill_color}, back_color {back_color}, format {image_format}."
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
            logger.debug(f"Creating image with fill_color={self.fill_color}, back_color={self.back_color}")
            img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
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
            logger.debug(f"Creating image object with fill_color={self.fill_color}, back_color={self.back_color}")
            img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
            logger.info(f"QR code image generated successfully (size: {img.size}).")
            return img
        except Exception as e:
            logger.error(f"Error generating QR code image: {e}")
            raise ValueError("Failed to generate QR code image.") from e

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

            # Enhance contrast and clean up the image
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Use adaptive thresholding for better binary conversion
            # This works better than simple Otsu for QR codes with varying lighting
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Clean up the binary image with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            logger.debug(f"Decoding QR code from preprocessed image (shape: {cleaned.shape})")

            # Use OpenCV's built-in QR code detector
            qr_detector = cv2.QRCodeDetector()

            # Try different preprocessing approaches for better detection
            decoded_data, _, _ = qr_detector.detectAndDecode(cleaned)

            if not decoded_data:
                # Try with processed binary
                decoded_data, _, _ = qr_detector.detectAndDecode(binary)

            if not decoded_data:
                # Try with blurred grayscale
                decoded_data, _, _ = qr_detector.detectAndDecode(blurred)

            if not decoded_data:
                # Try with original grayscale
                decoded_data, _, _ = qr_detector.detectAndDecode(gray)

            if not decoded_data:
                # Try with original color image as last resort
                decoded_data, _, _ = qr_detector.detectAndDecode(img)

            if not decoded_data:
                raise ValueError(f"Could not decode QR code from {image_path}")

            logger.info(f"QR code decoded successfully from {image_path}: '{decoded_data[:50]}...'")
            return decoded_data

        except Exception as e:
            logger.error(f"Error decoding QR code from {image_path}: {e}")
            raise ValueError(f"Failed to decode QR code from {image_path}.") from e
