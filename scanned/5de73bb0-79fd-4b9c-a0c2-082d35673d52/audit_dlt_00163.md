# [M] No bytes clamps for interfaces imported via JSON

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2022-24788
Published: 2022-04-13
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-4mrx-6fxm-8jpg
Type: github-advisory

## Details
### Impact
Importing a function from a JSON interface which returns `bytes` generates bytecode which does not clamp bytes length, potentially resulting in a buffer overrun.

### Patches
0.3.2 (as of https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b)

### Workarounds
Use .vy interfaces.
