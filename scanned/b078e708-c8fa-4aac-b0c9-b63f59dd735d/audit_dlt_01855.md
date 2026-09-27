# [?] rust: bump rkyv to 0.8.16 for RUSTSEC-2026-0122 (#20653)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-05-11
Source: https://github.com/ethereum-optimism/optimism/commit/cef9741905b2dd3711aa628aa59886438abf4e2e
Type: security-commit

## Details
rust: bump rkyv to 0.8.16 for RUSTSEC-2026-0122 (#20653)

`cargo update -p rkyv`. Fixes the unsound `InlineVec::clear` /
`SerVec::clear` advisory flagged by rust-deny.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
