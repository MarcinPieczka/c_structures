"""
First make HT without resizing of buckets
"""
import ctypes as ct


class HashTable:

    def __init__(self, key_type, data_def, initial_buckets_count=1024):
        self.data_def = data_def
        self.key_type = key_type
        self.data_struct = type(
            'struct',
            (ct.Structure,),
            {'__fields__': (('cht_key_hash', ct.c_int64), ('cht_key', key_type)) + tuple(data_def.items())}
        )
        self.bucket_struct = type(
            'struct',
            (ct.Structure,),
            {'__fields__': (
                ('data_len', ct.c_uint16),
                ('array_size', ct.c_uint16),
                ('data', ct.POINTER((ct.POINTER(self.data_struct) * 1))())
            )}
        )
        self.bucket_count = ct.c_uint64(initial_buckets_count)
        self.len = ct.c_uint64(0)
        self.buckets = (ct.POINTER(self.bucket_struct) * self.bucket_count.value)()

    def __setitem__(self, key, values):
        key_hash = hash(key)
        d_struct = self.data_struct(
            cht_key_hash=ct.c_int64(key_hash),
            cht_key=self.key_type,
            **{k: self.data_def[k](v) for k, v in values.items()},
        )
        bucket_index = self._bucket_index(key_hash)
        if not self.buckets[bucket_index]:
            darray = (ct.POINTER(self.data_struct) * 1)()
            darray[0] = ct.pointer(d_struct)
            self.buckets[bucket_index] = self.bucket_struct(
                data_len=ct.c_uint16(1),
                array_size=ct.c_uint16(1),
                data=ct.pointer(darray),
            )
        else:
            old_size = self.buckets[bucket_index].array_size.value
            old_len = self.buckets[bucket_index].data_len.value
            ct.resize(self.buckets[bucket_index].data.contents, old_size + 1)
            self.buckets[bucket_index].data.contents[old_size] = ct.pointer(d_struct)
            self.buckets[bucket_index].array_size = ct.c_uint16(old_size + 1)
            self.buckets[bucket_index].data_len = ct.c_uint16(old_len + 1)

    def __getitem__(self, item):
        pass

    def _bucket_index(self, key_hash):
        return key_hash % self.bucket_count.value

    def __len__(self):
        return self.len.value
