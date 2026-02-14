# Zarr v3 Unit Tests - Test Report

## Test Suite Overview

Created comprehensive unit tests in `tests/test_zarr_v3.py` to verify Zarr v2 and v3 compatibility in bfio.

## Test Coverage

### Test Classes and Methods

1. **TestZarrVersionDetection** (3 tests)
   - `test_zarr_version_detection` - Verify zarr version can be detected
   - `test_zarr_type_checking` - Verify appropriate types are available
   - `test_bfio_import` - Verify bfio imports correctly with current zarr version

2. **TestZarrBasicOperations** (3 tests)
   - `test_create_zarr_group` - Test creating zarr groups
   - `test_create_zarr_array` - Test creating zarr arrays with version-specific syntax
   - `test_read_zarr_group` - Test reading zarr groups

3. **TestZarrWriterV3** (4 tests)
   - `test_write_zarr_basic` - Test basic zarr writing
   - `test_write_zarr_with_metadata` - Test writing with custom metadata
   - `test_write_zarr_structure` - Verify written zarr structure
   - `test_write_zarr_large_tiles` - Test writing data larger than tile size (2048x2048)

4. **TestZarrReaderV3** (6 tests)
   - `test_read_zarr_basic` - Test basic zarr reading
   - `test_read_zarr_full_data` - Test reading complete data with integrity verification
   - `test_read_zarr_partial` - Test partial data reading
   - `test_read_zarr_metadata` - Test metadata reading
   - `test_read_zarr_dimensions` - Test dimension attributes (X, Y, Z, C, T)
   - `test_read_zarr_random_access` - Test random access pattern reading (5 random chunks)

5. **TestZarrRoundTrip** (4 tests)
   - `test_roundtrip_uint8` - Write-read roundtrip with uint8 data
   - `test_roundtrip_uint16` - Write-read roundtrip with uint16 data
   - `test_roundtrip_float32` - Write-read roundtrip with float32 data
   - `test_roundtrip_multichannel` - Write-read with multi-channel data (Z=5, C=3)

6. **TestZarrEdgeCases** (6 tests)
   - `test_write_read_exact_tile_size` - Test data exactly matching tile size (1024x1024)
   - `test_write_read_unaligned_boundaries` - Test unaligned data (1500x1300)
   - `test_write_read_small_image` - Test small 10x10 data
   - `test_partial_read_across_tiles` - Test reading regions spanning multiple tiles
   - `test_write_read_all_zeros` - Test highly compressible data (all zeros)
   - `test_write_read_max_values` - Test maximum dtype values (65535 for uint16)

7. **TestZarrVersionSpecific** (3 tests)
   - `test_zarr_version_string` - Verify zarr version information
   - `test_compression_works` - Test compression functionality
   - `test_consolidated_metadata` - Test consolidated metadata creation

8. **TestZarrIntegration** (4 tests)
   - `test_write_verify_structure_read` - Complete workflow test
   - `test_multiple_partial_writes` - Test writing in multiple chunks (4 quadrants)
   - `test_metadata_preservation_roundtrip` - Test metadata preservation
   - `test_read_after_direct_zarr_write` - Test bfio reading data written with zarr API

9. **TestZarrPerformance** (3 tests)
   - `test_many_channels` - Test 10 channels
   - `test_many_z_slices` - Test 20 z-slices
   - `test_sequential_reads` - Test 10 sequential read operations

**Total: 36 tests**

## Test Results

### Zarr v3.1.5
```
Ran 36 tests in 5.364s
OK - All tests passed ✓
```

### Zarr v2.18.7
```
Ran 36 tests in 1.778s
OK - All tests passed ✓
```

## Test Features

### Data Types Tested
- uint8
- uint16
- float32

### Data Dimensions Tested
- 2D: (128, 128, 1, 1, 1)
- Standard: (256, 256, 3, 2, 1)
- Large: (2048, 2048, 1, 1, 1)
- Multi-channel: (256, 256, 5, 3, 1)

### Operations Tested
- ✓ Version detection
- ✓ Group/Array creation
- ✓ Full data writing
- ✓ Full data reading
- ✓ Partial data reading
- ✓ Random access reading
- ✓ Metadata handling
- ✓ Compression
- ✓ Multi-channel support
- ✓ Multiple data types
- ✓ Large tile handling
- ✓ Consolidated metadata (v2)

## Known Warnings (Expected)

### Zarr v3
1. **OME metadata warning**: "Object at OME is not recognized as a component of a Zarr hierarchy"
   - Expected: OME metadata is stored in a separate directory
   
2. **Consolidated metadata warning**: "Consolidated metadata is currently not part in the Zarr format 3 specification"
   - Expected: Zarr v3 spec is still evolving

## Running the Tests

### Run all tests:
```bash
python -m unittest tests.test_zarr_v3 -v
```

### Run specific test class:
```bash
python -m unittest tests.test_zarr_v3.TestZarrReaderV3 -v
```

### Run specific test:
```bash
python -m unittest tests.test_zarr_v3.TestZarrReaderV3.test_read_zarr_full_data -v
```

## Test Data Management

- Tests create temporary directory: `tests/data_zarr_v3/`
- Automatically cleaned up after test suite completes
- Each test class manages its own test files
- No persistent test data required

## Compatibility Verification

The test suite verifies:
- ✓ Version detection works correctly
- ✓ API differences are handled transparently
- ✓ Data integrity is maintained across versions
- ✓ Metadata is preserved correctly
- ✓ Compression works in both versions
- ✓ All read/write operations function identically

## Conclusion

All 23 unit tests pass successfully with both Zarr v2.18.7 and v3.1.5, confirming that the bfio implementation correctly supports both versions with full backward compatibility.
