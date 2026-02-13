# -*- coding: utf-8 -*-
"""Tests for zarr v3 support in bfio using unittest."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy

from bfio.utils import detect_zarr_format


class TestZarrFormatDetection(unittest.TestCase):
    """Test detect_zarr_format() utility."""

    def test_detect_v2_format_zgroup(self):
        """Detect zarr v2 format via .zgroup marker."""
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "test.zarr"
            store.mkdir()
            (store / ".zgroup").write_text('{"zarr_format": 2}')
            self.assertEqual(detect_zarr_format(store), 2)

    def test_detect_v2_format_zarray(self):
        """Detect zarr v2 format via .zarray marker."""
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "test.zarr"
            store.mkdir()
            (store / ".zarray").write_text('{"zarr_format": 2}')
            self.assertEqual(detect_zarr_format(store), 2)

    def test_detect_v3_format(self):
        """Detect zarr v3 format via zarr.json marker."""
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "test.zarr"
            store.mkdir()
            with open(store / "zarr.json", "w") as f:
                json.dump({"zarr_format": 3, "node_type": "group"}, f)
            self.assertEqual(detect_zarr_format(store), 3)

    def test_detect_v3_format_in_subdir(self):
        """Detect zarr v3 format via zarr.json in a subdirectory."""
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "test.zarr"
            store.mkdir()
            subdir = store / "0"
            subdir.mkdir()
            with open(subdir / "zarr.json", "w") as f:
                json.dump({"zarr_format": 3, "node_type": "array"}, f)
            self.assertEqual(detect_zarr_format(store), 3)

    def test_detect_empty_dir(self):
        """Return 0 for empty directory."""
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "test.zarr"
            store.mkdir()
            self.assertEqual(detect_zarr_format(store), 0)

    def test_detect_nonexistent(self):
        """Return 0 for nonexistent path."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(detect_zarr_format(Path(tmp) / "nonexistent"), 0)


class TestZarr3Writer(unittest.TestCase):
    """Test Zarr3Writer creates v3 format stores."""

    def test_write_v3_creates_zarr_json(self):
        """Verify v3 writer creates zarr.json marker files."""
        from bfio import BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr3", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            self.assertTrue((out_path / "zarr.json").exists())
            with open(out_path / "zarr.json") as f:
                meta = json.load(f)
            self.assertEqual(meta.get("zarr_format"), 3)

    def test_write_v3_ome_metadata(self):
        """Verify v3 writer creates OME metadata."""
        from bfio import BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr3", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            metadata_path = out_path / "OME" / "METADATA.ome.xml"
            self.assertTrue(metadata_path.exists())

    def test_write_v3_multiscales_under_ome_key(self):
        """Verify v3 writer stores multiscales under 'ome' key per NGFF 0.5."""
        from bfio import BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr3", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            with open(out_path / "zarr.json") as f:
                meta = json.load(f)
            attrs = meta.get("attributes", {})
            self.assertIn("ome", attrs)
            self.assertIn("multiscales", attrs["ome"])
            self.assertEqual(attrs["ome"]["version"], "0.5")
            axes = attrs["ome"]["multiscales"][0]["axes"]
            axis_names = [a["name"] for a in axes]
            self.assertEqual(axis_names, ["t", "c", "z", "y", "x"])


class TestZarr3Reader(unittest.TestCase):
    """Test Zarr3Reader reads v3 format stores."""

    def test_read_v3_data(self):
        """Write v3 then read back, verify data integrity."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr3", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            br = BioReader(out_path, backend="zarr3")
            read_data = br[:128, :128]
            br.close()

            numpy.testing.assert_array_equal(data, read_data)

    def test_read_v3_dimensions(self):
        """Verify dimensions are correctly read from v3 store."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output.zarr"
            bw = BioWriter(
                out_path,
                backend="zarr3",
                X=256,
                Y=128,
                Z=2,
                C=3,
                T=1,
                dtype=numpy.uint16,
            )
            data = numpy.zeros((128, 256, 2, 3, 1), dtype=numpy.uint16)
            bw.write(data)
            bw.close()

            br = BioReader(out_path, backend="zarr3")
            self.assertEqual(br.X, 256)
            self.assertEqual(br.Y, 128)
            self.assertEqual(br.Z, 2)
            self.assertEqual(br.C, 3)
            self.assertEqual(br.T, 1)
            br.close()

    def test_read_v3_axis_info_from_ome_key(self):
        """Verify Zarr3Reader reads axis info from ome.multiscales per NGFF 0.5."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "axis_test.zarr"
            bw = BioWriter(
                out_path,
                backend="zarr3",
                X=64,
                Y=64,
                Z=2,
                C=3,
                T=1,
                dtype=numpy.uint8,
            )
            data = numpy.zeros((64, 64, 2, 3, 1), dtype=numpy.uint8)
            bw.write(data)
            bw.close()

            # Verify the zarr.json has ome.multiscales with axes
            with open(out_path / "zarr.json") as f:
                meta = json.load(f)
            axes = meta["attributes"]["ome"]["multiscales"][0]["axes"]
            axis_names = [a["name"] for a in axes]
            self.assertEqual(axis_names, ["t", "c", "z", "y", "x"])

            # Verify reader correctly parses dimensions from ome key
            br = BioReader(out_path, backend="zarr3")
            self.assertEqual(br.Z, 2)
            self.assertEqual(br.C, 3)
            self.assertEqual(br.T, 1)
            br.close()


class TestZarrAutoBackendSelection(unittest.TestCase):
    """Test auto-detection picks correct backend."""

    def test_auto_detect_v2(self):
        """Verify auto-detect picks 'zarr' for v2 format."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output_v2.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            br = BioReader(out_path)
            self.assertEqual(br._backend_name, "zarr")
            br.close()

    def test_auto_detect_v3(self):
        """Verify auto-detect picks 'zarr3' for v3 format."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "output_v3.zarr"
            data = numpy.random.randint(0, 255, (128, 128), dtype=numpy.uint8)

            bw = BioWriter(out_path, backend="zarr3", X=128, Y=128, dtype=numpy.uint8)
            bw[:128, :128, 0, 0, 0] = data
            bw.close()

            br = BioReader(out_path)
            self.assertEqual(br._backend_name, "zarr3")
            br.close()


class TestZarrRoundTrip(unittest.TestCase):
    """Test write-read roundtrip for both v2 and v3 formats."""

    def test_roundtrip_v2(self):
        """Write and read back data with zarr v2, verify integrity."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "roundtrip_zarr.zarr"
            data = numpy.random.randint(0, 65535, (64, 64), dtype=numpy.uint16)

            bw = BioWriter(out_path, backend="zarr", X=64, Y=64, dtype=numpy.uint16)
            bw[:64, :64, 0, 0, 0] = data
            bw.close()

            br = BioReader(out_path, backend="zarr")
            read_data = br[:64, :64]
            br.close()

            numpy.testing.assert_array_equal(data, read_data)

    def test_roundtrip_v3(self):
        """Write and read back data with zarr v3, verify integrity."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "roundtrip_zarr3.zarr"
            data = numpy.random.randint(0, 65535, (64, 64), dtype=numpy.uint16)

            bw = BioWriter(out_path, backend="zarr3", X=64, Y=64, dtype=numpy.uint16)
            bw[:64, :64, 0, 0, 0] = data
            bw.close()

            br = BioReader(out_path, backend="zarr3")
            read_data = br[:64, :64]
            br.close()

            numpy.testing.assert_array_equal(data, read_data)


class TestImageSizeV3(unittest.TestCase):
    """Test BioReader.image_size() works with both v2 and v3 format."""

    def test_image_size_v3(self):
        """Verify image_size() reads dimensions from v3 store."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "size_test.zarr"
            bw = BioWriter(out_path, backend="zarr3", X=256, Y=128, dtype=numpy.uint8)
            data = numpy.zeros((128, 256, 1, 1, 1), dtype=numpy.uint8)
            bw.write(data)
            bw.close()

            width, height = BioReader.image_size(out_path)
            self.assertEqual(width, 256)
            self.assertEqual(height, 128)

    def test_image_size_v2(self):
        """Verify image_size() still works with v2 stores."""
        from bfio import BioReader, BioWriter

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "size_test_v2.zarr"
            bw = BioWriter(out_path, backend="zarr", X=256, Y=128, dtype=numpy.uint8)
            data = numpy.zeros((128, 256, 1, 1, 1), dtype=numpy.uint8)
            bw.write(data)
            bw.close()

            width, height = BioReader.image_size(out_path)
            self.assertEqual(width, 256)
            self.assertEqual(height, 128)


if __name__ == "__main__":
    unittest.main()
