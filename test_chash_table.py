from cht import HashTable
from ctypes import *


def test_bucket_resize():
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(100):
        ht[2] = {'data': 2}
    print(ht)

def test_data_store_resize():
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(10000):
        ht[i] = {'data': i}
        ht.get(i - 10)
    print(ht)

def test_with_vatying_data():
    ht = HashTable(c_wchar_p, {'data': c_int64})
    for i in range(2000):
        ht['test' + str(i)] = {'data': i}
    print(ht)

def test_with_reads():
    ht = HashTable(c_int64, {'data': c_int64})
    for i in range(100):
        ht[2] = {'data': 2}
        x = ht[2]

test_bucket_resize()
test_data_store_resize()
test_with_vatying_data()
test_with_reads()


