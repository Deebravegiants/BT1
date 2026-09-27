# [?] Merge pull request from GHSA-mgv8-gggw-mrg6

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-04-29
Source: https://github.com/vyperlang/vyper/commit/0bb7203b584e771b23536ba065a6efda457161bb
Type: security-commit

## Details
Merge pull request from GHSA-mgv8-gggw-mrg6

* fix: block storage allocator overflows

the storage allocator did not guard against overflow when no storage
layout override was provided. this could result in vulnerabilities like
the following:

```vyper
owner: public(address)
buffer: public(uint256[max_value(uint256)])

@external
def initialize():
    self.owner = msg.sender

@external
def foo(idx: uint256, data: uint256):
    self.buffer[idx] = data
```

while the get_element_ptr calculation for `self.buffer[idx]` is checked,
it is not checked in `mod_{2**256}` arithmetic, which can lead to
arithmetic wrapping back to the `owner` variable if the provided `idx`
is large enough.

* clean up allocator logic

also fix a bug where large allocations would use too much storage due to
floating point rounding precision

* add warning for large arrays

* add note about 2**64 behavior
