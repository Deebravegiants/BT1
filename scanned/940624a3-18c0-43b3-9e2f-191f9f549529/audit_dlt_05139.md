# [?] Use SignedAmount::unsigned_abs to avoid overflow

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-02-04
Source: https://github.com/lightningdevkit/rust-lightning/commit/2d948fdd33bd3f509fae90f588b27c040a15d7aa
Type: security-commit

## Details
Use SignedAmount::unsigned_abs to avoid overflow

In debug mode, using SignedAmount::abs can lead to an integer overflow
when used with SignedAmount::MIN. Use SignedAmount::unsigned_abs to
avoid this.
