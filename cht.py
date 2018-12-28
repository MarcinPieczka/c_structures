import ctypes as ct

class HashTable:

    def __init__(self, key_type, data_def):
        self.struct = type(
            'struct',
            (ct.Structure,),
            {'__fields__': (('cht_key', key_type), ('cht_key_hash', ct.c_int64)) + data_def.items()}
        )
        