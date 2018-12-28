from array import array


class HashTableCache:

    def __init__(self, data_types, buckets, cache_limit, data_shrink_factor=1.2):
        self.data_types = data_types
        self.data_shrink_factor = data_shrink_factor
        self.buckets = [tuple()] * buckets
        self.limit = cache_limit
        self.data = {name: array(t) for name, t in data_types.items()}
        self.keys = []
        self.data_offset = 0

    def __setitem__(self, key, values):
        cdef long key_hash
        key_hash = hash(key)
        self.keys.append(key)
        for k, v in values.items():
            self.data[k].append(v)
        self._append_data_index_to_bucket(key_hash)
        self._remove_data_over_cache_limit()

    def __getitem__(self, key):
        cdef long key_hash, bucket_index
        key_hash = hash(key)
        bucket_index = key_hash % len(self.buckets)
        if not self.buckets[bucket_index]:
            raise KeyError(key)
        self._clean_bucket(bucket_index)
        for i in reversed(self.buckets[bucket_index]):
            if self.keys[i - self.data_offset] == key:
                return {k: v[i - self.data_offset] for k, v in self.data.items()}
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _append_data_index_to_bucket(self, long key_hash):
        bucket_index = key_hash % len(self.buckets)
        self._clean_bucket(bucket_index)
        last_data_index = self.data_offset + len(self.keys) - 1
        self.buckets[bucket_index] = self.buckets[bucket_index] + (last_data_index,)

    def _remove_data_over_cache_limit(self):
        if len(self.keys) / self.limit > self.data_shrink_factor:
            self.data_offset += len(self.keys) - self.limit
            for name, data_array in self.data.items():
                self.data[name] = self.data[name][-self.limit:]
            del self.keys[:-self.limit]

    def _clean_bucket(self, long bucket_index):
        if self.buckets[bucket_index]:
            i = None
            for i, v in enumerate(self.buckets[bucket_index]):
                if v - self.data_offset >= 0:
                    break
            if i:
                self.buckets[bucket_index] = self.buckets[bucket_index][i:]

    def __len__(self):
        return len(self.keys)


