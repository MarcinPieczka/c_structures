"""
First make HT without resizing of buckets
"""
import ctypes as ct
import pudb


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
        self.len = ct.c_uint64(self.len.value + 1)
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
            #pudb.set_trace()
            bucket = self.buckets[bucket_index].contents
            old_size = bucket.array_size
            old_len = bucket.data_len
            resized = (ct.POINTER(self.data_struct) * (old_size + 1))(bucket.data.contents)
            resized[old_len] = ct.pointer(d_struct)
            for p in resized:
                if p:
                    print(self._getdict(p.contents))
            bucket.data = ct.pointer(ct.cast(resized, ct.POINTER(self.data_struct)))
            bucket.array_size = ct.c_uint16(old_size + 1)
            bucket.data_len = ct.c_uint16(old_len + 1)

    def __getitem__(self, key):
        #pudb.set_trace()
        bucket_index = self._bucket_index(hash(key))
        bucket = self.buckets[bucket_index]
        if not bucket:
            raise KeyError()
        data = bucket.contents.data.contents
        for i in range(bucket.contents.data_len):
            data = bucket.contents.data.contents[i * ct.sizeof(self.data_struct)]
            if data.cht_key == key:
                return self._getdict(data)
            else:
                print(data.cht_key)
        raise KeyError()  # change so that error wil show the key

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _bucket_index(self, key_hash):
        return key_hash % self.bucket_count.value

    def _getdict(self, struct):
        return dict((field, getattr(struct, field)) for field, _ in struct._fields_)

    def __len__(self):
        return self.len.value
