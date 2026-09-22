# [?] fix(rpc): getblock verbosity 2 side-chain panic (GHSA-x6v8-c2xp-928m) (#10889)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-02
Source: https://github.com/ZcashFoundation/zebra/commit/b5e122f5f9c0aa490a3d5f2e8e4000d2a6023d73
Type: security-commit

## Details
fix(rpc): getblock verbosity 2 side-chain panic (GHSA-x6v8-c2xp-928m) (#10889)

* test(rpc): add regression test for getblock side-chain panic (GHSA-x6v8-c2xp-928m)

* fix(rpc): use i64 for transaction confirmations to avoid side-chain panic (GHSA-x6v8-c2xp-928m)

* fix(rpc): resolve clippy and rustfmt warnings

Remove unused `mut` on mempool mock and apply rustfmt formatting.

---------

Co-authored-by: Alfredo Garcia <oxarbitrage@gmail.com>
