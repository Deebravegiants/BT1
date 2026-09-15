# [M] VVE-2021-0001: Memory corruption using function calls within arrays

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-04-16
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-22wc-c9wj-6q2v
Type: github-advisory

## Details
### Impact
When performing a function call inside an array, there is a memory corruption issue that occurs because of an incorrect pointer to the the tip of the stack.

### Patches
This issue was partially fixed in [VVE-2020-0004](https://github.com/vyperlang/vyper/security/advisories/GHSA-2r3x-4mrv-mcxf), however the fix did not update similar code for arrays, which had a similar issue. The issue is fully fixed in https://github.com/vyperlang/vyper/pull/2345
