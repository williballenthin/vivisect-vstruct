import unittest
import binascii

import vstruct
from vstruct.primitives import *
from vstruct.bitfield import *

try:
    # py2
    from cStringIO import StringIO
    from cStringIO import StringIO as BytesIO
except ImportError:
    # py3
    from io import StringIO
    from io import BytesIO

class woot(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.lenfield = v_uint8()
        self.strfield = v_str(size=0x20)

    def pcb_lenfield(self):
        self.vsGetField('strfield').vsSetLength(self.lenfield)


class VStructTest(unittest.TestCase):

    #def setUp(self):
    #def tearDown(self):

    def test_vstruct_basicstruct(self):

        v = vstruct.VStruct()
        v.uint8 = v_uint8(1)
        v.uint16 = v_uint16(2)
        v.uint24 = v_uint24(3)
        v.uint32 = v_uint32(4)
        v.uint64 = v_uint64(5)
        v.vbytes = v_bytes(vbytes=b'ABCD')

        answer = binascii.unhexlify(b'01020003000004000000050000000000000041424344')
        self.assertEqual( v.vsEmit(), answer )


    def test_vstruct_basicreasign(self):
        v = vstruct.VStruct()
        v.uint8 = v_uint8(1)
        v.uint16 = v_uint16(2)
        v.uint24 = v_uint24(3)
        v.uint32 = v_uint32(4)
        v.uint64 = v_uint64(5)
        v.vbytes = v_bytes(vbytes=b'ABCD')

        v.uint8 = 99
        v.uint16 = 100
        v.uint24 = 101
        v.uint32 = 102
        v.uint64 = 103
        v.vbytes = b'\x00\x00\x00\x00'

        answer = binascii.unhexlify(b'63640065000066000000670000000000000000000000')
        self.assertEqual( v.vsEmit(), answer )


    def test_vstruct_fieldalign(self):
        v = vstruct.VStruct()
        v._vs_field_align = True
        v.uint8 = v_uint8(0x42, bigend=True)
        v.uint16 = v_uint16(0x4243, bigend=True)
        v.uint24 = v_uint24(0x424344, bigend=True)
        v.uint32 = v_uint32(0x42434445, bigend=True)
        v.uint64 = v_uint64(0x4243444546474849, bigend=True)

        answer = binascii.unhexlify(b'420042430000424344000000424344454243444546474849')
        self.assertEqual( v.vsEmit(), answer )

    def test_vstruct_fixedpartialasign(self):
        v = vstruct.VStruct()
        v.strfield = v_str(size=30)
        v.unifield = v_wstr(size=30)

        v.strfield = 'wootwoot!'
        v.unifield = 'bazbaz'

        answer = binascii.unhexlify(b'776f6f74776f6f7421000000000000000000000000000000000000000000620061007a00620061007a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')

        self.assertEqual( v.vsEmit(), answer )

    def test_vstruct_lengthcallback(self):

        def updatelen(vs):
            vs.vsGetField('strfield').vsSetLength(vs.lenfield)

        v = vstruct.VStruct()
        v.lenfield = v_uint8(0x30)
        v.strfield = v_str(size=30)
        v.vsAddParseCallback('lenfield', updatelen)

        v.vsParse(b'\x01' + b'A' * 30)
        self.assertEqual( v.vsEmit(), binascii.unhexlify(b'0141') )


    def test_vstruct_classcallback(self):
        v = woot()
        v.vsParse(b'\x01' + b'A'*30)
        self.assertEqual( v.vsEmit(), binascii.unhexlify(b'0141') )

    def test_vstruct_parsefd(self):
        v = woot()
        sio = BytesIO(b'\x01' + b'A' * 30)
        v.vsParseFd(sio)
        self.assertEqual( v.vsEmit(), binascii.unhexlify(b'0141') )

    def test_vstruct_insertfield(self):
        v = woot()
        v.vsInsertField('ifield', v_uint8(), 'strfield')
        v.vsParse(b'\x01BAAAAA')
        self.assertEqual( v.vsEmit(), binascii.unhexlify(b'014241') )

    def test_vstruct_floats(self):

        v = vstruct.VStruct()
        v.float4 = v_float()
        v.float8 = v_double()

        v.float4 = 99.3
        v.float8 = -400.2

        self.assertEqual( v.vsEmit(), binascii.unhexlify('9a99c64233333333330379c0') )

    def test_vstruct_fastparse(self):
        v = vstruct.VStruct()
        v.x = v_uint8()
        v.y = v_str(size=4)
        v.z = v_uint32()

        v.vsParse(b'BAAAAABCD', fast=True)

        self.assertEqual( v.x, 0x42 )
        self.assertEqual( v.y, 'AAAA' )
        self.assertEqual( v.z, 0x44434241 )

    def test_vstruct_fastparse_bigend(self):
        v = vstruct.VStruct()
        v.x = v_uint8()
        v.y = v_str(size=4)
        v.z = v_uint32(bigend=True)

        v.vsParse(b'BAAAAABCD', fast=True)

        self.assertEqual( v.x, 0x42 )
        self.assertEqual( v.y, 'AAAA' )
        self.assertEqual( v.z, 0x41424344 )

    def test_vstruct_varray(self):
        v = vstruct.VArray( [ v_uint8(i) for i in range(20) ] )
        self.assertEqual( int(v[2]), 2 )
        v.vsParse(b'A' * 20)
        self.assertEqual( int(v[2]), 0x41 )

    def test_bitfield(self):
        v = VBitField()
        v.vsAddField('w', v_bits(2))
        v.vsAddField('x', v_bits(3))
        v.vsAddField('y', v_bits(3))
        v.vsAddField('z', v_bits(11))
        v.vsAddField('a', v_bits(3))

        v.vsAddField('stuff', v_bits(23))
        v.vsAddField('pad', v_bits(3))
        v.vsAddField('pad2', v_bits(6))
        v.vsAddField('pad3', v_bits(2))


        v.vsParse(b'AAAAAAA')
        #print v.tree()
        self.assertEqual(1, v.w)
        self.assertEqual(0, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x20a, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x282828, v.stuff)
        self.assertEqual(1, v.pad)
        self.assertEqual(16, v.pad2)
        self.assertEqual(1, v.pad3)

        self.assertEqual(b'AAAAAAA', v.vsEmit())

        v.vsParse(b'ABCDEFG')
        #print v.tree()
        self.assertEqual(1, v.w)
        self.assertEqual(0, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x212, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x6888a8, v.stuff)
        self.assertEqual(6, v.pad)
        self.assertEqual(17, v.pad2)
        self.assertEqual(3, v.pad3)

        self.assertEqual(b'ABCDEFG', v.vsEmit())


        v.vsParse(b'zxcvbnm')
        #print v.tree()
        self.assertEqual(1, v.w)
        self.assertEqual(7, v.x)
        self.assertEqual(2, v.y)
        self.assertEqual(0x3c3, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x6ecc4d, v.stuff)
        self.assertEqual(6, v.pad)
        self.assertEqual(0x1b, v.pad2)
        self.assertEqual(1, v.pad3)

        self.assertEqual(b'zxcvbnm', v.vsEmit())

        
        v.vsParse(b'asdfghj')
        #print v.tree()
        self.assertEqual(1, v.w)
        self.assertEqual(4, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x39b, v.z)
        self.assertEqual(1, v.a)
        self.assertEqual(0xccced, v.stuff)
        self.assertEqual(0, v.pad)
        self.assertEqual(0x1a, v.pad2)
        self.assertEqual(2, v.pad3)

        self.assertEqual(b'asdfghj', v.vsEmit())