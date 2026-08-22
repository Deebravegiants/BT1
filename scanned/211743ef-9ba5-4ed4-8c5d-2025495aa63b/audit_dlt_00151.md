# [M] incorrect re-entrancy lock when key is empty string

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-42441
Published: 2023-09-15
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-3hg2-r75x-g69m
Type: github-advisory

## Details
### Impact

Locks of the type `@nonreentrant("")` or `@nonreentrant('')` do not produce reentrancy checks at runtime.

```Vyper
@nonreentrant("") # unprotected
@external
def bar():
    pass

@nonreentrant("lock") # protected
@external
def foo():
    pass
```
### Patches

Patched in #3605

### Workarounds

The lock name should be a non-empty string.

### References
_Are there any links users can visit to find out more?_
