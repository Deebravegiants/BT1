# [M] OpenZeppelin Contracts Bytes's lastIndexOf function with position argument performs out-of-bound memory access on empty buffers

## Summary
Severity: Medium
Chain: Solidity
Component: @openzeppelin/contracts
CVE: CVE-2025-54070
CWE: Out-of-bounds Read
Published: 2025-07-17
Source: https://github.com/advisories/GHSA-9rcw-c2f9-2j55
Type: github-advisory

## Details
### Impact

The `lastIndexOf(bytes,byte,uint256)` function of the `Bytes.sol` library may access uninitialized memory when the following two conditions hold: 1) the provided buffer length is empty (i.e. `buffer.length == 0`) and position is not `2**256 - 1` (i.e. `pos != type(uint256).max`).

The `pos` argument could be used to access arbitrary data outside of the buffer bounds. This could lead to the operation running out of gas, or returning an invalid index (outside of the empty buffer). Processing this invalid result for accessing the `buffer` would cause a revert under normal conditions.

When triggered, the function reads memory at offset `buffer + 0x20 + pos`. If memory at that location (outside the `buffer`) matches the search pattern, the function would return an out of bound index instead of the expected `type(uint256).max`. This creates unexpected behavior where callers receive a valid-looking index pointing outside buffer bounds.

Subsequent memory accesses that don't check bounds and use the returned index must carefully review the potential impact depending on their setup. Code relying on this function returning `type(uint256).max` for empty buffers or using the returned index without bounds checking could exhibit undefined behavior.

### Patches

Upgrade to 5.4.0
