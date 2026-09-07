# [?] fix: update bytes from 1.10.1 to 1.11.1 (RUSTSEC-2026-0007) (#5099)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-02-04
Source: https://github.com/nervosnetwork/ckb/commit/696455dc5000f7bf077e208f4d56c9e452785d84
Type: security-commit

## Details
fix: update bytes from 1.10.1 to 1.11.1 (RUSTSEC-2026-0007) (#5099)

### What problem does this PR solve?

Problem Summary:

RUSTSEC-2026-0007: Integer overflow in `BytesMut::reserve` allows
unchecked addition of `new_cap + offset` to wrap in release builds,
corrupting capacity tracking and enabling out-of-bounds memory access.

### What is changed and how it works?

What's Changed:

- Bump `bytes` dependency from `1.10.1` to `1.11.1` in workspace
`Cargo.toml`
- Update `Cargo.lock` to reflect patched version

Version 1.11.1 adds overflow checks to the reserve path, preventing
capacity corruption.

### Related changes

- N/A

### Check List

Tests

- No code

Side effects

- N/A

<!-- START COPILOT ORIGINAL PROMPT -->



_Trimmed to 38 lines — full report: https://github.com/nervosnetwork/ckb/commit/696455dc5000f7bf077e208f4d56c9e452785d84_
