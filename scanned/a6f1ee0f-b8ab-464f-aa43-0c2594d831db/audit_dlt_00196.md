# [M] vyper's range(start, start + N) reverts for negative numbers

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32481
CWE: Incorrect Conversion between Numeric Types
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-ppx5-q359-pvwj
Type: github-advisory

## Details
### Summary

When looping over a `range` of the form `range(start, start + N)`, if `start` is negative, the execution will always revert.
 
### Details

This issue is caused by an incorrect assertion inserted by the code generation of the range (`stmt.parse_For_range()`):

https://github.com/vyperlang/vyper/blob/9136169468f317a53b4e7448389aa315f90b95ba/vyper/codegen/stmt.py#L286-L287

This assertion was introduced in https://github.com/vyperlang/vyper/commit/3de1415ee77a9244eb04bdb695e249d3ec9ed868 to fix https://github.com/advisories/GHSA-6r8q-pfpv-7cgj. The issue arises when `start` is signed, instead of using `sle`, `le` is used and `start` is interpreted as an unsigned integer for the comparison. If it is a negative number, its 255th bit is set to `1` and is hence interpreted as a very large unsigned integer making the assertion always fail. 
### PoC

```Vyper
@external
def foo():
    x:int256 = min_value(int256)
    # revert when it should not since we have the following assertion that fails:
    # [assert, [le, min_value(int256), max_value(int256) + 1 - 10]],
    for i in range(x, x + 10):
        pass
```

### Patches

patched in v0.4.0, specifically, https://github.com/vyperlang/vyper/pull/3679 disallows this form of `range()`.

### Impact

Any contract having a `range(start, start + N)` where `start` is a signed integer with the possibility for `start` to be negative is affected. If a call goes through the loop while supplying a negative `start` the execution will revert.
