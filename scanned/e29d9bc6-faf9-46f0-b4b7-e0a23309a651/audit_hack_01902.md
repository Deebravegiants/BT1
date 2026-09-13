# [M] 6.3 MemUtils.memcpy Mask Is Wrong

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The memcpy function in MemUtils copies a segment of memory from one location to another. It does so
in 32-byte chunks. However, if the length of the segment to copy is not divisible by 32, it does an
additional copy with a masked value so that no memory values are overwritten when they shouldn't be.
However, this is done incorrectly.

```
function memcpy(uint256 _src, uint256 _dst, uint256 _len) internal pure {
assembly {
// while al least 32 bytes left, copy in 32-byte chunks
for { } gt(_len, 31) { } {
mstore(_dst, mload(_src))
_src := add(_src, 32)
_dst := add(_dst, 32)
_len := sub(_len, 32)
}
if gt(_len, 0) {
```

```
// read the next 32-byte chunk from _dst, replace the first N bytes
// with those left in the _src, and write the transformed chunk back
let mask := sub(shl(1, mul(8, sub(32, _len))), 1) // 2 ** (8 * (32 - _len)) - 1
let srcMasked := and(mload(_src), not(mask))
let dstMasked := and(mload(_dst), mask)
mstore(_dst, or(dstMasked, srcMasked))
}
}
}
```
The mask value is calculated incorrectly. The shl instruction for Solidity assembly is specified as follows:

```
shl(x, y): Logical shift left of y by x bits.
```
Hence, the mask is not shifting 1 to the left by some amount. Instead, mul(8, sub(32, _len)) is
being shifted to the left by 1 bit. As a result, the mask being calculated will always copy at least 30 bytes
(since 2*8*(32-1)-1<512), with the remaining two bytes being partially or not at all copied, depending
on the exact value of _len. In the case of _len % 32 == 16, exactly 31 bytes are copied, meaning an
additional 15 bytes after the end of the memory segment are copied to the destination.

This is the case when dealing with public keys. In the _loadAllocatedSigningKeys and
getSigningKeys functions of the NodeOperatorsRegistry, when the public keys are copied, the length
will be 48 and hence not divisible by 32. So additional bytes are copied.

However, it happens to be the case the when _loadSigningKey is called, the allocated memory for the
public key is directly followed by the signature. Hence, the 15 extra bytes which are copied are the first 15
bytes from the length field of the signature's bytes array. Because this length is always 3, these bytes are
guaranteed to be zero.

Additionally, as the destination of the memory copy is filled left-to-right, for all but the last copy operation
the extra bytes that are written are immediately overwritten by the following value. Only the last copy
writes 15 bytes of zeroes past the end of the publicKeys bytes array. But again, due to the order of
memory allocation, this array is followed in memory by the signatures bytes array. So, the extra bytes
happen to overlap with the length field of the signatures array. As the length of this array is (hopefully)
less than 2 ** (17 * 8), the extra bytes that are overwritten are already set to zero anyway.

All in all, this means that the memcpy function works correctly, but only due to the order of memory
allocations, which happen to guarantee that the extra bytes which are copied to and from are always
zero.

Code corrected

The argument order of the shl expression in the mask calculation was changed.

```
let mask := sub(shl(mul(8, sub(32, _len)), 1), 1)
```
