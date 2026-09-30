# [?] fix: fix for crash recovery (#7609)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-07-03
Source: https://github.com/iotaledger/iota/commit/653b2a2c0fcb9db598bc03afbf553cda54cc25cb
Type: security-commit

## Details
fix: fix for crash recovery (#7609)

# Description of change

This PR should fix the flaky/failing nightly simtest
test_simulated_load_restarts.
It is based on upstream https://github.com/MystenLabs/sui/pull/21929
Also, the function pub fn enqueue_transactions_for_execution is added in
authority.rs

## Links to any relevant issues

#7499

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

---------

Co-authored-by: muXxer <git@muxxer.de>

## Patch
### crates/iota-core/src/authority.rs
```diff
@@ -1175,6 +1175,14 @@ impl AuthorityState {
             .get_transaction_cache_reader()
             .get_executed_effects(tx_digest)?
         {
+            if let Some(expected_effects_digest) = expected_effects_digest {
+                assert_eq!(
+                    effects.digest(),
+                    expected_effects_digest,
+                    "Unexpected effects digest for transaction {:?}",
+                    tx_digest
+                );
+            }
             tx_guard.release();
             return Ok((effects, None));
         }
@@ -2964,6 +2972,16 @@ impl AuthorityState {
         &self.transaction_manager
     }
 
+    /// Adds transactions / certificates to transaction manager for ordered
+    /// execution.
+    pub fn enqueue_transactions_for_execution(
+        &self,
+        txns: Vec<VerifiedExecutableTransaction>,
+        epoch_store: &Arc<AuthorityPerEpochStore>,
+    ) {
+        self.transaction_manager.enqueue(txns, epoch_store)
+    }
+
     /// Adds certificates to transaction manager for ordered execution.
     pub fn enqueue_certificates_for_execution(
         &self,
```

### crates/iota-core/src/checkpoints/mod.rs
```diff
@@ -2333,10 +2333,16 @@ impl CheckpointService {
         tasks.spawn(monitored_future!(aggregator.run()));
 
         // If this times out, the validator may still start up. The worst that can
-        // happen is that we will crash later on (due to missing transactions).
-        if tokio::time::timeout(Duration::from_secs(10), self.wait_for_rebuilt_checkpoints())
-            .await
-            .is_err()
+        // happen is that we will crash later on instead of immediately. The eventual
+        // crash would occur because we may be missing transactions that are below the
+        // highest_synced_checkpoint watermark, which can cause a crash in
+        // `CheckpointExecutor::extract_randomness_rounds`.
+        if tokio::time::timeout(
+            Duration::from_secs(120),
+            self.wait_for_rebuilt_checkpoints(),
+        )
+        .await
+        .is_err()
         {
             debug_fatal!("Timed out waiting for checkpoints to be rebuilt");
         }
@@ -2347,7 +2353,11 @@ impl CheckpointService {
 
 impl CheckpointService {
     /// Waits until all checkpoints had been built before the node restarted
-    /// are rebuilt.
+    /// are rebuilt. This is required to preserve the invariant that all
+    /// checkpoints (and their transactions) below the
+    /// highest_synced_checkpoint watermark are available. Once the
+    /// checkpoints are constructed, we can be sure that the transactions
+    /// have also been executed.
     pub async fn wait_for_rebuilt_checkpoints(&self) {
         let highest_previously_built_seq = self.highest_previously_built_seq;
         let mut rx = self.highest_currently_built_seq_tx.subscribe();
```

### crates/iota-node/src/lib.rs
```diff
@@ -1530,65 +1530,112 @@ impl IotaNode {
         ))
     }
 
+    /// Re-executes pending consensus certificates, which may not have been
+    /// committed to disk before the node restarted. This is necessary for
+    /// the following reasons:
+    ///
+    /// 1. For any transaction for which we returned signed effects to a client,
+    ///    we must ensure that we have re-executed the transaction before we
+    ///    begin accepting grpc requests. Otherwise we would appear to have
+    ///    forgotten about the transaction.
+    /// 2. While this is running, we are concurrently waiting for all previously
+    ///    built checkpoints to be rebuilt. Since there may be dependencies in
+    ///    either direction (from checkpointed consensus transactions to pending
+    ///    consensus transactions, or vice versa), we must re-execute pending
+    ///    consensus transactions to ensure that both processes can complete.
+    /// 3. Also note that for any pending consensus transactions for which we
+    ///    wrote a signed effects digest to disk, we must re-execute using that
+    ///    digest as the expected effects digest, to ensure that we cannot
+    ///    arrive at different effects than what we previously signed.
     async fn reexecute_pending_consensus_certs(
         epoch_store: &Arc<AuthorityPerEpochStore>,
         state: &Arc<AuthorityState>,
     ) {
-        let pending_consensus_certificates = epoch_store
-            .get_all_pending_consensus_transactions()
-            .into_iter()
-            .filter_map(|tx| {
-                match tx.kind {
-                    // shared object txns will be re-executed by consensus replay
-                    ConsensusTransactionKind::CertifiedTransaction(tx)
-                        if !tx.contains_shared_object() =>
+        let mut pending_consensus_certificates = Vec::new();
+        let mut additional_certs = Vec::new();
+
+        for tx in epoch_store.get_all_pending_consensus_transactions() {
+            match tx.kind {
+                // Shared object txns cannot be re-executed at this point, because we must wait for
+                // consensus replay to assign shared object versions.
+                ConsensusTransactionKind::CertifiedTransaction(tx)
+                    if !tx.contains_shared_object() =>
+                {
+                    let tx = *tx;
+                    // new_unchecked is safe because we never submit a transaction to consensus
+                    // without verifying it
+                    let tx = VerifiedExecutableTransaction::new_from_certificate(
+                        VerifiedCertificate::new_unchecked(tx),
+                    );
+                    // we only need to re-execute if we previously signed the effects (which
+                    // indicates we returned the effects to a client).
+                    if let Some(fx_digest) = epoch_store
+                        .get_signed_effects_digest(tx.digest())
+                        .expect("db error")
                     {
-                        let tx = *tx;
-                        // we only need to re-execute if we previously signed the effects (which
-                        // indicates we returned the effects to a client).
-                        if let Some(fx_digest) = epoch_store
-                            .get_signed_effects_digest(tx.digest())
-                            .expect("db error")
-                        {
-                            // new_unchecked is safe because we never submit a transaction to
-                            // consensus without verifying it
-                            let tx = VerifiedExecutableTransaction::new_from_certificate(
-                                VerifiedCertificate::new_unchecked(tx),
-                            );
-                            Some((tx, fx_digest))
-                        } else {
-                            None
-                        }
+                        pending_consensus_certificates.push((tx, fx_digest));
+                    } else {
+                        additional_certs.push(tx);
                     }
-                    _ => None,
                 }
-            })
-            .collect::<Vec<_>>();
+                _ => (),
+            }
+        }
 
         let digests = pending_consensus_certificates
             .iter()
             .map(|(tx, _)| *tx.digest())
             .collect::<Vec<_>>();
 
-        info!("reexecuting pending consensus certificates: {:?}", digests);
+        info!(
+            "reexecuting {} pending consensus certificates: {:?}",
+            digests.len(),
+            digests
+        );
 
         state.enqueue_with_expected_effects_digest(pending_consensus_certificates, epoch_store);
+        state.enqueue_transactions_for_execution(additional_certs, epoch_store);
 
         // If this times out, the validator will still almost certainly start up fine.
         // But, it is possible that it may temporarily "forget" about
         // transactions that it had previously executed. This could confuse
         // clients in some circumstances. However, the transactions are still in
         // pending_consensus_certificates, so we cannot lose any finality guarantees.
+        let timeout = if cfg!(msim) { 120 } else { 60 };
         if tokio::time::timeout(
-            std::time::Duration::from_secs(10),
+            std::time::Duration::from_secs(timeout),
             state
                 .get_transaction_cache_reader()
                 .notify_read_executed_effects_digests(&digests),
         )
         .await
         .is_err()
         {
-            debug_fatal!("Timed out waiting for effects digests to be executed");
+            // Log all the digests that were not executed to help debugging.
+            if let Ok(executed_effects_digests) = state
+                .get_transaction_cache_reader()
+                .multi_get_executed_effects_digests(&digests)
+            {
+                let pending_digests = digests
+                    .iter()
+                    .zip(executed_effects_digests.iter())
+                    .filter_map(|(digest, executed_effects_digest)| {
+                        if executed_effects_digest.is_none() {
+                            Some(digest)
+                        } else {
+                            None
+                        }
+                    })
+                    .collect::<Vec<_>>();
+                debug_fatal!(
+                    "Timed out waiting for effects digests to be executed: {:?}",
+                    pending_digests
+                );
+            } else {
+                debug_fatal!(
+                    "Timed out waiting for effects digests to be executed, digests not found"
+                );
+            }
         }
     }
 
```
