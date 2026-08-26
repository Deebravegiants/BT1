# [M] Rust EVM erroneousle handles `record_external_operation` error return

## Summary
Severity: Medium
Chain: evm
Component: evm
CVE: CVE-2024-21629
CWE: Improper Check or Handling of Exceptional Conditions
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-27wg-99g8-2v4v
Type: github-advisory

## Details
### Impact

In `rust-evm`, a feature called `record_external_operation` was introduced, allowing library users to record custom gas changes. This feature can have some bogus interactions with the call stack.

In particular, during finalization of a `CREATE` or `CREATE2`, in the case that [the substack execution happens successfully](https://github.com/rust-ethereum/evm/blob/release-v041/src/executor/stack/executor.rs#L1012C25-L1012C69), `rust-evm` will first commit the substate, and then call `record_external_operation(Write(out_code.len()))`. If `record_external_operation` later fails, this error is returned to the parent call stack, instead of `Succeeded`. Yet, the substate commitment already happened. This causes smart contracts able to commit state changes, when the parent caller contract receives zero address (which usually indicates that the execution has failed).

This issue only impacts library users with custom `record_external_operation` that returns errors.

### Patches

The issue is patched in release 0.41.1. The commit can be seem [here](https://github.com/rust-ethereum/evm/commit/d8991ec727ad0fb64fe9957a3cd307387a6701e4).

### Workarounds

None.

### References

Patch PR [#264](https://github.com/rust-ethereum/evm/pull/264).
