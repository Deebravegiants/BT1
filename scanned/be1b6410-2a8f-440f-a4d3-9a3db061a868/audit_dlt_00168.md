# [M] VVE-2020-0004: Memory corruption using function calls within tuples / nested calls

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
Published: 2020-10-10
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-2r3x-4mrv-mcxf
Type: github-advisory

## Details
### Impact
When performing a function call inside a tuple or as an argument inside another function call, there is a memory corruption issue that occurs because of an incorrect pointer to the the tip of the stack.

Example code:
```python
@internal
def _foo(a: uint256, b: uint256, c: uint256) -> (uint256, uint256, uint256, uint256, uint256):
    return 1, a, b, c, 5

@internal
def _foo2() -> uint256:
    a: uint256[10] = [6,7,8,9,10,11,12,13,15,16]
    return 4

@external
def foo() -> (uint256, uint256, uint256, uint256, uint256):
    return self._foo(2, 3, self._foo2())
```

Please see #2186 for further information

### Patches
This problem was fixed in #2186, and released as a part of [`v0.2.6`](https://github.com/vyperlang/vyper/releases/tag/v0.2.6).
