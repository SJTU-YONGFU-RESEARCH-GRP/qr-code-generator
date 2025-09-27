#!/bin/bash

# QR Code Regression Test Script
# This script performs comprehensive testing of QR code generation and decoding
# to ensure features like dimensions, encoding, colors, etc. work correctly.

set -e  # Exit on any error

# Configuration
TEST_OUTPUT_DIR="outputs"
PYTHON_CMD="./venv/bin/python"  # Use virtual environment python
QR_GENERATOR_CMD="$PYTHON_CMD -m qr.main"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
LOG_LEVEL="INFO"  # Set to DEBUG for more details
GENERATE_CSV=false  # Set to true to generate CSV metadata during testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    local message="$2"
    if [ "$LOG_LEVEL" = "DEBUG" ] || [ "$level" != "DEBUG" ]; then
        echo -e "${BLUE}[$level]: $message${NC}"
    fi
}

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"
log "INFO" "Test output directory created at $TEST_OUTPUT_DIR"

# Function to generate random text
generate_random_text() {
    local length=$1
    # Generate random alphanumeric string
    $PYTHON_CMD -c "import random, string; print(''.join(random.choices(string.ascii_letters + string.digits, k=$length)))"
}

# Function to decode QR code from image
decode_qr() {
    local image_path="$1"
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
from qr.core.qr_generator import QRCodeGenerator
try:
    decoded = QRCodeGenerator.decode_qr_code('$image_path')
    print(decoded)
except ValueError as e:
    print('ERROR:', str(e))
"
}

# Function to run a single test
run_test() {
    local test_name="$1"
    local data="$2"
    local version="$3"
    local error_correction="$4"
    local box_size="$5"
    local border="$6"
    local fill_color="$7"
    local back_color="$8"
    local image_format="$9"
    local no_finder_patterns="${10:-false}"
    local no_alignment_patterns="${11:-false}"
    local no_timing_patterns="${12:-false}"
    local no_version_info="${13:-false}"
    local no_format_info="${14:-false}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log "INFO" "Starting test $TOTAL_TESTS: $test_name"
    log "DEBUG" "Test parameters: data='${data:0:50}...', version=$version, error_correction=$error_correction, box_size=$box_size, border=$border, fill_color=$fill_color, back_color=$back_color, format=$image_format, patterns: finder=${no_finder_patterns}, alignment=${no_alignment_patterns}, timing=${no_timing_patterns}, version=${no_version_info}, format=${no_format_info}"

    # Generate QR code
    local output_file="$TEST_OUTPUT_DIR/qr_test_$(date +%s)_$TOTAL_TESTS.png"
    local csv_file=""
    if [ "$GENERATE_CSV" = true ]; then
        csv_file="$TEST_OUTPUT_DIR/qr_metadata.csv"
    fi

    log "DEBUG" "Generating QR code to $output_file"
    start_time=$(date +%s.%N)

    # Use printf to safely escape the data and avoid eval issues with special characters
    printf -v safe_data '%q' "$data"

    local cmd="$QR_GENERATOR_CMD $safe_data -o \"$output_file\" \
        --version \"$version\" \
        --error-correction \"$error_correction\" \
        --box-size \"$box_size\" \
        --border \"$border\" \
        --fill-color \"$fill_color\" \
        --back-color \"$back_color\" \
        --image-format \"$image_format\""

    # Add pattern flags if specified
    if [ "$no_finder_patterns" = true ]; then
        cmd="$cmd --no-finder-patterns"
    fi
    if [ "$no_alignment_patterns" = true ]; then
        cmd="$cmd --no-alignment-patterns"
    fi
    if [ "$no_timing_patterns" = true ]; then
        cmd="$cmd --no-timing-patterns"
    fi
    if [ "$no_version_info" = true ]; then
        cmd="$cmd --no-version-info"
    fi
    if [ "$no_format_info" = true ]; then
        cmd="$cmd --no-format-info"
    fi

    if [ -n "$csv_file" ]; then
        cmd="$cmd --csv-output \"$csv_file\""
    fi

    eval "$cmd > /dev/null 2>&1"
    gen_exit_code=$?
    end_time=$(date +%s.%N)
    gen_duration=$(echo "$end_time - $start_time" | bc)

    if [ $gen_exit_code -ne 0 ]; then
        log "ERROR" "QR code generation failed for $test_name (exit code: $gen_exit_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    log "DEBUG" "QR code generated successfully in ${gen_duration}s"

    # Decode QR code
    log "DEBUG" "Decoding QR code from $output_file"
    start_time=$(date +%s.%N)
    decoded_data=$(decode_qr "$output_file")
    end_time=$(date +%s.%N)
    decode_duration=$(echo "$end_time - $start_time" | bc)
    log "DEBUG" "Decoding completed in ${decode_duration}s"

    # Special debugging for test 6 (Version 20)
    if [ "$test_name" = "Version 20" ]; then
        log "DEBUG" "VERSION 20 DEBUG: Original data length: ${#data}"
        log "DEBUG" "VERSION 20 DEBUG: Original data starts with: '${data:0:50}'"
        log "DEBUG" "VERSION 20 DEBUG: Decoded data length: ${#decoded_data}"
        log "DEBUG" "VERSION 20 DEBUG: Decoded data starts with: '${decoded_data:0:50}'"
        log "DEBUG" "VERSION 20 DEBUG: File exists: $(test -f "$output_file" && echo 'YES' || echo 'NO')"
        if [[ "$decoded_data" == "ERROR:"* ]]; then
            log "DEBUG" "VERSION 20 DEBUG: Keeping failed file for analysis: $output_file"
            # Don't clean up failed files for version 20 so we can analyze them
        fi
    fi

    # Check if this test expects decoding to fail (for pattern tests without essential elements)
    local expect_decode_failure=false
    if [ "$no_finder_patterns" = true ] || [ "$no_timing_patterns" = true ] || [ "$test_name" = "Minimal Patterns" ]; then
        expect_decode_failure=true
    fi

    if [[ "$decoded_data" == "ERROR:"* ]]; then
        if [ "$expect_decode_failure" = true ]; then
            log "INFO" "EXPECTED FAILURE: $test_name (QR code without essential patterns cannot be decoded)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log "ERROR" "QR code decoding failed for $test_name: $decoded_data"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        # Decoding succeeded - verify the data matches
        if [ "$decoded_data" = "$data" ]; then
            log "INFO" "PASSED: $test_name (decoded: '${decoded_data:0:50}...')"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log "ERROR" "FAILED: $test_name - Mismatch detected"
            log "ERROR" "Expected: '${data:0:50}...'"
            log "ERROR" "Got: '${decoded_data:0:50}...'"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi

    # Clean up (skip for failed version 20 tests for debugging)
    if [ "$test_name" = "Version 20" ] && [[ "$decoded_data" == "ERROR:"* ]]; then
        log "DEBUG" "Keeping failed Version 20 file for analysis: $output_file"
    else
        log "DEBUG" "Cleaning up $output_file"
        rm -f "$output_file"
    fi
}

# Test cases
echo "Starting QR Code Regression Tests..."

# Basic tests
run_test "Basic Text" "Hello World" 1 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "URL" "https://example.com" 1 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "Numeric" "123456789" 1 "M" 10 4 "black" "white" "PNG" false false false false false

# Version tests
run_test "Version 5" "$(generate_random_text 50)" 5 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "Version 10" "$(generate_random_text 100)" 10 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "Version 20" "$(generate_random_text 400)" 20 "H" 10 4 "black" "white" "PNG" false false false false false  # Use 400 characters for version 20 with high error correction
run_test "Version 39" "$(generate_random_text 1000)" 39 "H" 10 4 "black" "white" "PNG" false false false false false  # Use version 39 instead of 40 (OpenCV limitation)

# Error correction tests
run_test "Error Correction L" "$(generate_random_text 20)" 1 "L" 10 4 "black" "white" "PNG" false false false false false
run_test "Error Correction Q" "$(generate_random_text 20)" 1 "Q" 10 4 "black" "white" "PNG" false false false false false
run_test "Error Correction H" "$(generate_random_text 20)" 1 "H" 10 4 "black" "white" "PNG" false false false false false

# Box size and border tests
run_test "Small Box Size" "$(generate_random_text 20)" 1 "M" 5 4 "black" "white" "PNG" false false false false false
run_test "Large Box Size" "$(generate_random_text 20)" 1 "M" 20 4 "black" "white" "PNG" false false false false false
run_test "Small Border" "$(generate_random_text 20)" 1 "M" 10 1 "black" "white" "PNG" false false false false false
run_test "Large Border" "$(generate_random_text 20)" 1 "M" 10 8 "black" "white" "PNG" false false false false false

# Color tests
run_test "Blue Fill" "$(generate_random_text 20)" 1 "M" 10 4 "blue" "white" "PNG" false false false false false
run_test "Red Background" "$(generate_random_text 20)" 1 "M" 10 4 "black" "red" "PNG" false false false false false
run_test "Green Both" "$(generate_random_text 20)" 1 "M" 10 4 "green" "yellow" "PNG" false false false false false
run_test "White Fill Black Back" "$(generate_random_text 20)" 1 "M" 10 4 "white" "black" "PNG" false false false false false

# Image format tests
run_test "JPEG Format" "$(generate_random_text 20)" 1 "M" 10 4 "black" "white" "JPEG" false false false false false
run_test "BMP Format" "$(generate_random_text 20)" 1 "M" 10 4 "black" "white" "BMP" false false false false false

# Special character tests
run_test "Special Characters" "Hello!@#$%^&*()_+-=[]{}|;':\",./<>?" 1 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "Unicode" "Café naïve résumé" 1 "M" 10 4 "black" "white" "PNG" false false false false false
run_test "Emojis" "😀🚀🌟📱" 1 "M" 10 4 "black" "white" "PNG" false false false false false

# QR Code Pattern Tests
# Test different pattern combinations to verify functionality

# Test without finder patterns (should still be decodable with other patterns)
run_test "No Finder Patterns" "Pattern Test - No Finder" 1 "M" 10 4 "black" "white" "PNG" true false false false false

# Test without timing patterns
run_test "No Timing Patterns" "Pattern Test - No Timing" 1 "M" 10 4 "black" "white" "PNG" false false true false false

# Test without alignment patterns (version 1 doesn't have them anyway)
run_test "No Alignment Patterns V1" "Pattern Test - No Alignment V1" 1 "M" 10 4 "black" "white" "PNG" false true false false false

# Test without format info
run_test "No Format Info" "Pattern Test - No Format" 1 "M" 10 4 "black" "white" "PNG" false false false false true

# Test without version info (version 1 doesn't have it)
run_test "No Version Info V1" "Pattern Test - No Version V1" 1 "M" 10 4 "black" "white" "PNG" false false false true false

# Test version 7+ without version info (version 7 has version info)
run_test "No Version Info V7" "Pattern Test - No Version V7" 7 "M" 10 4 "black" "white" "PNG" false false false true false

# Test version 2+ without alignment patterns
run_test "No Alignment Patterns V2" "Pattern Test - No Alignment V2" 2 "M" 10 4 "black" "white" "PNG" false true false false false

# Test minimal patterns (only data, no structural patterns)
run_test "Minimal Patterns" "Pattern Test - Minimal" 1 "M" 10 4 "black" "white" "PNG" true true true true true

# Random text tests (multiple)
for i in {1..10}; do
    random_text=$(generate_random_text $((RANDOM % 200 + 10)))
    run_test "Random Test $i" "$random_text" 1 "M" 10 4 "black" "white" "PNG" false false false false false
done

# Long text test (already covered by Version 20 test above)

# Binary-like data
run_test "Binary Data" "$($PYTHON_CMD -c "import os; print(os.urandom(50).hex())")" 10 "H" 10 4 "black" "white" "PNG" false false false false false

# CSV Binary Matrix Conversion Tests
run_csv_conversion_test() {
    local test_name="$1"
    local data="$2"
    local version="$3"
    local error_correction="$4"
    local box_size="$5"
    local border="$6"
    local fill_color="$7"
    local back_color="$8"
    local image_format="$9"
    local no_finder_patterns="${10:-false}"
    local no_alignment_patterns="${11:-false}"
    local no_timing_patterns="${12:-false}"
    local no_version_info="${13:-false}"
    local no_format_info="${14:-false}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log "INFO" "Starting CSV conversion test $TOTAL_TESTS: $test_name"
    log "DEBUG" "Test parameters: data='${data:0:50}...', version=$version, error_correction=$error_correction, box_size=$box_size, border=$border, fill_color=$fill_color, back_color=$back_color, format=$image_format"

    # Generate QR code
    local qr_file="$TEST_OUTPUT_DIR/qr_test_$(date +%s)_$TOTAL_TESTS.png"
    local csv_file="$TEST_OUTPUT_DIR/qr_matrix_$(date +%s)_$TOTAL_TESTS.csv"
    local reconstructed_file="$TEST_OUTPUT_DIR/qr_reconstructed_$(date +%s)_$TOTAL_TESTS.png"

    log "DEBUG" "Generating QR code to $qr_file"
    start_time=$(date +%s.%N)

    # Use printf to safely escape the data and avoid eval issues with special characters
    printf -v safe_data '%q' "$data"

    local cmd="$QR_GENERATOR_CMD $safe_data -o \"$qr_file\" \
        --version \"$version\" \
        --error-correction \"$error_correction\" \
        --box-size \"$box_size\" \
        --border \"$border\" \
        --fill-color \"$fill_color\" \
        --back-color \"$back_color\" \
        --image-format \"$image_format\""

    # Add pattern flags if specified
    if [ "$no_finder_patterns" = true ]; then
        cmd="$cmd --no-finder-patterns"
    fi
    if [ "$no_alignment_patterns" = true ]; then
        cmd="$cmd --no-alignment-patterns"
    fi
    if [ "$no_timing_patterns" = true ]; then
        cmd="$cmd --no-timing-patterns"
    fi
    if [ "$no_version_info" = true ]; then
        cmd="$cmd --no-version-info"
    fi
    if [ "$no_format_info" = true ]; then
        cmd="$cmd --no-format-info"
    fi

    eval "$cmd > /dev/null 2>&1"
    gen_exit_code=$?
    end_time=$(date +%s.%N)
    gen_duration=$(echo "$end_time - $start_time" | bc)

    if [ $gen_exit_code -ne 0 ]; then
        log "ERROR" "QR code generation failed for $test_name (exit code: $gen_exit_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    log "DEBUG" "QR code generated successfully in ${gen_duration}s"

    # Convert QR code to CSV matrix
    log "DEBUG" "Converting QR code to CSV matrix: $csv_file"
    start_time=$(date +%s.%N)

    local csv_cmd="$QR_GENERATOR_CMD --image-to-csv \"$qr_file\" --csv-output \"$csv_file\""
    eval "$csv_cmd > /dev/null 2>&1"
    csv_exit_code=$?
    end_time=$(date +%s.%N)
    csv_duration=$(echo "$end_time - $start_time" | bc)

    if [ $csv_exit_code -ne 0 ]; then
        log "ERROR" "Image to CSV conversion failed for $test_name (exit code: $csv_exit_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi
    log "DEBUG" "Image to CSV conversion completed in ${csv_duration}s"

    # Verify CSV file was created and contains valid data
    if [ ! -f "$csv_file" ]; then
        log "ERROR" "CSV file was not created for $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi

    # Check CSV content (should contain only 0s and 1s)
    if ! $PYTHON_CMD -c "
import csv
with open('$csv_file', 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if any(cell not in ['0', '1'] for cell in row):
            print('ERROR: Invalid CSV content')
            exit(1)
print('CSV content is valid')
"; then
        log "ERROR" "CSV file contains invalid content for $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi

    # Convert CSV matrix back to QR code image
    log "DEBUG" "Converting CSV matrix back to QR code: $reconstructed_file"
    start_time=$(date +%s.%N)

    local reconstruct_cmd="$QR_GENERATOR_CMD --csv-to-image \"$csv_file\" --output \"$reconstructed_file\" --box-size 1"
    eval "$reconstruct_cmd > /dev/null 2>&1"
    reconstruct_exit_code=$?
    end_time=$(date +%s.%N)
    reconstruct_duration=$(echo "$end_time - $start_time" | bc)

    if [ $reconstruct_exit_code -ne 0 ]; then
        log "ERROR" "CSV to image conversion failed for $test_name (exit code: $reconstruct_exit_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi
    log "DEBUG" "CSV to image conversion completed in ${reconstruct_duration}s"

    # Verify reconstructed image was created
    if [ ! -f "$reconstructed_file" ]; then
        log "ERROR" "Reconstructed image was not created for $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi

    # Decode the reconstructed QR code to verify it matches original data
    log "DEBUG" "Decoding reconstructed QR code"
    start_time=$(date +%s.%N)
    decoded_data=$(decode_qr "$reconstructed_file")
    end_time=$(date +%s.%N)
    decode_duration=$(echo "$end_time - $start_time" | bc)
    log "DEBUG" "Decoding completed in ${decode_duration}s"

    if [[ "$decoded_data" == "ERROR:"* ]]; then
        log "ERROR" "Reconstructed QR code decoding failed for $test_name: $decoded_data"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        rm -f "$qr_file" "$csv_file" "$reconstructed_file"
        return 1
    fi

    # Verify the decoded data matches the original
    if [ "$decoded_data" = "$data" ]; then
        log "INFO" "PASSED: CSV conversion test $test_name (decoded: '${decoded_data:0:50}...')"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log "ERROR" "FAILED: CSV conversion test $test_name - Mismatch detected"
        log "ERROR" "Expected: '${data:0:50}...'"
        log "ERROR" "Got: '${decoded_data:0:50}...'"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Clean up files
    log "DEBUG" "Cleaning up test files"
    rm -f "$qr_file" "$csv_file" "$reconstructed_file"
}

# Now run the CSV conversion tests
run_csv_conversion_test "CSV Conversion Basic" "CSV Conversion Test Data" 1 "M" 10 4 "black" "white" "PNG" false false false false false
run_csv_conversion_test "CSV Conversion Colors" "Color Test Data" 1 "M" 10 4 "blue" "yellow" "PNG" false false false false false
run_csv_conversion_test "CSV Conversion Version 5" "$(generate_random_text 50)" 5 "Q" 10 4 "black" "white" "PNG" false false false false false
run_csv_conversion_test "CSV Conversion High Error Correction" "$(generate_random_text 30)" 1 "H" 10 4 "black" "white" "PNG" false false false false false
run_csv_conversion_test "CSV Conversion Unicode" "Unicode test: ñáéíóú" 1 "M" 10 4 "black" "white" "PNG" false false false false false

# Summary
echo ""
log "INFO" "Test execution completed"
echo "Test Summary:"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo -e "Success Rate: ${BLUE}$((PASSED_TESTS * 100 / TOTAL_TESTS))%${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    log "INFO" "All tests passed successfully!"
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    log "ERROR" "$FAILED_TESTS tests failed"
    echo -e "${RED}Some tests failed. Check the logs above for details.${NC}"
    exit 1
fi
