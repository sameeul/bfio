#!/usr/bin/env python3
"""
Test script to verify Tensorstore backend correctly handles zarr v2 and v3 formats.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bfio import BioReader
from bfio.utils import detect_zarr_format

def test_zarr_detection():
    """Test that zarr format detection works correctly."""
    print("=" * 60)
    print("Testing zarr format detection")
    print("=" * 60)

    # Find test zarr files
    test_files = list(Path(".").glob("**/*.zarr"))

    if not test_files:
        print("No .zarr test files found in current directory")
        return

    for zarr_file in test_files:
        if zarr_file.is_dir():
            format_version = detect_zarr_format(zarr_file)
            print(f"\n{zarr_file}:")
            print(f"  Detected format: v{format_version if format_version else 'unknown'}")

    print("\n")

def test_tensorstore_reader(zarr_path):
    """Test reading a zarr file with tensorstore backend."""
    print("=" * 60)
    print(f"Testing TensorstoreReader with: {zarr_path}")
    print("=" * 60)

    zarr_path = Path(zarr_path)
    if not zarr_path.exists():
        print(f"Error: {zarr_path} does not exist")
        return False

    format_version = detect_zarr_format(zarr_path)
    print(f"Detected zarr format: v{format_version if format_version else 'unknown'}")

    try:
        # Open with tensorstore backend
        print(f"\nOpening with tensorstore backend...")
        br = BioReader(str(zarr_path), backend="tensorstore")

        print(f"Successfully opened!")
        print(f"Dimensions: X={br.X}, Y={br.Y}, Z={br.Z}, C={br.C}, T={br.T}")
        print(f"Data type: {br.dtype}")
        print(f"File type: {br._backend._file_type}")

        # Try reading a small tile
        if br.X >= 100 and br.Y >= 100:
            print(f"\nReading 100x100 tile...")
            data = br[:100, :100, 0, 0, 0]
            print(f"Successfully read data with shape: {data.shape}")

        br.close()
        print(f"\n✓ Test passed for {zarr_path}")
        return True

    except Exception as e:
        print(f"\n✗ Test failed for {zarr_path}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # First, detect all zarr formats in current directory
    test_zarr_detection()

    # Test with command line argument if provided
    if len(sys.argv) > 1:
        zarr_path = sys.argv[1]
        test_tensorstore_reader(zarr_path)
    else:
        print("Usage: python test_tensorstore_v3.py <path_to_zarr_file>")
        print("\nTo test a specific zarr file, provide the path as an argument.")
        print("Example: python test_tensorstore_v3.py test.zarr")
