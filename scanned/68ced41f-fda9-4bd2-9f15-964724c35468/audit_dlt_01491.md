# [?] Fix race condition in integration test (#1564)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2020-10-15
Source: https://github.com/ACINQ/eclair/commit/bffb7a3fe1e5455c8075ce816e48fdb342f5bc3e
Type: security-commit

## Details
Fix race condition in integration test (#1564)

In the revoked commit tx case, both nodes are competing to claim the
HTLC outputs from the commit tx.

The test incorrectly assumed that node F would always win that race.
