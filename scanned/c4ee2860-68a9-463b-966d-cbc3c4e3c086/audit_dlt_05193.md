# [?] Update lz4-sys to fix GHSA-9q5j-jm53-v7vr (CVE-2021-3520)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-08
Source: https://github.com/Conflux-Chain/conflux-rust/commit/8f6606d5c972f2e5372db368d0716acbb657244f
Type: security-commit

## Details
Update lz4-sys to fix GHSA-9q5j-jm53-v7vr (CVE-2021-3520)

Update rust-rocksdb rev to use crates.io lz4-sys 1.11 instead of
the busyjay/lz4-rs fork (1.8.3). The fork was created in 2017 to add
header copying and cargo:root output for RocksDB integration, which
upstream lz4-sys now includes natively.

The old version bundled liblz4 1.8.3 vulnerable to integer overflow
during decompression (out-of-bounds write). Fixed in liblz4 1.9.4.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
