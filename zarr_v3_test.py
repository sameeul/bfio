# -*- coding: utf-8 -*-
import requests, pathlib, shutil, logging, sys
import bfio
import numpy as np
import pickle
import random
import tifffile
from PIL import Image
import zarr
from ome_zarr.utils import download as zarr_download

TEST_IMAGES = {
    "5025551.zarr": "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0054A/5025551.zarr",
    "Plate1-Blue-A-12-Scene-3-P3-F2-03.czi": "https://downloads.openmicroscopy.org/images/Zeiss-CZI/idr0011/Plate1-Blue-A_TS-Stinger/Plate1-Blue-A-12-Scene-3-P3-F2-03.czi",
    "0.tif": "https://osf.io/j6aer/download",
    "img_r001_c001.ome.tif": "https://github.com/usnistgov/WIPP/raw/master/data/PyramidBuilding/inputCollection/img_r001_c001.ome.tif",
    "Leica-1.scn": "https://downloads.openmicroscopy.org/images/Leica-SCN/openslide/Leica-1/Leica-1.scn",
    # "76-45.ome.zarr": "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0010/76-45.ome.zarr",
    "ExpD_chicken_embryo_MIP.ome.zarr": "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr"
}

# 
# TEST_DIR = pathlib.Path(__file__).parent.joinpath("test_images")
# """Download images for testing"""
# TEST_DIR.mkdir(exist_ok=True)

# for file, url in TEST_IMAGES.items():

#     if not file.endswith(".zarr"):
#         if TEST_DIR.joinpath(file).exists():
#             continue

#         r = requests.get(url)

#         with open(TEST_DIR.joinpath(file), "wb") as fw:
#             fw.write(r.content)
#     else:
#         if TEST_DIR.joinpath(file).exists():
#             shutil.rmtree(TEST_DIR.joinpath(file))
#         zarr_download(url, str(TEST_DIR))

# """Load the czi image, and save as a npy file for further testing."""
# with bfio.BioReader(
#     TEST_DIR.joinpath("Plate1-Blue-A-12-Scene-3-P3-F2-03.czi")
# ) as br:
#     np.save(TEST_DIR.joinpath("4d_array.npy"), br[:])
#     zf = zarr.open(
#         str(TEST_DIR.joinpath("4d_array.zarr")),
#         mode="w",
#         shape=(1, br.C, br.Z, br.Y, br.X),
#         dtype=br.dtype,
#         chunks=(1, 1, 1, 1024, 1024),
#         zarr_format=2,
#     )
#     for t in range(1):
#         for c in range(br.C):
#             for z in range(br.Z):
#                 zf[t, c, z, :, :] = br[:, :, z, c, t]

# # create a 2D numpy array filled with random integer form 0-255
# img_height = 8000
# img_width = 7500
# source_data = np.random.randint(0, 256, (img_height, img_width), dtype=np.uint16)
# np.save(TEST_DIR.joinpath("random_image.npy"), source_data)
# with bfio.BioWriter(
#     str(TEST_DIR.joinpath("random_image.ome.tiff")),
#     X=img_width,
#     Y=img_height,
#     dtype=np.uint16,
# ) as bw:
#     bw[0:img_height, 0:img_width, 0, 0, 0] = source_data

test_files = [
    "5025551.zarr",
    "ExpD_chicken_embryo_MIP.ome.zarr",
]

for file in test_files:
    with bfio.BioReader(
        pathlib.Path(__file__).parent.joinpath("test_images", file)
    ) as br:
        print(f"Image shape: {br.shape}")
        print(f"Image dtype: {br.dtype}")
        print(f"Image metadata: {br.metadata}")
        data = br[:]
        print(f"sum: {data.sum()}")