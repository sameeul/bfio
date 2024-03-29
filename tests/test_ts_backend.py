from bfiocpp import TSTiffReader, Seq
import numpy as numpy
from time import time

FILE_PATH = "/mnt/hdd2/axle/data/bfio_test_images/r001_c001_z000.ome.tif"

# t1 = time()
# br = TSTiffReader(FILE_PATH)
# rows = Seq(0,1079,1)
# cols = Seq(0,1079,1)
# layers = Seq(0,0,1)
# channels = Seq(0,0,1)
# tsteps = Seq(0,0,1)
# t2 = time()
# tmp = br.data(rows, cols, layers, channels, tsteps)
# t3 = time()

# print(tmp.sum())
# print(tmp.shape)
# print(type(tmp))
# print(tmp.dtype)

# print(f"Time taken for init {(t2-t1)}")
# print(f"Time taken for read {(t3-t2)}")
from bfio import BioReader as BioReader
t4 = time()
br = BioReader(FILE_PATH, backend="python")
print(br._metadata)
t5 = time()
# tmp = br[:]
# t6 = time()
# # tmp = tmp2[0:1024, 0:1024]
# print(tmp.sum())
# print(tmp.shape)
# print(type(tmp))
# print(tmp.dtype)
# print(f"Time taken for init {(t5-t4)}")
# print(f"Time taken for read {(t6-t5)}")