# QR Code Generator

A Python CLI tool for generating QR codes from text data, URLs, or other information. This tool allows you to create customizable QR codes with various error correction levels, sizes, and colors.

## Features

- Generate QR codes from text, URLs, or any string data
- Customizable QR code versions (1-40)
- Multiple error correction levels (L, M, Q, H)
- Adjustable box size and border width
- Support for different image formats (PNG, JPEG, BMP)
- Custom fill and background colors
- Comprehensive logging and error handling
- Full test coverage with pytest

## Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd qr-code-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

The tool provides a command-line interface for easy QR code generation.

#### Basic Usage

Generate a QR code for a URL:
```bash
python -m src.main "https://example.com" -o qr_code.png
```

Generate a QR code for text with custom options:
```bash
python -m src.main "Hello World" --version 5 --error-correction H --box-size 15 -o hello.png
```

#### Command Line Options

- `data`: The data to encode (required)
- `-o, --output`: Output file path (required)
- `-v, --version`: QR code version (1-40, default: 1)
- `-e, --error-correction`: Error correction level (L, M, Q, H, default: M)
- `-b, --box-size`: Size of each box in pixels (default: 10)
- `-d, --border`: Border width in boxes (default: 4)
- `-f, --fill-color`: Fill color for QR modules (default: black)
- `-k, --back-color`: Background color (default: white)
- `-i, --image-format`: Output image format (PNG, JPEG, BMP, default: PNG)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, default: INFO)

#### Examples

1. Simple QR code:
   ```bash
   python -m src.main "Visit our website" -o website.png
   ```

2. High error correction for a complex URL:
   ```bash
   python -m src.main "https://example.com/very/long/url/with/many/parameters" --error-correction H -o robust.png
   ```

3. Custom colors and size:
   ```bash
   python -m src.main "Contact us" --fill-color blue --back-color yellow --box-size 20 -o contact.png
   ```

4. JPEG format:
   ```bash
   python -m src.main "Image data" -f JPEG --fill-color red -o image.jpg
   ```

### Using as a Library

You can also use the QRCodeGenerator class directly in your Python code:

```python
from src.core.qr_generator import QRCodeGenerator

# Create generator
generator = QRCodeGenerator(
    data="https://example.com",
    version=5,
    error_correction=QRCodeGenerator.ERROR_CORRECT_H,
    box_size=15,
    border=4,
    fill_color="black",
    back_color="white",
)

# Save to file
generator.save_qr_code("output.png")

# Or get as PIL Image
img = generator.get_qr_code_image()
img.show()

# Decode a QR code from an image file
decoded_text = QRCodeGenerator.decode_qr_code("path/to/qr_image.png")
print(decoded_text)
```

## Project Structure

```
qr-code-generator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── qr_generator.py     # Core QR generation logic
│   ├── utils/                  # Utility functions (if needed)
│   ├── config/
│   │   ├── __init__.py
│   │   └── logging_config.py   # Logging setup
│   └── models/                 # Data models (if needed)
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   │   ├── __init__.py
│   │   └── test_qr_generator.py
│   └── test_utils/             # Additional tests
├── docs/
│   ├── CONSTRAINTS.md          # Development constraints
│   └── QR.md                   # QR code documentation
├── requirements.txt
├── pyproject.toml
├── README.md
└── venv/                       # Virtual environment
```

## Configuration

- **Logging**: Configured via the `--log-level` option or by modifying `qr/config/logging_config.py`. Enhanced logging provides detailed information about QR code generation, decoding, and test execution.
- **Environment Variables**: Use `.env` files for sensitive configurations if needed (e.g., via `python-dotenv`).

## Testing

Run the test suite using pytest:

```bash
pytest
```

Or with coverage:
```bash
pytest --cov=src
```

The tests cover:
- Initialization with valid/invalid parameters
- QR code generation
- Image saving and retrieval
- Error handling

## Development

### Code Quality

- **Linting**: Use `ruff` for code formatting and linting.
  ```bash
  ruff check src/
  ruff format src/
  ```

- **Type Checking**: Use `mypy` for static type checking.
  ```bash
  mypy src/
  ```

### Adding Features

1. Follow the constraints in `docs/CONSTRAINTS.md`.
2. Add unit tests for new functionality.
3. Update documentation as needed.
4. Ensure all code has type annotations and Google-style docstrings.

### Building and Distribution

To build the package:
```bash
python -m build
```

## Error Handling

The tool includes comprehensive error handling:
- Invalid parameters (e.g., version out of range)
- Data overflow for QR code capacity
- File I/O errors
- Unexpected exceptions

Check the logs for detailed error messages.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Regression Testing

Use the `run.sh` script to perform comprehensive regression tests:

```bash
chmod +x run.sh
./run.sh
```

The script tests:
- Various QR code versions, error correction levels, and dimensions
- Different encoding modes and colors
- Random input texts for closed-loop verification
- Generation and decoding to ensure data integrity

**Note**: The QR generator now includes decoding functionality with enhanced logging. Ensure pyzbar and OpenCV are installed for full decoding support. Set LOG_LEVEL=DEBUG in run.sh for detailed logs.

## Troubleshooting

- **QR Code Too Large**: Increase the version number or reduce error correction level.
- **Installation Issues**: Ensure Python 3.10+ and try reinstalling dependencies.
- **Permission Errors**: Check file permissions for output directory.
- **Memory Issues**: For very large QR codes, consider reducing box size or version.
- **Decoding Issues**: Install OpenCV and ensure pyzbar dependencies are met for full decoding support.
