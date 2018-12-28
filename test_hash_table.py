from hash_table import HashTableCache
from cht import HashTable
from time import time
import ctypes as c

backend = input('dict-dict: dd, dict-tuple dt, HashTable: ht, CHashTable ch\n')


if backend == 'ht':
    ht = HashTableCache({'height': 'h', 'width': 'h', 'sth': 'l', 'sth2': 'l'}, buckets=10**7, cache_limit=10**7)
if backend in ('dt', 'dd'):
    ht = dict()
if backend == 'ch':
    ht = HashTable(c.c_wchar_p, {'height': c.c_uint16, 'width': c.c_uint16, 'sth': c.c_int64, 'sth2': c.c_int64})
stats = {'min': 234., 'max': 0., 'sum': 0.}
for i in range(10**7):
    if i % 100000 == 0:
        stats['avg'] = stats['sum'] / 100000
        del stats['sum']
        print(f"len: {len(ht)/10**6:.5}M, min: {stats['min']:.5}us, "
              f"max: {stats['max']:.5}us, avg: {stats['avg']:.5}us")
        stats = {'min': 234, 'max': 0, 'sum': 0}
    start = time()
    val = {'height': i % 999, 'width': i % 777, 'sth': i % 10**6 + 1, 'sth2': i % 10**6 + 1}
    if backend in ('dd', 'ht', 'ch'):
        ht['test' + str(i)] = val
    if backend == 'dt':
        ht['test' + str(i)] = tuple(val.values())
    ht.get('test' + str(i))
    exec_time = (time() - start) * 10**6
    stats['min'] = min(stats['min'], exec_time)
    stats['max'] = max(stats['max'], exec_time)
    stats['sum'] += exec_time

input()
