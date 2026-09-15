# [?] fix(sync): guard waitForPeer() to fix retry deadlock(#10865)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-07-24
Source: https://github.com/besu-eth/besu/commit/7a49d77cd5b9938bf0907abd45b0761e7c93a3fc
Type: security-commit

## Details
fix(sync): guard waitForPeer() to fix retry deadlock(#10865)

- AbstractSyncTargetManager and PivotSyncActions call
  EthPeers.waitForPeer() with no timeout; it never wakes if the sole
  peer's request capacity is saturated and no new peer connects,
  permanently killing the sync retry loop.
- Add .orTimeout(5s) at both call sites, matching the existing guard
  in BackwardSyncAlgorithm.checkReadiness(). Add a regression test.
- CI: upload raw JUnit XML on acceptance-test failure too, not just
  the HTML report.

Fixes #10864

---------

Signed-off-by: Usman Saleem <usman@usmans.info>
