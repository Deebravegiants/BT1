# [?] test(sync): add failing regression test for GHSA-qhr3-cvch-5fh2 far-ahead block attribution

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/f844bbecbe360d3a49316ec5b8cba18cce63aa8d
Type: security-commit

## Details
test(sync): add failing regression test for GHSA-qhr3-cvch-5fh2 far-ahead block attribution

During integration with GHSA-g95h-hw6g-pvgv, preserve both sets of
regression tests and reuse the newer shared ChainSync test helper,
including its separate read-state service.

Conflicts:
    zebrad/src/components/sync/tests/vectors.rs
