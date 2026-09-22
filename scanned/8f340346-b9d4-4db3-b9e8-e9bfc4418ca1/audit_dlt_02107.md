# [?] fix(forge): prevent gas underflow in delete operations on Cancun (#13157)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-01-20
Source: https://github.com/foundry-rs/foundry/commit/e03e3ff39791987cac5f0b2675f50cb376fe1f77
Type: security-commit

## Details
fix(forge): prevent gas underflow in delete operations on Cancun (#13157)

Fixes a gas underflow issue that occurs when using `delete` operations within a `pauseGasMetering` block on the Cancun EVM version.

In Cancun, the reported gas usage can drop below the stipend due to the absence of the EIP-7702 gas floor (unlike in Prague). This previously triggered a wrapping subtraction panic in the test runner's gas calculation.

This PR replaces the wrapping subtraction with a saturating subtraction to correctly handle this scenario, ensuring that gas usage is reported as 0 rather than underflowing to a large integer.

Fixes https://github.com/foundry-rs/foundry/issues/12803

Co-authored-by: subwaycookiecrunch <lucid7006@gmail.com>
