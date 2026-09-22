# [?] qa: Add regression test for GHSA-78pp-mc9g-g4mw

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-30
Source: https://github.com/zcash/zcash/commit/d6ee9a48379bcc1289302df69cb041b118b7d923
Type: security-commit

## Details
qa: Add regression test for GHSA-78pp-mc9g-g4mw

Send a block whose aggregate Sapling pool-value delta is out of range and
assert that the sending peer is disconnected (DoS 100) and the block is
rejected with `bad-blk-pool-value-out-of-range`, rather than being left
header-only for the peer to replay and re-write to disk indefinitely.

The block carries two v5 transactions whose negated valueBalanceSapling
values each pass CheckTransaction but together overflow MoneyDeltaRange in
ComputePoolDeltas, so the failure surfaces in ReceivedBlockTransactions
before ConnectBlock is reached. A comment records why the descendant
AccumulateChainPoolValues path has no observable pre/post-fix difference
and so is not exercised.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
