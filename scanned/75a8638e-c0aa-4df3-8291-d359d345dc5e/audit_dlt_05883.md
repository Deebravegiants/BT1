# [?] fixes state panic ofter trusted reorg (#989)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygonHermez/zkevm-node
Published: 2022-08-03
Source: https://github.com/0xPolygon/zkevm-node/commit/b734d9f11b28ccb1b5bcb153fed78c62cb4ff0ff
Type: security-commit

## Details
fixes state panic ofter trusted reorg (#989)

* fixes

1- decode signature was no needed.
2-synchronizer and sequencer must be running in the same docker instance to avoid problems with the channel.
3-fix in the cli components option

* log

* undo. Sequencer and synchronizer running in different docker instances
