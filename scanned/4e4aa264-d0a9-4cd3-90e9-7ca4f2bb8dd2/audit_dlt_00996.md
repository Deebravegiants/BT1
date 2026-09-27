# [?] fix[codegen]: fix `_abi_decode` buffer overflow (#3925)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-05-28
Source: https://github.com/vyperlang/vyper/commit/eb011367cc769d62a084deff62153825e626f87a
Type: security-commit

## Details
fix[codegen]: fix `_abi_decode` buffer overflow (#3925)

this commit fixes two related bugs in the ABI decoder.

the first is that the ABI decoder does not have a buffer overflow check
for "head" (aka, dynamic offsets) pointers. this can result in a toctou,
where the result of ABI decoding a bytearray can depend on the value
allocated after the bytearray in memory, and a change is observable if
there is a memory write between two ABI decodes of the same buffer:

```vyper
def foo(xs: Bytes[1024]):
    y: Bytes[32] = b"foo"
    x: Bytes[1024] = xs
    # the `head` element of `xs` points outside of the `xs` buffer,
    # to `y`
    z1: Bytes[32] = _abi_decode(y, Bytes[32])
    y = b"bar"
    # `z1` != `x2`
    z2: Bytes[32] = _abi_decode(y, Bytes[32])
```

the second is that the "head" pointer can point within the allocated
buffer but not within the payload. for instance, we might allocate 1024
bytes as an upper bound for the payload, but the payload could be just
128 bytes at runtime. if the "head" pointer points to 160, then the
decoder might read dirty memory. we ban this behavior to prevent
introspection of dirty memory.

both of these are only considered security vulnerabilities when the
payload is in memory. if the payload is in calldata (or returndata -
although that is not currently applicable since we do not ABI decode
directly from returndata at this time), the payload is user-controlled,
and the worst they can do is force reads of zero bytes. therefore, the
fix here only does the overflow check for decodes from memory.

an alternative implementation strategy was considered, which is to
decode ABI payloads more "strictly" - requiring that each "head" pointer
is equal the the previous "head" plus the length of that item, but this
was scrapped as it would requires a larger change to the decoder.

---------

Co-authored-by: Charles Cooper <cooper.charles.m@gmail.com>
Co-authored-by: Daniel Schiavini <daniel.schiavini@gmail.com>

### tests/functional/builtins/codegen/test_abi_decode.py
```diff
@@ -4,6 +4,7 @@
 from tests.evm_backends.base_env import EvmError, ExecutionReverted
 from tests.utils import decimal_to_int
 from vyper.exceptions import ArgumentException, StructureException
+from vyper.utils import method_id
 
 TEST_ADDR = "0x" + b"".join(chr(i).encode("utf-8") for i in range(20)).hex()
 
@@ -471,3 +472,611 @@ def foo(x: Bytes[32]):
 @pytest.mark.parametrize("bad_code,exception", FAIL_LIST)
 def test_abi_decode_length_mismatch(get_contract, assert_compile_failed, bad_code, exception):
     assert_compile_failed(lambda: get_contract(bad_code), exception)
+
+
+def _abi_payload_from_tuple(payload: tuple[int | bytes, ...]) -> bytes:
+    return b"".join(p.to_bytes(32, "big") if isinstance(p, int) else p for p in payload)
+
+
+def _replicate(value: int, count: int) -> tuple[int, ...]:
+    return (value,) * count
+
+
+def test_abi_decode_arithmetic_overflow(env, tx_failed, get_contract):
+    # test based on GHSA-9p8r-4xp4-gw5w:
+    # https://github.com/vyperlang/vyper/security/advisories/GHSA-9p8r-4xp4-gw5w#advisory-comment-91841
+    # buf + head causes arithmetic overflow
+    code = """
+@external
+def f(x: Bytes[32 * 3]):
+    a: Bytes[32] = b"foo"
+    y: Bytes[32 * 3] = x
+
+    decoded_y1: Bytes[32] = _abi_decode(y, Bytes[32])
+    a = b"bar"
+    decoded_y2: Bytes[32] = _abi_decode(y, Bytes[32])
+
+    assert decoded_y1 != decoded_y2
+    """
+    c = get_contract(code)
+
+    data = method_id("f(bytes)")
+    payload = (
+        0x20,  # tuple head
+        0x60,  # parent array length
+        # parent payload - this word will be considered as the head of the abi-encoded inner array
+        # and it will be added to base ptr leading to an arithmetic overflow
+        2**256 - 0x60,
+    )
+    data += _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        env.message_call(c.address, data=data)
+
+
+def test_abi_decode_nonstrict_head(env, tx_failed, get_contract):
+    # data isn't strictly encoded - head is 0x21 instead of 0x20
+    # but the head + length is still within runtime bounds of the parent buffer
+    code = """
+@external
+def f(x: Bytes[32 * 5]):
+    y: Bytes[32 * 5] = x
+    a: Bytes[32] = b"a"
+    decoded_y1: DynArray[uint256, 3] = _abi_decode(y, DynArray[uint256, 3])
+    a = b"aaaa"
+    decoded_y1 = _abi_decode(y, DynArray[uint256, 3])
+    """
+    c = get_contract(code)
+
+    data = method_id("f(bytes)")
+
+    payload = (
+        0x20,  # tuple head
+        0xA0,  # parent array length
+        # head should be 0x20 but is 0x21 thus the data isn't strictly encoded
+        0x21,
+        # we don't want to revert on invalid length, so set this to 0
+        # the first byte of payload will be considered as the length
+        0x00,
+        (0x01).to_bytes(1, "big"),  # will be considered as the length=1
+        (0x00).to_bytes(31, "big"),
+        *_replicate(0x03, 2),
+    )
+
+    data += _abi_payload_from_tuple(payload)
+
+    env.message_call(c.address, data=data)
+
+
+def test_abi_decode_child_head_points_to_parent(tx_failed, get_contract):
+    # data isn't strictly encoded and the head for the inner array
+    # skipts the corresponding payload and points to other valid section of the parent buffer
+    code = """
+@external
+def run(x: Bytes[14 * 32]):
+    y: Bytes[14 * 32] = x
+    decoded_y1: DynArray[DynArray[DynArray[uint256, 2], 1], 2] = _abi_decode(
+        y,
+        DynArray[DynArray[DynArray[uint256, 2], 1], 2]
+    )
+    """
+    c = get_contract(code)
+    # encode [[[1, 1]], [[2, 2]]] and modify the head for [1, 1]
+    # to actually point to [2, 2]
+    payload = (
+        0x20,  # top-level array head
+        0x02,  # top-level array length
+        0x40,  # head of DAr[DAr[DAr, uint256]]][0]
+        0xE0,  # head of DAr[DAr[DAr, uint256]]][1]
+        0x01,  # DAr[DAr[DAr, uint256]]][0] length
+        # head of DAr[DAr[DAr, uint256]]][0][0]
+        # points to DAr[DAr[DAr, uint256]]][1][0]
+        0x20 * 6,
+        0x02,  # DAr[DAr[DAr, uint256]]][0][0] length
+        0x01,  # DAr[DAr[DAr, uint256]]][0][0][0]
+        0x01,  # DAr[DAr[DAr, uint256]]][0][0][1]
+        0x01,  # DAr[DAr[DAr, uint256]]][1] length
+        0x20,  # DAr[DAr[DAr, uint256]]][1][0] head
+        0x02,  # DAr[DAr[DAr, uint256]]][1][0] length
+        0x02,  # DAr[DAr[DAr, uint256]]][1][0][0]
+        0x02,  # DAr[DAr[DAr, uint256]]][1][0][1]
+    )
+
+    data = _abi_payload_from_tuple(payload)
+
+    c.run(data)
+
+
+def test_abi_decode_nonstrict_head_oob(tx_failed, get_contract):
+    # data isn't strictly encoded and (non_strict_head + len(DynArray[..][2])) > parent_static_sz
+    # thus decoding the data pointed to by the head would cause an OOB read
+    # non_strict_head + length == parent + parent_static_sz + 1
+    code = """
+@external
+def run(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x
+    decoded_y1: DynArray[Bytes[32 * 3], 3] = _abi_decode(y,  DynArray[Bytes[32 * 3], 3])
+    """
+    c = get_contract(code)
+
+    payload = (
+        0x20,  # DynArray head
+        0x03,  # DynArray length
+        # non_strict_head - if the length pointed to by this head is 0x60 (which is valid
+        # length for the Bytes[32*3] buffer), the decoding function  would decode
+        # 1 byte over the end of the buffer
+        # we define the non_strict_head as: skip the remaining heads, 1st and 2nd tail
+        # to the third tail + 1B
+        0x20 * 8 + 0x20 * 3 + 0x01,  # inner array0 head
+        0x20 * 4 + 0x20 * 3,  # inner array1 head
+        0x20 * 8 + 0x20 * 3,  # inner array2 head
+        0x60,  # DynArray[Bytes[96], 3][0] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][0] data
+        0x60,  # DynArray[Bytes[96], 3][1] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][1]  data
+        # the invalid head points here + 1B (thus the length is 0x60)
+        # we don't revert because of invalid length, but because head+length is OOB
+        0x00,  # DynArray[Bytes[96], 3][2] length
+        (0x60).to_bytes(1, "big"),
+        (0x00).to_bytes(31, "big"),
+        *_replicate(0x03, 2),
+    )
+
+    data = _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        c.run(data)
+
+
+def test_abi_decode_nonstrict_head_oob2(tx_failed, get_contract):
+    # same principle as in Test_abi_decode_nonstrict_head_oob
+    # but adapted for dynarrays
+    code = """
+@external
+def run(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x
+    decoded_y1: DynArray[DynArray[uint256, 3], 3] = _abi_decode(
+        y,
+        DynArray[DynArray[uint256, 3], 3]
+    )
+    """
+    c = get_contract(code)
+
+    payload = (
+        0x20,  # DynArray head
+        0x03,  # DynArray length
+        (0x20 * 8 + 0x20 * 3 + 0x01),  # inner array0 head
+        (0x20 * 4 + 0x20 * 3),  # inner array1 head
+        (0x20 * 8 + 0x20 * 3),  # inner array2 head
+        0x03,  # DynArray[..][0] length
+        *_replicate(0x01, 3),  # DynArray[..][0] data
+        0x03,  # DynArray[..][1] length
+        *_replicate(0x01, 3),  # DynArray[..][1] data
+        0x00,  # DynArray[..][2] length
+        (0x03).to_bytes(1, "big"),
+        (0x00).to_bytes(31, "big"),
+        *_replicate(0x01, 2),  # DynArray[..][2] data
+    )
+
+    data = _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        c.run(data)
+
+
+def test_abi_decode_head_pointing_outside_buffer(tx_failed, get_contract):
+    # the head points completely outside the buffer
+    code = """
+@external
+def run(x: Bytes[3 * 32]):
+    y: Bytes[3 * 32] = x
+    decoded_y1: Bytes[32] = _abi_decode(y, Bytes[32])
+    """
+    c = get_contract(code)
+
+    payload = (0x80, 0x20, 0x01)
+    data = _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        c.run(data)
+
+
+def test_abi_decode_bytearray_clamp(tx_failed, get_contract):
+    # data has valid encoding, but the length of DynArray[Bytes[96], 3][0] is set to 0x61
+    # and thus the decoding should fail on bytestring clamp
+    code = """
+@external
+def run(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x
+    decoded_y1: DynArray[Bytes[32 * 3], 3] = _abi_decode(y,  DynArray[Bytes[32 * 3], 3])
+    """
+    c = get_contract(code)
+
+    payload = (
+        0x20,  # DynArray head
+        0x03,  # DynArray length
+        0x20 * 3,  # inner array0 head
+        0x20 * 4 + 0x20 * 3,  # inner array1 head
+        0x20 * 8 + 0x20 * 3,  # inner array2 head
+        # invalid length - should revert on bytestring clamp
+        0x61,  # DynArray[Bytes[96], 3][0] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][0] data
+        0x60,  # DynArray[Bytes[96], 3][1] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][1] data
+        0x60,  # DynArray[Bytes[96], 3][2] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][2] data
+    )
+
+    data = _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        c.run(data)
+
+
+def test_abi_decode_runtimesz_oob(tx_failed, get_contract, env):
+    # provide enough data, but set the runtime size to be smaller than the actual size
+    # so after y: [..] = x, y will have the incorrect size set and only part of the
+    # original data will be copied. This will cause oob read outside the
+    # runtime sz (but still within static size of the buffer)
+    code = """
+@external
+def f(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x
+    decoded_y1: DynArray[Bytes[32 * 3], 3] = _abi_decode(y,  DynArray[Bytes[32 * 3], 3])
+    """
+    c = get_contract(code)
+
+    data = method_id("f(bytes)")
+
+    payload = (
+        0x20,  # tuple head
+        # the correct size is 0x220 (2*32+3*32+4*3*32)
+        # therefore we will decode after the end of runtime size (but still within the buffer)
+        0x01E4,  # top-level bytes array length
+        0x20,  # DynArray head
+        0x03,  # DynArray length
+        0x20 * 3,  # inner array0 head
+        0x20 * 4 + 0x20 * 3,  # inner array1 head
+        0x20 * 8 + 0x20 * 3,  # inner array2 head
+        0x60,  # DynArray[Bytes[96], 3][0] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][0] data
+        0x60,  # DynArray[Bytes[96], 3][1] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][1] data
+        0x60,  # DynArray[Bytes[96], 3][2] length
+        *_replicate(0x01, 3),  # DynArray[Bytes[96], 3][2] data
+    )
+
+    data += _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        env.message_call(c.address, data=data)
+
+
+def test_abi_decode_runtimesz_oob2(tx_failed, get_contract, env):
+    # same principle as in test_abi_decode_runtimesz_oob
+    # but adapted for dynarrays
+    code = """
+@external
+def f(x: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x
+    decoded_y1: DynArray[DynArray[uint256, 3], 3] = _abi_decode(
+        y,
+        DynArray[DynArray[uint256, 3], 3]
+    )
+    """
+    c = get_contract(code)
+
+    data = method_id("f(bytes)")
+
+    payload = (
+        0x20,  # tuple head
+        0x01E4,  # top-level bytes array length
+        0x20,  # DynArray head
+        0x03,  # DynArray length
+        0x20 * 3,  # inner array0 head
+        0x20 * 4 + 0x20 * 3,  # inner array1 head
+        0x20 * 8 + 0x20 * 3,  # inner array2 head
+        0x03,  # DynArray[..][0] length
+        *_replicate(0x01, 3),  # DynArray[..][0] data
+        0x03,  # DynArray[..][1] length
+        *_replicate(0x01, 3),  # DynArray[..][1] data
+        0x03,  # DynArray[..][2] length
+        *_replicate(0x01, 3),  # DynArray[..][2] data
+    )
+
+    data += _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        env.message_call(c.address, data=data)
+
+
+def test_abi_decode_head_roundtrip(tx_failed, get_contract, env):
+    # top-level head in the y2 buffer points to the y1 buffer
+    # and y1 contains intermediate heads pointing to the inner arrays
+    # which are in turn in the y2 buffer
+    # NOTE: the test is memory allocator dependent - we assume that y1 and y2
+    # have the 800 & 960 addresses respectively
+    code = """
+@external
+def run(x1: Bytes[4 * 32], x2: Bytes[2 * 32 + 3 * 32  + 3 * 32 * 4]):
+    y1: Bytes[4*32] = x1 # addr: 800
+    y2: Bytes[2 * 32 + 3 * 32 + 3 * 32 * 4] = x2 # addr: 960
+    decoded_y1: DynArray[DynArray[uint256, 3], 3] = _abi_decode(
+        y2,
+        DynArray[DynArray[uint256, 3], 3]
+    )
+    """
+    c = get_contract(code)
+
+    payload = (
+        0x03,  # DynArray length
+        # distance to y2 from y1 is 160
+        160 + 0x20 + 0x20 * 3,  # points to DynArray[..][0] length
+        160 + 0x20 + 0x20 * 4 + 0x20 * 3,  # points to DynArray[..][1] length
+        160 + 0x20 + 0x20 * 8 + 0x20 * 3,  # points to DynArray[..][2] length
+    )
+
+    data1 = _abi_payload_from_tuple(payload)
+
+    payload = (
+        # (960 + (2**256 - 160)) % 2**256 == 800, ie will roundtrip to y1
+        2**256 - 160,  # points to y1
+        0x03,  # DynArray length (not used)
+        0x20 * 3,  # inner array0 head
+        0x20 * 4 + 0x20 * 3,  # inner array1 head
+        0x20 * 8 + 0x20 * 3,  # inner array2 head
+        0x03,  # DynArray[..][0] length
+        *_replicate(0x01, 3),  # DynArray[..][0] data
+        0x03,  # DynArray[..][1] length
+        *_replicate(0x02, 3),  # DynArray[..][1] data
+        0x03,  # DynArray[..][2] length
+        *_replicate(0x03, 3),  # DynArray[..][2] data
+    )
+
+    data2 = _abi_payload_from_tuple(payload)
+
+    with tx_failed():
+        c.run(data1, data2)
+
+
+def test_abi_decode_merge_head_and_length(get_contract):
+    # compress head and length into 33B
+    code = """
+@external
+def run(x: Bytes[32 * 2 + 8 * 32]) -> uint256:
+    y: Bytes[32 * 2 + 8 * 32] = x
+    decoded_y1: Bytes[256] = _abi_decode(y, Bytes[256])
+    return len(decoded_y1)
+    """
+    c = get_contract(code)
+
+    payload = (0x01, (0x00).to_bytes(1, "big"), *_replicate(0x00, 8))
+
+    data = _abi_payload_from_tuple(payload)
+
+    length = c.run(data)
+
+    assert length == 256
+
+
+def test_abi_decode_extcall_invalid_head(tx_failed, get_contract):
+    # the head returned from the extcall is set to invalid value of 480
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256):
+    return (480, 0, 0)
+
+interface A:
+    def bar() -> String[32]: nonpayable
+
+@external
+def foo():
+    x:String[32] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
+
+
+def test_abi_decode_extcall_oob(tx_failed, get_contract):
+    # the head returned from the extcall is 1 byte bigger than expected
+    # thus we'll take the last 31 0-bytes from tuple[1] and the 1st byte from tuple[2]
+    # and consider this the length - thus the length is 2**5
+    # and thus we'll read 1B over the buffer end (33 + 32 + 32)
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256):
+    return (33, 0, 2**(5+248))
+
+interface A:
+    def bar() -> String[32]: nonpayable
+
+@external
+def foo():
+    x:String[32] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
+
+
+def test_abi_decode_extcall_runtimesz_oob(tx_failed, get_contract):
+    # the runtime size (33) is bigger than the actual payload (32 bytes)
+    # thus we'll read 1B over the runtime size - but still within the static size of the buffer
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256):
+    return (32, 33, 0)
+
+interface A:
+    def bar() -> String[64]: nonpayable
+
+@external
+def foo():
+    x:String[64] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
+
+
+def test_abi_decode_extcall_truncate_returndata(get_contract):
+    # return more data than expected
+    # the truncated data is still valid
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256, uint256):
+    return (32, 32, 36, 36)
+
+interface A:
+    def bar() -> Bytes[32]: nonpayable
+
+@external
+def foo():
+    x:Bytes[32] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    c.foo()
+
+
+def test_abi_decode_extcall_truncate_returndata2(tx_failed, get_contract):
+    # return more data than expected
+    # after truncation the data is invalid because the length is too big
+    # wrt to the static size of the buffer
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256, uint256):
+    return (32, 33, 36, 36)
+
+interface A:
+    def bar() -> Bytes[32]: nonpayable
+
+@external
+def foo():
+    x:Bytes[32] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
+
+
+def test_abi_decode_extcall_return_nodata(tx_failed, get_contract):
+    code = """
+@external
+def bar():
+    return
+
+interface A:
+    def bar() -> Bytes[32]: nonpayable
+
+@external
+def foo():
+    x:Bytes[32] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+    with tx_failed():
+        c.foo()
+
+
+def test_abi_decode_extcall_array_oob(tx_failed, get_contract):
+    # same as in test_abi_decode_extcall_oob
+    # DynArray[..][1] head isn't strict and points 1B over
+    # thus the 1st B of 2**(5+248) is considered as the length (32)
+    # thus we try to decode 1B over the buffer end
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256):
+    return (
+        32, # DynArray head
+        2,  # DynArray length
+        32 * 2,  # DynArray[..][0] head
+        32 * 2 + 32 * 2 + 1, # DynArray[..][1] head
+        32, # DynArray[..][0] length
+        0,  # DynArray[..][0] data
+        0,  # DynArray[..][1] length
+        2**(5+248) # DynArray[..][1] length (and data)
+    )
+
+interface A:
+    def bar() -> DynArray[Bytes[32], 2]: nonpayable
+
+@external
+def run():
+    x: DynArray[Bytes[32], 2] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+
+    with tx_failed():
+        c.run()
+
+
+def test_abi_decode_extcall_array_oob_with_truncate(tx_failed, get_contract):
+    # same as in test_abi_decode_extcall_oob but we also return more data than expected
+    # DynArray[..][1] head isn't strict and points 1B over
+    # thus the 1st B of 2**(5+248) is considered as the length (32)
+    # thus we try to decode 1B over the buffer end
+    code = """
+@external
+def bar() -> (uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256):
+    return (
+        32, # DynArray head
+        2,  # DynArray length
+        32 * 2,  # DynArray[..][0] head
+        32 * 2 + 32 * 2 + 1, # DynArray[..][1] head
+        32, # DynArray[..][0] length
+        0,  # DynArray[..][0] data
+        0,  # DynArray[..][1] length
+        2**(5+248), # DynArray[..][1] length (and data)
+        0   # extra data
+    )
+
+interface A:
+    def bar() -> DynArray[Bytes[32], 2]: nonpayable
+
+@external
+def run():
+    x: DynArray[Bytes[32], 2] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+
+    with tx_failed():
+        c.run()
+
+
+def test_abi_decode_extcall_zero_len_array(get_contract):
+    code = """
+@external
+def bar() -> (uint256, uint256):
+    return 32, 0
+
+interface A:
+    def bar() -> DynArray[Bytes[32], 2]: nonpayable
+
+@external
+def run():
+    x: DynArray[Bytes[32], 2] = extcall A(self).bar()
+    """
+    c = get_contract(code)
+
+    c.run()
+
+
+def test_abi_decode_extcall_zero_len_array2(get_contract):
+    code = """
+@external
+def bar() -> (uint256, uint256):
+    return 0, 0
+
+interface A:
+    def bar() -> DynArray[Bytes[32], 2]: nonpayable
+
+@external
+def run() -> uint256:
+    x: DynArray[Bytes[32], 2] = extcall A(self).bar()
+    return len(x)
+    """
+    c = get_contract(code)
+
+    length = c.run()
+
+    assert length == 0
```

### tests/functional/builtins/codegen/test_empty.py
```diff
@@ -619,24 +619,17 @@ def test_clear_typecheck(contract, get_contract, assert_compile_failed):
     assert_compile_failed(lambda: get_contract(contract), TypeMismatch)
 
 
+_33_bytes = b"\x01" * 33
+_65_bytes = b"\x01" * 65
+
+
 @pytest.mark.parametrize(
     "a,b,expected",
     [
-        ("empty(Bytes[65])", "b'hello'", (b"hello", b"")),
-        ("b'hello'", "empty(Bytes[33])", (b"", b"hello")),
-        (
-            "empty(Bytes[65])",
-            "b'thirty three bytes long baby!!!!!'",
-            (b"thirty three bytes long baby!!!!!", b""),
-        ),
-        (
-            "b'thirty three bytes long baby!!!aathirty three bytes long baby!!!a'",
-            "b'thirty three bytes long baby!!!aa'",
-            (
-                b"thirty three bytes long baby!!!aa",
-                b"thirty three bytes long baby!!!aathirty three bytes long baby!!!a",
-            ),
-        ),
+        ("empty(Bytes[65])", b"hello", (b"hello", b"")),
+        (b"hello", "empty(Bytes[33])", (b"", b"hello")),
+        ("empty(Bytes[65])", _33_bytes, (_33_bytes, b"")),
+        (_65_bytes, _33_bytes, (_33_bytes, _65_bytes)),
     ],
 )
 def test_empty_as_func_arg(get_contract, a, b, expected):
```

### vyper/builtins/functions.py
```diff
@@ -14,6 +14,7 @@
     add_ofst,
     bytes_data_ptr,
     calculate_type_for_external_return,
+    check_buffer_overflow_ir,
     check_external_call,
     clamp,
     clamp2,
@@ -232,18 +233,6 @@ def build_IR(self, expr, context):
 ADHOC_SLICE_NODE_MACROS = ["~calldata", "~selfcode", "~extcode"]
 
 
-# make sure we don't overrun the source buffer, checking for overflow:
-# valid inputs satisfy:
-#   `assert !(start+length > src_len || start+length < start`
-def _make_slice_bounds_check(start, length, src_len):
-    with start.cache_when_complex("start") as (b1, start):
-        with add_ofst(start, length).cache_when_complex("end") as (b2, end):
-            arithmetic_overflow = ["lt", end, start]
-            buffer_oob = ["gt", end, src_len]
-            ok = ["iszero", ["or", arithmetic_overflow, buffer_oob]]
-            return b1.resolve(b2.resolve(["assert", ok]))
-
-
 def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context: Context) -> IRnode:
     assert length.is_literal, "typechecker failed"
     assert isinstance(length.value, int)  # mypy hint
@@ -257,7 +246,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
         if sub.value == "~calldata":
             node = [
                 "seq",
-                _make_slice_bounds_check(start, length, "calldatasize"),
+                check_buffer_overflow_ir(start, length, "calldatasize"),
                 ["mstore", buf, length],
                 ["calldatacopy", add_ofst(buf, 32), start, length],
                 buf,
@@ -267,7 +256,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
         elif sub.value == "~selfcode":
             node = [
                 "seq",
-                _make_slice_bounds_check(start, length, "codesize"),
+                check_buffer_overflow_ir(start, length, "codesize"),
                 ["mstore", buf, length],
                 ["codecopy", add_ofst(buf, 32), start, length],
                 buf,
@@ -282,7 +271,7 @@ def _build_adhoc_slice_node(sub: IRnode, start: IRnode, length: IRnode, context:
                 sub.args[0],
                 [
                     "seq",
-                    _make_slice_bounds_check(start, length, ["extcodesize", "_extcode_address"]),
+                    check_buffer_overflow_ir(start, length, ["extcodesize", "_extcode_address"]),
                     ["mstore", buf, length],
                     ["extcodecopy", "_extcode_address", add_ofst(buf, 32), start, length],
                     buf,
@@ -456,7 +445,7 @@ def build_IR(self, expr, args, kwargs, context):
 
             ret = [
                 "seq",
-                _make_slice_bounds_check(start, length, src_len),
+                check_buffer_overflow_ir(start, length, src_len),
                 do_copy,
                 ["mstore", dst, length],  # set length
                 dst,  # return pointer to dst
@@ -2539,7 +2528,11 @@ def build_IR(self, expr, args, kwargs, context):
 
             # sanity check buffer size for wrapped output type will not buffer overflow
             assert wrapped_typ.memory_bytes_required == output_typ.memory_bytes_required
-            ret.append(make_setter(output_buf, to_decode))
+
+            # pass a buffer bound to make_setter so appropriate oob
+            # validation is performed
+            buf_bound = add_ofst(data_ptr, data_len)
+            ret.append(make_setter(output_buf, to_decode, hi=buf_bound))
 
             ret.append(output_buf)
             # finalize. set the type and location for the return buffer.
```

### vyper/codegen/core.py
```diff
@@ -194,7 +194,7 @@ def dynarray_data_ptr(ptr):
     return add_ofst(ptr, ptr.location.word_scale)
 
 
-def _dynarray_make_setter(dst, src):
+def _dynarray_make_setter(dst, src, hi=None):
     assert isinstance(src.typ, DArrayT)
     assert isinstance(dst.typ, DArrayT)
 
@@ -208,6 +208,9 @@ def _dynarray_make_setter(dst, src):
     # before we clobber the length word.
 
     if src.value == "multi":
+        # validation is only performed on unsafe data, but we are dealing with
+        # a literal here.
+        assert hi is None
         ret = ["seq"]
         # handle literals
 
@@ -258,6 +261,7 @@ def _dynarray_make_setter(dst, src):
                 loop_body = make_setter(
                     get_element_ptr(dst, i, array_bounds_check=False),
                     get_element_ptr(src, i, array_bounds_check=False),
+                    hi=hi,
                 )
                 loop_body.annotation = f"{dst}[i] = {src}[i]"
 
@@ -449,7 +453,7 @@ def _mul(x, y):
 
 
 # Resolve pointer locations for ABI-encoded data
-def _getelemptr_abi_helper(parent, member_t, ofst, clamp=True):
+def _getelemptr_abi_helper(parent, member_t, ofst):
     member_abi_t = member_t.abi_type
 
     # ABI encoding has length word and then pretends length is not there
@@ -462,9 +466,10 @@ def _getelemptr_abi_helper(parent, member_t, ofst, clamp=True):
 
     if member_abi_t.is_dynamic():
         # double dereference, according to ABI spec
-        # TODO optimize special case: first dynamic item
-        # offset is statically known.
         ofst_ir = add_ofst(parent, unwrap_location(ofst_ir))
+        if _dirty_read_risk(ofst_ir):
+            # check no arithmetic overflow
+            ofst_ir = ["seq", ["assert", ["ge", ofst_ir, parent]], ofst_ir]
 
     return IRnode.from_list(
         ofst_ir,
@@ -476,7 +481,7 @@ def _getelemptr_abi_helper(parent, member_t, ofst, clamp=True):
 
 
 # TODO simplify this code, especially the ABI decoding
-def _get_element_ptr_tuplelike(parent, key):
+def _get_element_ptr_tuplelike(parent, key, hi=None):
     typ = parent.typ
     assert is_tuple_like(typ)
 
@@ -487,7 +492,7 @@ def _get_element_ptr_tuplelike(parent, key):
         index = attrs.index(key)
         annotation = key
     else:
-        # TupleT
+        assert isinstance(typ, TupleT)
         assert isinstance(key, int)
         subtype = typ.member_types[key]
         attrs = list(typ.tuple_keys())
@@ -872,10 +877,41 @@ def needs_clamp(t, encoding):
     raise CompilerPanic("unreachable")  # pragma: nocover
 
 
+# when abi encoded data is user provided and lives in memory,
+# we risk either reading oob of the buffer or oob of the payload data.
+# in these cases, we need additional validation.
+def _dirty_read_risk(ir_node):
+    return ir_node.encoding == Encoding.ABI and ir_node.location == MEMORY
+
+
+# child elements which have dynamic length, and could overflow the buffer
+# even if the start of the item is in-bounds.
+def _abi_payload_size(ir_node):
+    SCALE = ir_node.location.word_scale
+    assert SCALE == 32  # we must be in some byte-addressable region, like memory
+
+    OFFSET = DYNAMIC_ARRAY_OVERHEAD * SCALE
+
+    if isinstance(ir_node.typ, DArrayT):
+        return ["add", OFFSET, ["mul", get_dyn_array_count(ir_node), SCALE]]
+
+    if isinstance(ir_node.typ, _BytestringT):
+        return ["add", OFFSET, get_bytearray_length(ir_node)]
+
+    raise CompilerPanic("unreachable")  # pragma: nocover
+
+
 # Create an x=y statement, where the types may be compound
-def make_setter(left, right):
+def make_setter(left, right, hi=None):
     check_assign(left, right)
 
+    # we need bounds checks when decoding from memory, otherwise we can
+    # get oob reads.
+    #
+    # the caller is responsible for calculating the bound;
+    # sanity check that there is a bound if there is dirty read risk
+    assert (hi is not None) == _dirty_read_risk(right)
+
     # For types which occupy just one word we can use single load/store
     if left.typ._is_prim_word:
         enc = right.encoding  # unwrap_location butchers encoding
@@ -892,7 +928,7 @@ def make_setter(left, right):
         if needs_clamp(right.typ, right.encoding):
             with right.cache_when_complex("bs_ptr") as (b, right):
                 copier = make_byte_array_copier(left, right)
-                ret = b.resolve(["seq", clamp_bytestring(right), copier])
+                ret = b.resolve(["seq", clamp_bytestring(right, hi=hi), copier])
         else:
             ret = make_byte_array_copier(left, right)
 
@@ -907,8 +943,8 @@ def make_setter(left, right):
         # TODO rethink/streamline the clamp_basetype logic
         if needs_clamp(right.typ, right.encoding):
             with right.cache_when_complex("arr_ptr") as (b, right):
-                copier = _dynarray_make_setter(left, right)
-                ret = b.resolve(["seq", clamp_dyn_array(right), copier])
+                copier = _dynarray_make_setter(left, right, hi=hi)
+                ret = b.resolve(["seq", clamp_dyn_array(right, hi=hi), copier])
         else:
             ret = _dynarray_make_setter(left, right)
 
@@ -917,7 +953,7 @@ def make_setter(left, right):
     # Complex Types
     assert isinstance(left.typ, (SArrayT, TupleT, StructT))
 
-    return _complex_make_setter(left, right)
+    return _complex_make_setter(left, right, hi=hi)
 
 
 # locations with no dedicated copy opcode
@@ -929,7 +965,7 @@ def copy_opcode_available(left, right):
     return left.location == MEMORY and right.location.has_copy_opcode
 
 
-def _complex_make_setter(left, right):
+def _complex_make_setter(left, right, hi=None):
     if right.value == "~empty" and left.location == MEMORY:
         # optimized memzero
         return mzero(left, left.typ.memory_bytes_required)
@@ -1013,13 +1049,14 @@ def _complex_make_setter(left, right):
         for k in keys:
             l_i = get_element_ptr(left, k, array_bounds_check=False)
             r_i = get_element_ptr(right, k, array_bounds_check=False)
-            ret.append(make_setter(l_i, r_i))
+            ret.append(make_setter(l_i, r_i, hi=hi))
 
         return b1.resolve(b2.resolve(IRnode.from_list(ret)))
 
 
 def ensure_in_memory(ir_var, context):
-    """Ensure a variable is in memory. This is useful for functions
+    """
+    Ensure a variable is in memory. This is useful for functions
     which expect to operate on memory variables.
     """
     if ir_var.location == MEMORY:
@@ -1085,19 +1122,47 @@ def sar(bits, x):
     return ["sar", bits, x]
 
 
-def clamp_bytestring(ir_node):
+def clamp_bytestring(ir_node, hi=None):
     t = ir_node.typ
     if not isinstance(t, _BytestringT):  # pragma: nocover
         raise CompilerPanic(f"{t} passed to clamp_bytestring")
-    ret = ["assert", ["le", get_bytearray_length(ir_node), t.maxlen]]
-    return IRnode.from_list(ret, error_msg=f"{ir_node.typ} bounds check")
 
+    # check if byte array length is within type max
+    with get_bytearray_length(ir_node).cache_when_complex("length") as (b1, length):
+        len_check = ["assert", ["le", length, t.maxlen]]
+
+        assert (hi is not None) == _dirty_read_risk(ir_node)
+        if hi is not None:
+            assert t.maxlen < 2**64  # sanity check
 
-def clamp_dyn_array(ir_node):
+            # note: this add does not risk arithmetic overflow because
+            # length is bounded by maxlen.
+            item_end = add_ofst(ir_node, _abi_payload_size(ir_node))
+
+            len_check = ["seq", ["assert", ["le", item_end, hi]], len_check]
+
+        return IRnode.from_list(b1.resolve(len_check), error_msg=f"{ir_node.typ} bounds check")
+
+
+def clamp_dyn_array(ir_node, hi=None):
     t = ir_node.typ
     assert isinstance(t, DArrayT)
-    ret = ["assert", ["le", get_dyn_array_count(ir_node), t.count]]
-    return IRnode.from_list(ret, error_msg=f"{ir_node.typ} bounds check")
+
+    len_check = ["assert", ["le", get_dyn_array_count(ir_node), t.count]]
+
+    assert (hi is not None) == _dirty_read_risk(ir_node)
+
+    # if the subtype is dynamic, the check will be performed in the recursion
+    if hi is not None and not t.abi_type.subtyp.is_dynamic():
+        assert t.count < 2**64  # sanity check
+
+        # note: this add does not risk arithmetic overflow because
+        # length is bounded by count * elemsize.
+        item_end = add_ofst(ir_node, _abi_payload_size(ir_node))
+
+        len_check = ["seq", ["assert", ["le", item_end, hi]], len_check]
+
+    return IRnode.from_list(len_check, error_msg=f"{ir_node.typ} bounds check")
 
 
 # clampers for basetype
@@ -1211,3 +1276,15 @@ def clamp2(lo, arg, hi, signed):
         LE = "sle" if signed else "le"
         ret = ["seq", ["assert", ["and", [GE, arg, lo], [LE, arg, hi]]], arg]
         return IRnode.from_list(b1.resolve(ret), typ=arg.typ)
+
+
+# make sure we don't overrun the source buffer, checking for overflow:
+# valid inputs satisfy:
+#   `assert !(start+length > src_len || start+length < start)`
+def check_buffer_overflow_ir(start, length, src_len):
+    with start.cache_when_complex("start") as (b1, start):
+        with add_ofst(start, length).cache_when_complex("end") as (b2, end):
+            arithmetic_overflow = ["lt", end, start]
+            buffer_oob = ["gt", end, src_len]
+            ok = ["iszero", ["or", arithmetic_overflow, buffer_oob]]
+            return b1.resolve(b2.resolve(["assert", ok]))
```

### vyper/codegen/external_call.py
```diff
@@ -119,7 +119,14 @@ def _unpack_returndata(buf, fn_type, call_kwargs, contract_address, context, exp
         return_buf = context.new_internal_variable(wrapped_return_t)
 
         # note: make_setter does ABI decoding and clamps
-        unpacker.append(make_setter(return_buf, buf))
+
+        payload_bound = IRnode.from_list(
+            ["select", ["lt", ret_len, "returndatasize"], ret_len, "returndatasize"]
+        )
+        with payload_bound.cache_when_complex("payload_bound") as (b1, payload_bound):
+            unpacker.append(
+                b1.resolve(make_setter(return_buf, buf, hi=add_ofst(buf, payload_bound)))
+            )
     else:
         return_buf = buf
 
```
