# [?] Fix overflow (#84)

## Summary
Severity: Unknown
Chain: Solana
Component: raydium-io/raydium-clmm
Published: 2024-08-13
Source: https://github.com/raydium-io/raydium-clmm/commit/946dc44b779e78665552944a844d8193990b6a56
Type: security-commit

## Details
Fix overflow (#84)

* Fix: fix for overflow while calculate amount

* Fix: fix for stack overflow about U512 overflowing_pow

* optimizate limit price

* catch overflow when calculate amount from liquidity

---------

Co-authored-by: 0x777A <eddy@raydium.io>
