# [?] apollo_l1_events: improve panic message in commit_txs for missing rejected tx (#14511)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-06-18
Source: https://github.com/starkware-libs/sequencer/commit/44d840f79fa17c0ca674fa83aea1962efc07c15a
Type: security-commit

## Details
apollo_l1_events: improve panic message in commit_txs for missing rejected tx (#14511)

Validators abort proposals via FailOnError when an L1 handler tx returns
NotFound, so a missing record at commit_txs time is a genuine invariant
violation. Clarify the panic message to explain why this is unreachable.

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### crates/apollo_l1_events/src/transaction_manager.rs
```diff
@@ -157,8 +157,10 @@ impl TransactionManager {
         }
         for &tx_hash in rejected_txs {
             self.with_record(tx_hash, |r| r.mark_rejected()).expect(
-                "Storage inconsistency: a transaction sent to the batcher was removed \
-                 unexpectedly.",
+                "Rejected L1 handler tx has no record. Unreachable: all L1 handler txs in a \
+                 committed block were validated as known (validation rejects unknown hashes), \
+                 sync commits with empty rejected_txs, and records are only removed via L1 \
+                 cancellation/consumption, which can't race a block.",
             );
         }
     }
```
