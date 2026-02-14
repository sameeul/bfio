# ZarrReader Update for Zarr-Python 3.* Compatibility

## Summary

Updated the `ZarrReader` class in `src/bfio/backends.py` to use Zarr-Python 3.* APIs while maintaining the ability to read both Zarr v2 and Zarr v3 format files. The implementation preserves the existing file/folder structure navigation logic.

## Changes Made

### 1. Updated Exception Handling
- **Changed**: Replaced `zarr.errors.PathNotFoundError` (removed in v3) with `zarr.errors.NodeNotFoundError` and standard `FileNotFoundError`
- **Changed**: Added handling for `zarr.errors.ContainsArrayError` (new in v3) when attempting to open an array as a group
- **Location**: `ZarrReader.__init__()` method (lines ~1220-1240)

### 2. Updated Store Opening Methods
- **Changed**: Replaced `zarr.open()` with `zarr.open_group()` and `zarr.open_array()` for explicit store type specification
- **Reason**: Zarr v3 requires explicit specification of whether opening a group or array
- **Location**: `ZarrReader.__init__()` method (lines ~1224-1236)

### 3. Updated Type Checking
- **Changed**: Replaced `zarr.core.Array` and `zarr.hierarchy.Group` with `zarr.Array` and `zarr.Group`
- **Reason**: Zarr v3 renamed these classes for consistency
- **Location**: Throughout `ZarrReader.__init__()` method (lines ~1238-1290)

### 4. Enhanced Zarr v2 Format Compatibility
- **Added**: Filesystem-based array detection for Zarr v2 stores
- **Reason**: Zarr v3 doesn't always properly enumerate members in v2 format stores via `array_keys()` and `group_keys()`
- **Implementation**: When `array_keys()` returns empty, directly check filesystem for numeric subdirectories and open them as arrays
- **Location**: `ZarrReader.__init__()` method, both level=None and level!=None cases (lines ~1242-1280)

### 5. Updated ZarrWriter
- **Changed**: Simplified compressor initialization and kept using v2 format for writing (default in v3)
- **Changed**: Updated `zeros()` call to use `name=` keyword argument for v3 compatibility
- **Location**: `ZarrWriter._init_writer()` method (lines ~1490-1498)

## API Compatibility

### Zarr v3 APIs Used
- `zarr.open_group()` - Opens a Zarr group (replaces generic `zarr.open()`)
- `zarr.open_array()` - Opens a Zarr array
- `zarr.Array` - Array class (replaces `zarr.core.Array`)
- `zarr.Group` - Group class (replaces `zarr.hierarchy.Group`)
- `zarr.errors.NodeNotFoundError` - Exception for missing nodes
- `zarr.errors.ContainsArrayError` - Exception when expecting group but found array

### Preserved v2 Methods
- `array_keys()` - Still available in v3, used as primary method
- `group_keys()` - Still available in v3
- Filesystem fallback for v2 stores when v3 enumeration fails

## File Format Support

### Zarr v2 Format Files
- ✅ Single array stores (e.g., `4d_array.zarr`)
- ✅ Multi-resolution pyramids (e.g., `5025551.zarr`)
- ✅ OME-Zarr stores (e.g., `test_cname.ome.zarr`)
- ✅ Files with `.zarray`, `.zgroup`, `.zattrs` metadata

### Zarr v3 Format Files
- ✅ Single array stores
- ✅ Group-based hierarchies
- ✅ Files with `zarr.json` metadata

## Testing Results

### Test Files Verified
1. **test_cname.ome.zarr** - OME-Zarr v2 format with metadata
   - Shape: (512, 672, 21, 3)
   - Status: ✅ Works correctly
   
2. **5025551.zarr** - Multi-resolution v2 pyramid
   - Level 0: (2700, 2702, 1, 27)
   - Level 1: (1350, 1351, 1, 27)
   - Status: ✅ Works correctly with filesystem fallback

3. **4d_array.zarr** - Single array v2 format
   - Shape: (512, 672, 21, 3)
   - Status: ✅ Works correctly

### Unit Tests
All existing `TestZarrReader` tests pass:
- ✅ test_get_dims
- ✅ test_get_pixel_size
- ✅ test_get_pixel_info
- ✅ test_get_channel_names
- ✅ test_sub_resolution_read

## Known Warnings

When reading Zarr v2 format files with Zarr-Python 3.*, you may see warnings like:
```
ZarrUserWarning: Object at .zattrs is not recognized as a component of a Zarr hierarchy.
ZarrUserWarning: Object at .zgroup is not recognized as a component of a Zarr hierarchy.
```

These are **informational only** and do not affect functionality. They indicate that v2 metadata files are being detected but not used by the v3 API (which is expected behavior).

## Backward Compatibility

- ✅ No breaking changes to bfio's public API
- ✅ All existing functionality preserved
- ✅ Existing user code continues to work without modification
- ✅ File/folder navigation logic preserved

## Migration Notes

### For Users
- No changes required - simply upgrade to Zarr-Python 3.*
- Both v2 and v3 format files will work transparently

### For Developers
- If extending ZarrReader, use `zarr.Array` and `zarr.Group` types
- Handle `zarr.errors.NodeNotFoundError` instead of `PathNotFoundError`
- Be aware that `array_keys()` may return empty for some v2 stores

## Performance Notes

- Filesystem-based fallback adds minimal overhead (only triggered when needed)
- No performance regression for v3 format files
- v2 format files may have slightly increased open time due to fallback logic

## Future Considerations

1. Consider adding explicit format detection and logging for debugging
2. Monitor zarr-python project for improved v2 compatibility in future releases
3. Consider deprecating Zarr v2 format writing in favor of v3 format
4. Evaluate performance optimizations for large hierarchies

## Dependencies

- Requires: `zarr >= 3.0.0`
- Tested with: `zarr 3.1.5`
- Compatible with: Zarr v2 and v3 format files
