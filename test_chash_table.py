from cht import HashTable
from ctypes import *


def test_bucket_resize():
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(100):
        ht[2] = {'data': 2}

def test_

test_bucket_resize()


