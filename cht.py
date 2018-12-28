"""
First make HT without resizing of buckets
"""
import ctypes as ct


class HashTable:

    def __init__(self, key_type, data_def, initial_buckets_count=1024):
        class DataStruct(ct.Structure):
            _fields_ = [('cht_key_hash', ct.c_int64), ('cht_key', key_type)] + list(data_def.items())

        self.data_struct = DataStruct

        class BucketStruct(ct.Structure):
            _fields_ = [
                ('data_len', ct.c_uint16),
                ('array_size', ct.c_uint16),
                ('data', ct.POINTER(ct.POINTER(self.data_struct)))
            ]

        self.bucket_struct = BucketStruct

        self.data_def = data_def
        self.key_type = key_type
        self.bucket_count = ct.c_uint64(initial_buckets_count)
        self.len = ct.c_uint64(0)
        self.buckets = (ct.POINTER(self.bucket_struct) * self.bucket_count.value)()

    def __setitem__(self, key, values):
        key_hash = hash(key)
        d_struct = self.data_struct(
            cht_key_hash=ct.c_int64(key_hash),
            cht_key=self.key_type(key),
            **{k: self.data_def[k](v) for k, v in values.items()},
        )
        bucket_index = self._bucket_index(key_hash)
        if not self.buckets[bucket_index]:
            darray = (ct.POINTER(self.data_struct) * 1)()
            darray[0] = ct.pointer(d_struct)
            self.buckets[bucket_index] = ct.pointer(self.bucket_struct(
                data_len=ct.c_uint16(1),
                array_size=ct.c_uint16(1),
                data=ct.cast(darray, ct.POINTER(ct.POINTER(self.data_struct))),
            ))
        else:
            bucket = self.buckets[bucket_index].contents
            print(type(bucket))
            old_size = bucket.array_size
            old_len = bucket.data_len
            resized = (ct.POINTER(self.data_struct) * (old_size + 1))(*bucket.data.contents)
            bucket.data = ct.pointer(resized)
            bucket.data.contents[old_size] = ct.pointer(d_struct)
            bucket.array_size = ct.c_uint16(old_size + 1)
            bucket.data_len = ct.c_uint16(old_len + 1)

    def __getitem__(self, item):
        pass

    def _bucket_index(self, key_hash):
        return key_hash % self.bucket_count.value

    def __len__(self):
        return self.len.value
