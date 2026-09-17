# [?] fix(state): surface RocksDB error messages in the block-write panic (#10722)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-06-22
Source: https://github.com/ZcashFoundation/zebra/commit/728afb38e16debc30078196c87654be75cb3dfe9
Type: security-commit

## Details
fix(state): surface RocksDB error messages in the block-write panic (#10722)

fix(state): surface RocksDB's error message in the block-write panic

- Allow operators to see details like "IO error: No space left on device"
