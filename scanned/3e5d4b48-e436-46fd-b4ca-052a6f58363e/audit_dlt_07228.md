# [?] [consensus] fix deadlock during recovery (#24292)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-11-15
Source: https://github.com/MystenLabs/sui/commit/d04950c9ca4e0a4b51834a1b44d2593a0bc85203
Type: security-commit

## Details
[consensus] fix deadlock during recovery (#24292)

## Description 

https://github.com/MystenLabs/sui/pull/24024 introduced a potential
deadlock when recovering consensus. Possible sequence of events:

1. Thread A: acquires `dag_state` read lock for the duration of the
function call in
`recover_blocks_after_round(observer.dag_state.read().gc_round())`
2. Thread B: `CommitFinalizer::run()` tries to acquire the `dag_state`
write lock, and is blocked on the reader lock from (1)
3. Thread A: `recover_and_vote_on_blocks()` tries to acquire read lock
on `dag_state` again. This usually succeeds but in this case because of
(2), this is blocked, causing a deadlock.

Also:
- Run the last step of `TransactionCertifier` recovery in a blocking
thread.
- Improve logging.

## Test plan 

CI
The affected validator is fixed.

## Patch
### consensus/core/src/commit_observer.rs
```diff
@@ -77,9 +77,16 @@ impl CommitObserver {
         // Recover blocks needed for future commits (and block proposals).
         // Some blocks might have been recovered as committed blocks in recover_and_send_commits().
         // They will just be ignored.
-        observer
-            .transaction_certifier
-            .recover_blocks_after_round(observer.dag_state.read().gc_round());
+        tokio::runtime::Handle::current()
+            .spawn_blocking({
+                let transaction_certifier = observer.transaction_certifier.clone();
+                let gc_round = observer.dag_state.read().gc_round();
+                move || {
+                    transaction_certifier.recover_blocks_after_round(gc_round);
+                }
+            })
+            .await
+            .expect("Spawn blocking should not fail");
 
         observer
     }
```

### consensus/core/src/transaction_certifier.rs
```diff
@@ -100,7 +100,7 @@ impl TransactionCertifier {
                 .scan_blocks_by_author(authority_index, recovery_start_round)
                 .unwrap();
             info!(
-                "Recovering and voting on {} blocks for authority {} {}",
+                "Recovered and voting on {} blocks from authority {} {}",
                 blocks.len(),
                 authority_index,
                 context.committee.authority(authority_index).hostname
@@ -116,11 +116,21 @@ impl TransactionCertifier {
     /// Because own votes on blocks are not stored, input blocks are voted on if they can be
     /// included in a future proposed block.
     pub(crate) fn recover_and_vote_on_blocks(&self, blocks: Vec<VerifiedBlock>) {
-        let dag_state = self.dag_state.read();
+        let (gc_round, hard_linked) = {
+            let dag_state = self.dag_state.read();
+            (
+                dag_state.gc_round(),
+                blocks
+                    .iter()
+                    .map(|b| dag_state.is_hard_linked(&b.reference()))
+                    .collect::<Vec<_>>(),
+            )
+        };
         let voted_blocks = blocks
             .into_iter()
-            .map(|b| {
-                if b.round() <= dag_state.gc_round() || dag_state.is_hard_linked(&b.reference()) {
+            .zip(hard_linked)
+            .map(|(b, linked)| {
+                if b.round() <= gc_round || linked {
                     // Voting is unnecessary for blocks already included in own proposed blocks,
                     // or outside of local DAG GC bound.
                     (b, vec![])
```

### crates/sui-core/src/authority_server.rs
```diff
@@ -1441,7 +1441,7 @@ impl ValidatorService {
         Ok((tonic::Response::new(response), Weight::zero()))
     }
 
-    #[instrument(name= "ValidatorService::wait_for_effects_response", level = "error", skip_all, err(level = "debug"), fields(consensus_position = ?request.consensus_position, fast_path_effects = tracing::field::Empty))]
+    #[instrument(name= "ValidatorService::wait_for_effects_response", level = "error", skip_all, fields(consensus_position = ?request.consensus_position, fast_path_effects = tracing::field::Empty))]
     async fn wait_for_effects_response(
         &self,
         request: WaitForEffectsRequest,
```

### crates/sui-core/src/consensus_validator.rs
```diff
@@ -176,7 +176,7 @@ impl SuiTxValidator {
 
             let tx_digest = *tx.digest();
             if let Err(error) = self.vote_transaction(&epoch_store, tx) {
-                debug!(?tx_digest, "Transaction rejected during voting: {error}");
+                debug!(?tx_digest, "Voting to reject transaction: {error}");
                 self.metrics
                     .transaction_reject_votes
                     .with_label_values(&[error.to_variant_name()])
@@ -191,6 +191,8 @@ impl SuiTxValidator {
                     },
                     &error,
                 );
+            } else {
+                debug!(?tx_digest, "Voting to accept transaction");
             }
         }
 
```
