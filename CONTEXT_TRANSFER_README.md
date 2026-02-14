# Context Transfer Guide for New Machine

## Overview
This document helps restore the Claude Code session context on a new machine for the tensorstore zarr v3 support implementation.

## Branches Created

### 1. `feat/zarrv3-via-tensorstore` (Main Implementation Branch)
**Commit:** `cc683acf707578c4b491895a0c2b71be639f52fa`

Contains the actual implementation changes:
- ✅ Zarr v3 format detection in tensorstore backend
- ✅ Format-specific child enumeration (v2: filesystem, v3: native methods)
- ✅ NGFF 0.5 metadata parsing with v2 fallback
- ✅ Comprehensive test coverage

**Files modified:**
- `src/bfio/ts_backends.py` - Core implementation (114 lines changed)
- `tests/test_read.py` - Test coverage (54 lines added)

### 2. `context/tensorstore-v3-docs` (Documentation Branch)
**Commit:** `832737c8c88d5f96da252aa7649231c6455b1737`

Contains all Claude Code session documentation and context:

**Documentation files (753 lines total):**
- `TENSORSTORE_V3_IMPLEMENTATION.md` - Complete implementation guide
- `ZARR_V3_IMPLEMENTATION.md` - General zarr v3 details
- `ZARR_V3_COMPATIBILITY.md` - Compatibility notes
- `ZARR_V3_UNIT_TESTS.md` - Testing documentation

**Test utilities:**
- `test_tensorstore_v3.py` - Standalone verification script
- `demo_zarr_v2_with_v3.py` - Compatibility demo
- `zarr_v3_test.py` - Additional test utilities

## Setting Up on New Machine

### 1. Clone the repository
```bash
git clone <repo-url>
cd bfio
```

### 2. Checkout the implementation branch
```bash
git checkout feat/zarrv3-via-tensorstore
```

### 3. View the documentation (optional)
```bash
git checkout context/tensorstore-v3-docs
cat TENSORSTORE_V3_IMPLEMENTATION.md
```

### 4. Set up Python environment
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .
```

### 5. Run verification tests
```bash
# Quick verification
python test_tensorstore_v3.py <path-to-v3-zarr-file>

# Full test suite
python -m unittest tests.test_read.TestZarrTSReader.test_read_zarr_v3 -v
```

## Key Implementation Details

### Format Detection Strategy
```python
zarr_format = detect_zarr_format(path)
if zarr_format == 3:
    file_type = FileType.OmeZarrV3  # Uses "zarr3" tensorstore driver
else:
    file_type = FileType.OmeZarrV2  # Uses "zarr" tensorstore driver
```

### Child Enumeration
- **v2 stores:** Use `_list_zarr_children()` filesystem fallback
  - Reason: `array_keys()`/`group_keys()` unreliable in zarr-python v3
- **v3 stores:** Use native `root.array_keys()` / `root.group_keys()`
  - Reason: Reliable for v3, no filesystem access needed

### Metadata Locations
- **v2 (NGFF 0.4):** `attrs["multiscales"][0]["axes"]`
- **v3 (NGFF 0.5):** `attrs["ome"]["multiscales"][0]["axes"]`
- Implementation tries v3 location first, falls back to v2

## Test Coverage

### Unit Tests Added
1. `TestZarrTSReader.test_read_zarr_v3()` - Basic v3 reading
2. `TestZarrTSReader.test_read_zarr_v3_multi_resolution()` - Multi-resolution support
3. `TestZarrReader.test_read_zarr_v3()` - Regular zarr backend compatibility

### Test Dataset
- **ExpD_chicken_embryo_MIP.ome.zarr** (NGFF 0.5/v3 format)
  - URL: https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr
  - Dimensions: 8978 x 6510 x 1 x 1
  - Multi-resolution levels: 6

## Architecture Decisions

### Why Different Enumeration Methods?
The zarr-python v3 library has **inconsistent behavior** with v2 stores:
- `array_keys()`/`group_keys()` work reliably for v3 stores
- Same methods are **unreliable** for v2 stores
- Solution: Format-specific enumeration strategy

### Backward Compatibility
- ✅ All v2 zarr files work as before
- ✅ Writer defaults to v2 format
- ✅ No breaking changes to existing API
- ✅ Automatic format detection transparent to users

## Next Steps (if continuing development)

1. **Add v3 writer support:**
   - Add `zarr_version` parameter to BioWriter
   - Update `write_metadata()` to write NGFF 0.5 format

2. **Performance optimization:**
   - Benchmark v2 vs v3 read/write speeds
   - Optimize child enumeration for large stores

3. **Enhanced testing:**
   - Add stress tests with large multi-resolution pyramids
   - Test edge cases (empty groups, missing metadata)

## Troubleshooting

### If tests fail
1. Check zarr version: `pip show zarr` (should be >= 3.0)
2. Verify bfiocpp supports v3: Check for `FileType.OmeZarrV3` enum
3. Check test data downloaded: ExpD_chicken_embryo_MIP.ome.zarr

### Common issues
- **"FileType.OmeZarrV3 not found"**: Update bfiocpp to latest version
- **"list index out of range"**: v3 child enumeration failing, check `_get_zarr_children()`
- **Metadata location errors**: Check both v2 and v3 metadata locations

## Claude Code Memory

The Claude Code memory system has been updated with:
- Zarr v3 API differences in zarr-python v3
- `_list_zarr_children()` fallback rationale
- Format detection strategy
- Key architecture files

See: `/home/samee/.claude/projects/-usr-axle-dev-bfio/memory/MEMORY.md`

## Contact & Attribution

Implementation by: Claude Sonnet 4.5 (Anthropic)
Session Date: February 13-14, 2026
Branch: feat/zarrv3-via-tensorstore
