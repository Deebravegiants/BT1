# [?] fix(test): fix TestBlockPoolMaliciousNode DATA RACE (#4636)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-12-10
Source: https://github.com/cometbft/cometbft/commit/2b1db1c16bf2db16b81b49fef3581e79679fbed6
Type: security-commit

## Details
fix(test): fix TestBlockPoolMaliciousNode DATA RACE (#4636)

follow up to #4633 

See
https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504

<details>
<summary>DATA RACE</summary>

==================
WARNING: DATA RACE
Write at 0x00c00028f110 by goroutine 507:
  runtime.mapassign_faststr()
/opt/hostedtoolcache/go/1.23.1/x64/src/runtime/map_faststr.go:223 +0x0
  github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).banPeer()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:433
+0x16f

github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).RemovePeerAndRedoAllPeerRequests()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:266
+0x192

github.com/cometbft/cometbft/internal/blocksync.TestBlockPoolMaliciousNode.func4()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool_test.go:353
+0x1ee

Previous read at 0x00c00028f110 by goroutine 501:
  runtime.mapaccess1_faststr()
/opt/hostedtoolcache/go/1.23.1/x64/src/runtime/map_faststr.go:13 +0x0

github.com/cometbft/cometbft/internal/blocksync.(*BlockPool).isPeerBanned()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool.go:428
+0x128c

github.com/cometbft/cometbft/internal/blocksync.TestBlockPoolMaliciousNode()
/home/runner/work/cometbft/cometbft/internal/blocksync/pool_test.go:381
+0x1[20](https://github.com/cometbft/cometbft/actions/runs/12247740137/job/34188217504#step:6:21)5

_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/commit/2b1db1c16bf2db16b81b49fef3581e79679fbed6_
