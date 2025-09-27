# QR Code Generator

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/test-pytest-green.svg)](https://pytest.org/)
[![ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-orange.svg)](https://github.com/features/actions)
[![Issues](https://img.shields.io/github/issues/SJTU-YONGFU-RESEARCH-GRP/qr-code-generator)](https://github.com/SJTU-YONGFU-RESEARCH-GRP/qr-code-generator/issues)
[![GitHub Stars](https://img.shields.io/github/stars/SJTU-YONGFU-RESEARCH-GRP/qr-code-generator?style=flat-square&logo=github&color=ffdd00&label=⭐%20Stars&v=1)](https://github.com/SJTU-YONGFU-RESEARCH-GRP/qr-code-generator/stargazers)

A Python CLI tool for generating QR codes from text data, URLs, or other information. This tool allows you to create customizable QR codes with various error correction levels, sizes, and colors.

## Table of Contents

* [Features](#features)
* [Quick Start](#quick-start)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Configuration](#configuration)
* [Testing](#testing)
* [Development](#development)
* [Error Handling](#error-handling)
* [Regression Testing](#regression-testing)
* [Troubleshooting](#troubleshooting)
* [License](#license)
* [Contributing](#contributing)

## Features

- 🚀 **Generate QR codes** from text, URLs, or any string data
- 📏 **Customizable versions** (1-40) for different sizes and capacities
- 🛡️ **Multiple error correction levels** (L, M, Q, H) for robustness
- 🎨 **Custom colors** and styling options
- 📷 **Multiple image formats** (PNG, JPEG, BMP) support
- 🔍 **QR decoding** functionality for verification
- 📊 **Comprehensive logging** and error handling
- 🧪 **Full test coverage** with pytest
- ⚡ **Fast processing** with PIL and qrcode libraries

## Quick Start

### Basic Usage

Generate a QR code for a URL:
```bash
python -m qr.main "https://example.com" -o qr_code.png
```

Generate a QR code for text with custom options:
```bash
python -m qr.main "Hello World" --version 5 --error-correction H --box-size 15 -o hello.png
```

### As a Library

```python
from qr.core.qr_generator import QRCodeGenerator

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

# Or decode a QR code
decoded_text = QRCodeGenerator.decode_qr_code("path/to/qr_image.png")
print(decoded_text)
```

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

#### Basic Usage

```bash
python -m qr.main [OPTIONS] DATA
```

#### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `data` | - | The data to encode (required) | - |
| `-o, --output` | `-o` | Output file path (required) | - |
| `-v, --version` | `-v` | QR code version (1-40) | 1 |
| `-e, --error-correction` | `-e` | Error correction level (L, M, Q, H) | M |
| `-b, --box-size` | `-b` | Size of each box in pixels | 10 |
| `-d, --border` | `-d` | Border width in boxes | 4 |
| `-f, --fill-color` | `-f` | Fill color for QR modules | black |
| `-k, --back-color` | `-k` | Background color | white |
| `-i, --image-format` | `-i` | Output image format (PNG, JPEG, BMP) | PNG |
| `--log-level` | - | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

#### Examples

1. **Simple QR code:**
   ```bash
   python -m qr.main "Visit our website" -o website.png
   ```

2. **High error correction for robust scanning:**
   ```bash
   python -m qr.main "https://example.com/very/long/url/with/many/parameters" --error-correction H -o robust.png
   ```

3. **Custom colors and size:**
   ```bash
   python -m qr.main "Contact us" --fill-color blue --back-color yellow --box-size 20 -o contact.png
   ```

4. **JPEG format:**
   ```bash
   python -m qr.main "Image data" -f JPEG --fill-color red -o image.jpg
   ```

### Using as a Library

#### Basic Library Usage

```python
from qr.core.qr_generator import QRCodeGenerator

# Create and save a QR code
generator = QRCodeGenerator(
    data="https://example.com",
    version=5,
    error_correction=QRCodeGenerator.ERROR_CORRECT_H,
)
generator.save_qr_code("output.png")
```

#### Advanced Configuration

```python
from qr.core.qr_generator import QRCodeGenerator

# Full configuration
generator = QRCodeGenerator(
    data="Hello, World!",
    version=10,
    error_correction=QRCodeGenerator.ERROR_CORRECT_Q,
    box_size=20,
    border=4,
    fill_color="#FF0000",
    back_color="#FFFFFF",
)

# Get PIL Image object
img = generator.get_qr_code_image()
img.show()

# Save with custom format
generator.save_qr_code("custom_qr.jpg", format="JPEG")
```

#### Decoding QR Codes

```python
from qr.core.qr_generator import QRCodeGenerator

# Decode from file
decoded_data = QRCodeGenerator.decode_qr_code("path/to/qr_code.png")
print(f"Decoded: {decoded_data}")

# Decode from PIL Image
from PIL import Image
img = Image.open("qr_code.png")
decoded_data = QRCodeGenerator.decode_qr_code(img)
print(f"Decoded: {decoded_data}")
```

## Project Structure

```
qr-code-generator/
├── qr/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── qr_generator.py     # Core QR generation logic
│   └── config/
│       ├── __init__.py
│       └── logging_config.py   # Logging setup
├── tests/
│   ├── __init__.py
│   └── test_core/
│       ├── __init__.py
│       └── test_qr_generator.py
├── docs/
│   ├── CONSTRAINTS.md          # Development constraints
│   └── QR.md                   # QR code documentation
├── outputs/                    # Generated QR code images
├── pyproject.toml
├── requirements.txt
├── run.sh                      # Regression testing script
├── README.md
└── venv/                       # Virtual environment (ignored)
```

## Configuration

### Core Configuration

- **Logging**: Configured via the `--log-level` option or by modifying `qr/config/logging_config.py`
- **Environment Variables**: Use `.env` files for sensitive configurations (via `python-dotenv`)

### QR Code Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| Version | 1-40 | QR code size and data capacity |
| Error Correction | L, M, Q, H | Recovery capability (7%, 15%, 25%, 30%) |
| Box Size | 1-100 | Pixel size of each QR module |
| Border | 0-100 | Border width in modules |
| Fill Color | Any color | QR code foreground color |
| Back Color | Any color | QR code background color |

## Example Output

### Generated QR Code

The tool generates QR codes as image files with customizable parameters:

```bash
# Generate a blue QR code on white background
python -m qr.main "Hello World" --fill-color "#0066CC" --back-color white -o blue_qr.png
```

### File Structure Example

```
outputs/
├── qr_test_1758959208_6.png    # Generated QR code
└── qr_test_1758959776_18.png   # Another test output
```

### Decoding Verification

The tool includes built-in QR code decoding for verification:

```python
from qr.core.qr_generator import QRCodeGenerator

# Generate and immediately decode for verification
generator = QRCodeGenerator(data="Test data")
generator.save_qr_code("test.png")
decoded = QRCodeGenerator.decode_qr_code("test.png")
assert decoded == "Test data"  # Verification
```

## Requirements

### Software Dependencies

* **Python 3.10+** with pip
* **PIL/Pillow** (included in qrcode[pil])
* **OpenCV** (for QR decoding)
* **pyzbar** (for QR decoding)

### Hardware Support

* Compatible with all platforms (Windows, macOS, Linux)
* No special hardware requirements
* Supports standard image formats (PNG, JPEG, BMP)

## Testing

Run the test suite using pytest:

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=qr
```

### Test Coverage

The tests cover:
- ✅ QR code generation with valid/invalid parameters
- ✅ Image saving and retrieval functionality
- ✅ Error handling for edge cases
- ✅ QR code decoding verification
- ✅ Command-line interface validation

## Development

### Code Quality

**Linting and Formatting:**
```bash
ruff check qr/
ruff format qr/
```

**Type Checking:**
```bash
mypy qr/
```

### Adding Features

1. Follow the constraints in `docs/CONSTRAINTS.md`
2. Add comprehensive unit tests for new functionality
3. Update documentation and docstrings
4. Ensure all code has proper type annotations
5. Test across different Python versions (3.10+)

### Building and Distribution

Build the package:
```bash
python -m build
```

Install locally for development:
```bash
pip install -e .
```

## Support

* 🐛 **Issues**: Use [GitHub Issues](https://github.com/your-username/qr-code-generator/issues) for bug reports
* 📖 **Documentation**: Check the `docs/` directory for detailed information
* 💬 **Discussions**: Use GitHub Discussions for questions and general discussion
* 📧 **Email**: Contact the maintainers for support

---

**Ready to generate QR codes?** Start with the Quick Start guide above! 🚀

```bash
pytest
```


## Error Handling

The tool includes comprehensive error handling:
- ✅ Invalid parameters (version out of range, invalid colors)
- ✅ Data overflow for QR code capacity limits
- ✅ File I/O errors and permission issues
- ✅ Image format compatibility problems
- ✅ Decoding failures with fallback mechanisms

Check the logs for detailed error messages and debugging information.

## Regression Testing

Use the `run.sh` script to perform comprehensive regression tests:

```bash
chmod +x run.sh
./run.sh
```

### What the script tests:

- ✅ Various QR code versions (1-40)
- ✅ All error correction levels (L, M, Q, H)
- ✅ Different box sizes and border configurations
- ✅ Multiple encoding modes and color schemes
- ✅ Random input texts for closed-loop verification
- ✅ Generation and decoding to ensure data integrity

**Note**: Ensure pyzbar and OpenCV are installed for full decoding support. Set `LOG_LEVEL=DEBUG` in run.sh for detailed logs.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **QR Code Too Large** | Increase version number or reduce error correction level |
| **Installation Issues** | Ensure Python 3.10+ and reinstall dependencies |
| **Permission Errors** | Check file permissions for output directory |
| **Memory Issues** | Reduce box size or version for large QR codes |
| **Decoding Issues** | Install OpenCV and pyzbar dependencies |
| **Color Format Errors** | Use valid color names or hex codes (#RRGGBB) |

### Getting Help

- Check the logs with `--log-level DEBUG` for detailed information
- Verify your Python version: `python --version`
- Test with minimal parameters first, then add complexity

## License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

### What this means:

* ✅ **Commercial Use**: You can use this project for commercial purposes
* ✅ **Modifications**: You can modify, adapt, and build upon this work
* ✅ **Distribution**: You can distribute your modified versions
* ✅ **Share Alike**: You may distribute, remix, adapt, and build upon the material for any purpose, even commercially
* 📋 **Attribution Required**: You must give appropriate credit to the original author(s) and provide a link to the license
* 🚫 **No Additional Restrictions**: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits

For the full license text, see the LICENSE file in this repository or visit [creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/).

## Contributing

We welcome contributions! Here's how to get started:

### Development Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Develop** your changes with proper tests
4. **Test** thoroughly: `pytest --cov=qr`
5. **Lint** your code: `ruff check qr/ && ruff format qr/`
6. **Commit** with clear messages
7. **Push** to your fork and create a **Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive unit tests for new features
- Update documentation and docstrings
- Ensure type annotations are complete
- Test across Python 3.10+ versions
- Keep commits focused and atomic

### Code of Conduct

This project follows a standard code of conduct. Be respectful, constructive, and collaborative.
