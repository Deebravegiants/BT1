# [H] Memory corruption when returning a literal struct with a private call inside of it

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2021-41121
Published: 2021-10-06
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-xv8x-pr4h-73jv
Type: github-advisory

## Details
### Impact

When performing a function call inside a literal struct, there is a memory corruption issue that occurs because of an incorrect pointer to the the top of the stack.

### Patches
0.3.0 / #2447
