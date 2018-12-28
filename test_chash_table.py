from cht import HashTable
from ctypes import *

ht = None


def test_bucket_resize(ht):
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(100):
        ht[2] = {'data': 2}
    print(ht)

def test_with_vatying_data():
    ht = HashTable(c_wchar_p, {'data': c_int64})
    for i in range(100):
        ht['test' + str(i)] = {'data': i}
    print(ht)

def test_with_reads(ht):
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(100):
        ht[2] = {'data': 2}
        x = ht[2]

test_bucket_resize(ht)
test_with_vatying_data()
test_with_reads(ht)


