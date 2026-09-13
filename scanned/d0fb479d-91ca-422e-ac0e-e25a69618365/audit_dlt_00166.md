# [H] VVE-2021-0003: Storage variables overwritten by re-entrancy locks

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-07-27
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-7f92-rr6w-cq64
Type: github-advisory

## Details
### Background
When attempting to use the v0.2.14 release, @pandadefi discovered an issue using the `@nonreentrant` decorator.

### Impact
Reentrancy protection storage slots get allocated to the same slots as storage variables, leading to the corruption of storage variables when using the `@nonreentrant` decorator.

### Patches
This issue was fixed in v0.2.15 in #2391, #2379

### Workarounds
Don't use the `@nonreentrant` decorator in these versions.

### References
https://github.com/vyperlang/vyper/pull/2391, https://github.com/vyperlang/vyper/pull/2379
