# [M] AugAssign evaluation order causing OOB write within the object

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2025-27105
Published: 2025-02-21
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-4w26-8p97-f4jp
Type: github-advisory

## Details
Vyper handles AugAssign statements by first caching the target location to avoid double evaluation. However, in the case when target is an access to a DynArray and the rhs modifies the array, the cached target will evaluate first, and the bounds check will not be re-evaluated during the write portion of the statement. In other words, the following code

```vyper
def poc():
    a: DynArray[uint256, 2] = [1, 2]
    a[1] += a.pop()
```

is equivalent to:
```vyper
def poc():
    a: DynArray[uint256, 2] = [1, 2]
    a[1] += a[len(a) - 1]
    a.pop()
```
rather than:
```vyper
def poc():
    a: DynArray[uint256, 2] = [1, 2]
    s: uint256 = a[1]
    t: uint256 = a.pop()
    a[1] = s + t  # reverts due to oob access
```
