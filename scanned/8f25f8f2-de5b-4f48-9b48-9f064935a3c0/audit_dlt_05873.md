# [?] chore: Fix SQLX vulnerability (#2736)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-08-26
Source: https://github.com/matter-labs/zksync-era/commit/d8e43e77ed9bf91dde1cacdb1698afd366bb3c1a
Type: security-commit

## Details
chore: Fix SQLX vulnerability (#2736)

SQLX 0.8.0 had a vulnerability, which didn't affect us. At the time of
discovery, there was no fix. We silenced the warning to unlock
development.

This PR bumps SQLX to 0.8.1 which includes the vulnerability fix and
removes the cargo deny allowlist.

Co-authored-by: perekopskiy <53865202+perekopskiy@users.noreply.github.com>
