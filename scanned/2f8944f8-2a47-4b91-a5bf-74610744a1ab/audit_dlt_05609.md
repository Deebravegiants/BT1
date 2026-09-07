# [?] fix(txpool): fix data race that broadcasts a null transaction (#12162)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-29
Source: https://github.com/NethermindEth/nethermind/commit/618af12a9a1542f980c2c509d7700a589a95f1c9
Type: security-commit

## Details
fix(txpool): fix data race that broadcasts a null transaction (#12162)

* fix(txpool): fix data race that broadcasts a null transaction

TxBroadcaster.BroadcastOnce locked on the _accumulatedTemporaryTxs
instance while TimerOnElapsed swapped that field by reference via
Interlocked.Exchange without taking the same lock. A monitor only
serialises sections that lock the same stable object, so the swap let
two threads hold monitors on two different ResettableList instances
while both Add()-ing to the same underlying List<T>. A concurrent Add
during a resize leaves a null hole in the list, which is later read
lazily through txs.Where(_gossipFilter) and dereferenced by
SpecDrivenTxGossipPolicy, throwing NullReferenceException in
CompositeTxGossipPolicy.ShouldGossipTransaction while gossiping to peers.

Use a dedicated, never-reassigned lock for both the append and the swap.
After the swap, BroadcastOnce only touches the new (empty) accumulator
while the timer exclusively owns the buffer being sent, so the two lists
are never mutated concurrently. The ResettableList reuse/swap design is
kept to avoid per-broadcast allocations during sync.

The pre-existing race surfaces as a fatal crash now only because
SpecDrivenTxGossipPolicy is the first gossip policy to dereference the
transaction; it was observed on gnosis+Flat sync where finalization-driven
background work shifts scheduling enough to hit the window.

Adds a concurrency regression test that drives BroadcastOnce against
repeated timer swaps and asserts no null reaches the peer (and that every
transaction is sent exactly once). The test fails reliably on the old
code and passes on the fix.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* refactor(txpool): address review feedback

- Remove the two comments @asdacap flagged as unnecessary (the XML doc on
  _accumulatedTxsLock and the inline comment in NotifyPeers).
- Yield in the regression test's ticker loop so it no longer busy-spins a

_Trimmed to 38 lines — full report: https://github.com/NethermindEth/nethermind/commit/618af12a9a1542f980c2c509d7700a589a95f1c9_
