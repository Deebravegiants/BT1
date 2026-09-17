# [M] Incorrect is_static parameter for custom stateful precompiles in SputnikVM (evm)

## Summary
Severity: Medium
Chain: evm
Component: evm
CVE: CVE-2022-39354
CWE: Always-Incorrect Control Flow Implementation
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-hhc4-47rh-cr34
Type: github-advisory

## Details
### Impact

A custom stateful precompile can use the `is_static` parameter to determine if the call is executed in a static context (via `STATICCALL`), and thus decide if stateful operations should be done. Previously, the passed `is_static` parameter was incorrect -- it was only set to `true` if the call comes from a **direct** `STATICCALL` opcode. However, once a static call context is entered, it should stay static. 

The issue only impacts custom precompiles that actually uses `is_static`. The maintainers estimate the usage is low. However, for those affected, it can lead to possible incorrect state transitions.

### Patches

PR: https://github.com/rust-blockchain/evm/pull/133
Released in v0.36.0.

Older patch versions can be released on request if anyone needs them. Simply contact @sorpaas by email to request it.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [evm repo](https://github.com/rust-blockchain/evm)
* Email Wei at [wei@that.world](mailto:wei@that.world)
