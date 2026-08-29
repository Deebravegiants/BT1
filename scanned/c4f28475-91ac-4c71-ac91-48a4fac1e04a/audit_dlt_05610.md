# [?] fix(flatdb): make snap finalize crash-durable and the restart wipe cheap (#11997)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-16
Source: https://github.com/NethermindEth/nethermind/commit/92b96a067b9dbbd6cf262b7d82db37f1e7b058c7
Type: security-commit

## Details
fix(flatdb): make snap finalize crash-durable and the restart wipe cheap (#11997)

* fix(flatdb): make snap finalize crash-durable and the restart wipe bounded

Two distinct restart-during-snap failures on FlatDb:

- #11457: FinalizeSync advanced the WAL-durable CurrentState pointer before
  flushing the snap/heal data (written with DisableWAL). An unclean shutdown in
  that window left the pointer ahead of still-unflushed data, so a state with
  holes was served as complete -> "transaction nonce is too high" on the first
  post-pivot block -> the canonical chain was deleted as "invalid" and sync got
  permanently stuck. Flush all data before advancing the pointer so the pointer
  is never durable ahead of the state it references.

- #11442: ClearAllColumns collected every key into a single write batch, holding
  them all in memory at once and exhausting memory when wiping a large,
  partially-synced DB on restart (a fresh sync starts empty, so there is nothing
  to clear -> flat RSS). It now streams keys and point-deletes them in bounded
  batches, committing periodically. The Metadata format markers are preserved
  (only CurrentState is reset, cf. #11996). Kept entirely within the FlatDb
  persistence layer; no core DB changes.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* chore(flatdb): trim comments and harden the clear batch loop

Address review feedback:
- Trim the verbose comments flagged by @LukaszRozmej.
- Create the next write batch before disposing the current one so a throw from
  StartWriteBatch can't lead to a double dispose in the finally block.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
