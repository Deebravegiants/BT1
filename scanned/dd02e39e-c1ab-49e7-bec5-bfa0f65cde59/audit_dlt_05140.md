# [?] Fix race condition in async `UtxoFuture` resolution

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2026-01-28
Source: https://github.com/lightningdevkit/rust-lightning/commit/114f6b56864304cfeadc6f54fdc5abc2e8768d46
Type: security-commit

## Details
Fix race condition in async `UtxoFuture` resolution

Previously, we refactored the `GossipVerifier` to not require holding a
circular reference. As part of this, we moved to a model where the
`UtxoFuture`s are now polled by the background processor which checks
for completion through `get_and_clear_pending_msg_events`.

However, as part of this refactor we introduced race-condition: as we
only held `Weak` references in `PendingChecksContext` and the
`UtxoFuture` was directly dropped by the `GossipVerifier` after calling
`resolve`, the actual data was dropped with the future and gone when the
background processor attempted to retrieve and apply it via
`check_resolved_futures`.

Here, we fix this issue by simply holding on to the `state` `Arc`s in a
separate `pending_states` `Vec` that is only pruned in
`check_resolved_futures`, ensuring any completed results are collected
first.

Signed-off-by: Elias Rohrer <dev@tnull.de>
