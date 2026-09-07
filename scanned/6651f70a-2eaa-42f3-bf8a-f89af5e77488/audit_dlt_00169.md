# [M] VVE-2020-0003: Call stack corruption when passing complex type containing non-base type members as argument

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
Published: 2020-10-10
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-4v7v-gqf9-ww2g
Type: github-advisory

## Details
### Impact
When we pass a multi-dimensional array (like `[[1, 2], [3, 4]]`) as an argument to internal/external functions we get incorrect output. This is due to a stack management issue, because it was assumed that the size of each subtype of an array/struct is 32, which is not always correct.

Example code:
```python
@internal
def test_input(arr: int128[2][1], i: int128) -> (int128[2][1], int128):
    return arr, i

@external
def test_values(arr: int128[2][1], i: int128) -> (int128[2][1], int128):
    return self.test_input(arr, i)
```

Please see #2183 for further information

### Patches
This problem was fixed in #2184, and released as a part of [`v0.2.6`](https://github.com/vyperlang/vyper/releases/tag/v0.2.6).
