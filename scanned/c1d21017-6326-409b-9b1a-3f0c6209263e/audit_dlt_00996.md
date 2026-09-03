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

_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/commit/eb011367cc769d62a084deff62153825e626f87a_
