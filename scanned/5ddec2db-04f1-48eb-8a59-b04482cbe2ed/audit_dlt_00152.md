# [C] Incorrectly allocated named re-entrancy locks

## Summary
Severity: Critical
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-39363
Published: 2023-08-05
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-5824-cm3x-3c38
Type: github-advisory

## Details
### Impact

In versions 0.2.15, 0.2.16 and 0.3.0, named re-entrancy locks are allocated incorrectly. Each function using a named re-entrancy lock gets a unique lock regardless of the key, allowing cross-function re-entrancy in contracts compiled with the susceptible versions. A specific set of conditions is required to result in misbehavior of affected contracts, specifically:

- A `.vy` contract compiled with either of the following `vyper` versions: `0.2.15`, `0.2.16`, `0.3.0`
- A primary function that utilizes the `@nonreentrant` decorator with a specific `key` and does not strictly follow the check-effects-interaction pattern (i.e. contains an external call to an untrusted party before storage updates)
- A secondary function that utilizes the same `key` and would be affected by the improper state caused by the primary function

### Patches
https://github.com/vyperlang/vyper/pull/2439, https://github.com/vyperlang/vyper/pull/2514

### Workarounds
Upgrade to 0.3.1 or higher

### References
Technical post-mortem report: https://hackmd.io/@vyperlang/HJUgNMhs2
