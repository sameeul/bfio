# Tensorstore Backend Zarr v3 Support - Implementation Summary

## Overview

Added Zarr v3 format support to the Tensorstore backend (`ts_backends.py`). The backend now automatically detects whether a zarr store is v2 or v3 format and passes the appropriate `FileType` to the underlying bfiocpp TSReader/TSWriter.

## Key Changes

### 1. Import `detect_zarr_format` utility
**File:** `ts_backends.py:16`

Added import for the existing `detect_zarr_format()` utility from `bfio.utils`.

### 2. Format Detection in `TensorstoreReader.__init__()`
**File:** `ts_backends.py:57-63`

After calling `get_zarr_array_info()`, detect the zarr format and set `_file_type`:
- `FileType.OmeZarrV3` for zarr v3 stores
- `FileType.OmeZarrV2` for zarr v2 stores (or unknown)

This file type is then passed to the bfiocpp `TSReader`, which uses the appropriate tensorstore driver ("zarr3" for v3, "zarr" for v2).

### 3. Child Enumeration Methods
**File:** `ts_backends.py:73-122`

Added proper zarr child enumeration based on format:

#### `_list_zarr_children()` (lines 73-90)
- **Purpose:** Filesystem-based fallback for v2 stores ONLY
- **Reason:** In zarr-python v3, `array_keys()`/`group_keys()` are unreliable for v2 stores
- **Implementation:** Checks for `.zarray` or `.zgroup` marker files in subdirectories

#### `_get_zarr_children()` (lines 92-122)
- **Purpose:** Unified interface that chooses the right enumeration method
- **For v3 stores:** Uses `root.array_keys()` / `root.group_keys()` (reliable in zarr-python v3)
- **For v2 stores:** Uses `_list_zarr_children()` filesystem fallback

### 4. Updated `get_zarr_array_info()`
**File:** `ts_backends.py:124-235`

**Changes:**
1. Detect zarr format at the beginning (line 137-138)
2. Replace all `_list_zarr_children()` calls with `_get_zarr_children()` and pass `is_v3` flag
3. Updated metadata parsing to check both v3 location (`attrs["ome"]["multiscales"]`) and v2 location (`attrs["multiscales"]`)

### 5. Updated `read_metadata()`
**File:** `ts_backends.py:247-250`

Added `FileType.OmeZarrV3` to the condition so both v2 and v3 use `read_zarr_metadata()`.

### 6. Writer Support
**File:** `ts_backends.py:380-392`

Added `file_type` parameter to `TSWriter` initialization, defaulting to `FileType.OmeZarrV2` for backward compatibility.

**Note:** Currently always writes v2 format. Future enhancement could add a `zarr_version` parameter to BioWriter.

## Architecture

### Why Different Enumeration Methods?

The implementation uses different methods to enumerate zarr children based on format:

```
Zarr v2 stores:
  └─> _list_zarr_children() [filesystem fallback]
      └─> Checks for .zarray/.zgroup markers
      └─> Reason: array_keys()/group_keys() unreliable in zarr-python v3

Zarr v3 stores:
  └─> root.array_keys() / root.group_keys()
      └─> Native zarr-python methods
      └─> Reason: Reliable for v3 stores, no filesystem access needed
```

### Metadata Location Differences

**Zarr v2 (NGFF 0.4 and earlier):**
```json
{
  "multiscales": [{
    "axes": [...],
    "datasets": [...]
  }]
}
```

**Zarr v3 (NGFF 0.5):**
```json
{
  "ome": {
    "version": "0.5",
    "multiscales": [{
      "axes": [...],
      "datasets": [...]
    }]
  }
}
```

The code tries v3 location first, then falls back to v2 location for compatibility.

## Testing

### Test Results

✓ v3 zarr stores (ExpA_VIP_ASLM_on.zarr, ExpD_chicken_embryo_MIP.ome.zarr)
  - Correctly detected as v3
  - FileType.OmeZarrV3 set
  - Successfully read data

✓ v2 zarr stores (test_zarr.ome.zarr, test_images/5025551.zarr)
  - Correctly detected as v2
  - FileType.OmeZarrV2 set
  - Successfully read data (backward compatible)

### Test Script

`test_tensorstore_v3.py` - Simple test script to verify:
- Format detection works
- Reading v2 and v3 stores with tensorstore backend
- Correct FileType is set

## Backward Compatibility

✓ **Fully backward compatible** - All existing v2 zarr files work as before
✓ **Auto-detection** - No user code changes needed
✓ **Writing** - Defaults to v2 format (existing behavior)

## Future Enhancements

1. **Writer v3 support:** Add option to write v3 format zarr stores (requires `zarr_version` parameter in BioWriter)
2. **NGFF 0.5 metadata:** Update writer to optionally write NGFF 0.5 compliant metadata for v3 stores

## References

- bfiocpp already supports v3 via `FileType.OmeZarrV3` enum
- C++ utilities.cpp uses "zarr3" tensorstore driver for v3 format
- NGFF 0.5 spec: https://ngff.openmicroscopy.org/0.5/
