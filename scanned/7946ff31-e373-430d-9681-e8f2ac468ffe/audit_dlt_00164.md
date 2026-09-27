# [M] missing clamps for decimal args in external functions

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2021-41122
Published: 2021-10-05
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-c7pr-343r-5c46
Type: github-advisory

## Details
### Impact

The following code does not properly validate that its input is in bounds.

```python
@external
def foo(x: decimal) -> decimal:
    return x
```

### Patches
0.3.0 / #2447

### Workarounds
Don't use decimal args
