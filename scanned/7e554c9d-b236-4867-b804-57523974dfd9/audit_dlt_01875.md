# [?] op-node: Fix uint64 overflow in yParity calculation and use Uint64Strict instead of UInt64 for safety (#18921)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-01-26
Source: https://github.com/ethereum-optimism/optimism/commit/b8a91297ea47b224a071db3ae6a721445e9fc8d1
Type: security-commit

## Details
op-node: Fix uint64 overflow in yParity calculation and use Uint64Strict instead of UInt64 for safety (#18921)

* op-node: Use Uint64Strict.

* op-node: Use big.Int to calculate yParity/v to support large chain IDs.

* Update tests to compare big.Int logically
