# BEGIN_COPYRIGHT
#
# Copyright 2009-2014 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# END_COPYRIGHT

"""
Serialization routines based on Hadoop's SerialUtils.cc.


Expected usage:

.. code-block:: python

   import pydoop.serialize as ps

   class Foo(object):
       def __init__(self, x, y, z):
           assert (isinstance(x, int) and isinstance(y, float)
                   and isinstance(z, str))
           self.x, self.y, self.z = x, y, z
       @classmethod
       def read(cls, stream):
           x = ps.deserialize_int(stream)
           y = ps.deserialize_float(stream)
           z = ps.deserialize_str(stream)
           return Foo(x, y, z)

   ps.register_serializer(Foo, Foo.read)
   ps.register_deserializer('org.apache.hadoop.io.VIntWritable',
                            ps.deserialize_int)

   # in the reader code:
   class Reader(..):
       def __init__(self, ctx):
           self.ctx = ctx
       def next(self):
           ....
           key = ...
           # defaults to no changes if it does not have a deserializer for that
           # type
           key = ps.deserialize(self.ctx.input_key_type, key)
           value = ps.deserialize(self.ctx.input_value_type, value)
           return key, value

   # in the TaskContext code:
   ...
   def emit(self, key, value):
       ...
       # if there is noting registered for type(key), try __str__
       up_link.send('ouput', serialize(key), serialize(value))

We also expect to be able to support something like the following::

 pydoop script my_mr.py  --type-conversion=(VIntWritable,pydoop.serialize.VInt)

"""

from __future__ import division
import struct, xdrlib


# The following is a reimplementation of the Hadoop Pipes c++ utils functions

def read_buffer(n, stream):
    buff = stream.read(n)
    if len(buff) != n:
        raise EOFError
    return buff


def serialize_int(t, stream):
    p = xdrlib.Packer()
    p.pack_int(t)
    stream.write(p.get_buffer())

def deserialize_int(stream):
    SIZE_OF_INT = 4
    buf = read_buffer(SIZE_OF_INT, stream)
    up = xdrlib.Unpacker(buf)
    return up.unpack_int()

def serialize_int_compressed(t, stream):
    if -112 <= t <= 127:
        stream.write(struct.pack('b', t))
    else:
        l = -112
        if t < 0:
            t ^= -1  # remove sign
            l = -120  # encode negativeness in l
        size = (t.bit_length() + 7) // 8
        stream.write(struct.pack('b', l - size))
        # we assume that integers are at most long long
        stream.write(struct.pack('>Q', t)[-size:])
    return

def deserialize_int_compressed(stream):
    b = struct.unpack('b', read_buffer(1, stream))[0]
    if b >= -112:
        return b
    (negative, l) = (True, -120 - b) if b < -120 else (False, -112 - b)
    q = struct.unpack('>Q', '\x00' * (8 - l) + read_buffer(l, stream))[0]
    return q^-1 if negative else q

def serialize_float(t, stream):
    p = xdrlib.Packer()
    p.pack_float(t)
    stream.write(p.get_buffer())

def deserialize_float(stream):
    """
    **NOTE:** floats are serialized using XDR (4 bytes).  When mapped
    back to python, the float is upgraded to a double, so it could be
    slightly different than the original value.
    """
    SIZE_OF_FLOAT = 4
    buf = read_buffer(SIZE_OF_FLOAT, stream)
    up = xdrlib.Unpacker(buf)
    return up.unpack_float()

def serialize_bool_compressed(v, stream):
    serialize_int_compressed(int(v), stream)

def deserialize_bool_compressed(stream):
    return bool(deserialize_int_compressed(stream))


def serialize_string(s, stream):
    p = xdrlib.Packer()
    p.pack_int(len(s))
    stream.write(p.get_buffer())
    if len(s) > 0:
        stream.write(s)
        
def deserialize_string(stream):
    l = deserialize_int(stream)
    return read_buffer(l, stream)

def serialize_string_compressed(s, stream):
    """
    This is the wire format used by hadoop pipes.
    The string length is encoded using VInt.
    """
    serialize_int_compressed(len(s), stream)
    if len(s) > 0:
        stream.write(s)

def deserialize_string_compressed(stream):
    l = deserialize_int_compressed(stream)
    return read_buffer(l, stream)


class SerializerStore(object):
    def __init__(self):
        self.serialize_map = {}
        self.deserialize_map = {}
    def register_serializer(self, class_id, ser_func):
        self.serialize_map[class_id] = ser_func
    def register_deserializer(self, class_id, deser_func):
        self.deserialize_map[class_id] = deser_func
    def serializer(self, type_id):
        return self.serialize_map[type_id]
    def deserializer(self, type_id):
        return self.deserialize_map[type_id]

DEFAULT_STORE = SerializerStore()

DEFAULT_STORE.register_serializer(int, serialize_int_compressed)
DEFAULT_STORE.register_serializer(str, serialize_string_compressed)
DEFAULT_STORE.register_serializer(float, serialize_float)
DEFAULT_STORE.register_serializer(bool, serialize_bool_compressed)

DEFAULT_STORE.register_deserializer(int, deserialize_int_compressed)
DEFAULT_STORE.register_deserializer(str, deserialize_string_compressed)
DEFAULT_STORE.register_deserializer(float, deserialize_float)
DEFAULT_STORE.register_deserializer(bool, deserialize_bool_compressed)

DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.VIntWritable',
                                    deserialize_int_compressed)
DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.VLongWritable',
                                    deserialize_int_compressed)
DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.FloatWritable',
                                    deserialize_float)
DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.BooleanWritable',
                                    deserialize_bool_compressed)
DEFAULT_STORE.register_deserializer('BytesOnWire',
                                    deserialize_string_compressed)
DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.BytesWritable',
                                    deserialize_string)
DEFAULT_STORE.register_deserializer('org.apache.hadoop.io.Text',
                                    deserialize_string_compressed)
DEFAULT_STORE.register_deserializer('java.lang.String',
                                    deserialize_string)

def serialize(v, stream, type_id=None):
    type_id = type_id if not type_id is None else type(v)
    return DEFAULT_STORE.serializer(type_id)(v, stream)

def deserialize(type_id, stream):
    return DEFAULT_STORE.deserializer(type_id)(stream)
