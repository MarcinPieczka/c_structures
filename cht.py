"""
First make HT without resizing of buckets
"""
import ctypes as ct
from pprint import pformat

import pudb


class HashTable:

    def __init__(self, key_type, data_def):
        class DataStruct(ct.Structure):
            _fields_ = [('cht_key_hash', ct.c_int64), ('cht_key', key_type)] + list(data_def.items())

        self.data_struct = DataStruct

        class BucketStruct(ct.Structure):
            _fields_ = [
                ('data_len', ct.c_uint16),
                ('array_size', ct.c_uint16),
                ('indexes', ct.POINTER(ct.c_uint64))
            ]

        self.bucket_struct = BucketStruct

        self.data_def = data_def
        self.key_type = key_type
        self.data_slots = 16
        self.len = 0
        self.data = (self.data_struct * self.data_slots)()
        self.buckets = (self.bucket_struct * self.data_slots)()

    def __setitem__(self, key, values):
        if key == '-test1024':
            pudb.set_trace()
        key_hash = hash(key)
        bucket_index = self._bucket_index(key_hash)
        bucket = self.buckets[bucket_index]

        data_struct = self.data_struct(
            cht_key_hash=ct.c_int64(key_hash),
            cht_key=self.key_type(key),
            **{k: self.data_def[k](v) for k, v in values.items()},
        )

        if bucket.indexes:
            for i in range(bucket.data_len):
                data_index = bucket.indexes[i]
                if self.data[data_index].cht_key == key:
                    self.data[data_index] = data_struct
                    return

        self.data[self.len] = data_struct
        self._insert_index_into_bucket_(bucket_index, self.len)
        self.len += 1
        if self.len >= self.data_slots:
            self._resize_data_structures_()

    def __getitem__(self, key):
        bucket_index = self._bucket_index(hash(key))
        bucket = self.buckets[bucket_index]
        if bucket:
            for i in range(bucket.data_len):
                data_index = bucket.indexes[i]
                if self.data[data_index].cht_key == key:
                    return self._getdict(self.data[data_index])
        raise KeyError()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _insert_index_into_bucket_(self, bucket_index, data_index):
        data_index = ct.c_uint64(data_index)
        bucket = self.buckets[bucket_index]
        if not bucket.indexes:
            self.buckets[bucket_index] = self.bucket_struct(
                data_len=ct.c_uint16(1),
                array_size=ct.c_uint16(1),
                indexes=ct.pointer(data_index),
            )
        else:
            array_size = bucket.array_size
            data_len = bucket.data_len
            if data_len == array_size:
                bucket.indexes = self._resize_p_array(
                    ct.c_uint64,
                    array_size + 1,
                    bucket.indexes,
                    array_size
                )
                bucket.array_size = ct.c_uint16(array_size + 1)
            bucket.indexes[data_len] = data_index
            bucket.data_len = ct.c_uint16(data_len + 1)

    def _resize_data_structures_(self):
        old_data_size = self.data_slots
        self.data_slots *= 2
        self._resize_data_array()
        self._resize_buckets(old_data_size)

    def _resize_data_array(self):
        self.data = self._resize_array(
            self.data_struct,
            self.data_slots,
            self.data
        )

    def _resize_buckets(self, old_buckets_count):
        self.buckets = self._resize_array(self.bucket_struct, self.data_slots, self.buckets)
        for b in reversed(range(old_buckets_count)):
            indexes = self.buckets[b].indexes
            if indexes:
                old_indexes = self._resize_p_array(
                    ct.c_uint64,
                    self.buckets[b].data_len,
                    indexes,
                    self.buckets[b].data_len
                )
                self.buckets[b].indexes = ct.POINTER(ct.c_uint64)()
                for i in range(self.buckets[b].data_len):
                    data_index = old_indexes[i]
                    key_hash = self.data[data_index].cht_key_hash
                    bucket_index = self._bucket_index(key_hash)
                    self._insert_index_into_bucket_(bucket_index, data_index)

    @staticmethod
    def _resize_p_array(structure, length, old_p_array, old_len):
        new = (ct.POINTER(structure) * length)()
        ct.memmove(new, old_p_array, ct.sizeof(old_p_array) * old_len)
        return ct.cast(new, ct.POINTER(structure))

    @staticmethod
    def _resize_array(structure, length, old_array):
        new = (structure * length)()
        ct.memmove(new, old_array, ct.sizeof(old_array))
        return new

    def _bucket_index(self, key_hash):
        return key_hash % self.data_slots

    def _getdict(self, struct):
        return dict((field, getattr(struct, field)) for field, _ in struct._fields_)

    def __len__(self):
        return self.len

    def __repr__(self):
        entry_nr = len(self) if len(self) < 20 else 20
        entries = {}
        for i in range(entry_nr):
            d = self._getdict(self.data[i])
            key = d['cht_key']
            del d['cht_key']
            del d['cht_key_hash']
            entries[key] = d
        return f"HashTable{pformat(entries)[1:-1]}\n{' ...' if self.len >= 20 else ''}}})"

    def __str__(self):
        entries = {}
        for i in range(self.len):
            d = self._getdict(self.data[i])
            key = d['cht_key']
            del d['cht_key']
            del d['cht_key_hash']
            entries[key] = d
        return pformat(entries)

