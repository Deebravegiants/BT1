# [M] 6.5 Value for the Call Can Be Loaded From Wrong

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Memory Location

Correctness Medium Version 1 Code Corrected

When a call with value is performed in VM the first index is treated as an index for the state element. The
read from this memory location is done via assembly instruction.

```
bytes memory v = state[uint8(bytes1(indices))];
assembly {
callEth := mload(add(v, 0x20))
}
```
This mload skips 1 word - the length of the state element. However, the state element can be empty. In
this case, the mload will read memory allocated for other data. Since callEth should be a uint
typed argument, it should be treated the same way as any other static variable.

Code corrected:

Enso responded:

```
We now validate that the state element’s length is 32 bytes and convert it into a uint256.
```
