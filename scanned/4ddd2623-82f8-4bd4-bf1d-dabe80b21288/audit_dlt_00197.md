# [M] vyper performs incorrect topic logging in raw_log

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32645
CWE: Improper Input Validation
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-xchq-w5r3-4wg3
Type: github-advisory

## Details
### Summary
Incorrect values can be logged when `raw_log` builtin is called with memory or storage arguments to be used as topics.

A contract search was performed and no vulnerable contracts were found in production. In particular, no uses of `raw_log()` were found at all in production; it is apparently not a well-known function.

### Details
The `build_IR` function of the `RawLog` class fails to properly unwrap the variables provided as topics. Consequently, incorrect values are logged as topics.

### PoC
```vyper
x: bytes32

@external
def f():
    self.x = 0x1234567890123456789012345678901234567890123456789012345678901234
    raw_log([self.x], b"") # LOG1(offset:0x60, size:0x00, topic1:0x00)

    y: bytes32 = 0x1234567890123456789012345678901234567890123456789012345678901234
    raw_log([y], b"") # LOG1(offset:0x80, size:0x00, topic1:0x40)
```
### Patches
Fixed in https://github.com/vyperlang/vyper/pull/3977.

### Impact
Incorrect values can be logged which may result in unexpected behavior in client-side applications relying on these logs.
