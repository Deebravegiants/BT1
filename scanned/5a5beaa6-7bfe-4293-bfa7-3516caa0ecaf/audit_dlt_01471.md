# [?] fuzz-tests: fix overflow of u32 in `fuzz-close-tx`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-06-19
Source: https://github.com/ElementsProject/lightning/commit/20e252b5488e5d31aa4f75fb5f0fe803853a4893
Type: security-commit

## Details
fuzz-tests: fix overflow of u32 in `fuzz-close-tx`

Changelog-None: The value WALLY_SATOSHI_PER_BTC * WALLY_BTC_MAX
is equal to 2.1e15, which is much higher than the maximum capacity
of a u32, which is 4.29e9.

Hence, use a u64 to store this value instead.
