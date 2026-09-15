# [?] fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/324dea07dd48e278d32f06c8cb8f52dac43b6b38
Type: security-commit

## Details
fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

During integration with GHSA-g95h-hw6g-pvgv, preserve the explicit
behind-tip scoring arm while leaving above-lookahead responses
deliberately unscored. Retain both security changelog entries.

Conflicts:
    CHANGELOG.md
    zebrad/src/components/sync.rs
