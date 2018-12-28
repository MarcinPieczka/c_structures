import cProfile, pstats, io

from hash_table import HashTableCache

pr = cProfile.Profile()
pr.enable()

ht = HashTableCache({'height': 'h', 'width': 'h', 'sth': 'l', 'sth2': 'l'}, buckets=10**5, cache_limit=10**5)
for i in range(10**6):
    val = {'height': i % 999, 'width': i % 777, 'sth': i % 10**6 + 1, 'sth2': i % 10**6 + 1}
    ht['test' + str(i)] = val
    ht.get('test' + str(i))

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s)
ps.print_stats()
print(s.getvalue())