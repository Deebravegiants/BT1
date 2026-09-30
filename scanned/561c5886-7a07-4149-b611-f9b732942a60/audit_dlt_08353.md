# [?] Fixes for crash recovery (#21929)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-10
Source: https://github.com/MystenLabs/sui/commit/68113e14ae371146856a01614c89cf30e3ee0589
Type: security-commit

## Details
Fixes for crash recovery (#21929)

- Fix `reexecute_pending_consensus_transactions`
- Address comment TODOs

## Patch
### crates/sui-core/src/authority.rs
```diff
@@ -1263,6 +1263,14 @@ impl AuthorityState {
             .get_transaction_cache_reader()
             .get_executed_effects(tx_digest)
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
```

### crates/sui-core/src/checkpoints/mod.rs
```diff
@@ -2652,8 +2652,10 @@ impl CheckpointService {
         tasks.spawn(monitored_future!(accumulator.run()));
 
         // If this times out, the validator may still start up. The worst that can
-        // happen is that we will crash later on (due to missing transactions).
-        // TODO: Explain why it will crash later on.
+        // happen is that we will crash later on instead of immediately. The eventual
+        // crash would occur because we may be missing transactions that are below the
+        // highest_synced_checkpoint watermark, which can cause a crash in
+        // `CheckpointExecutor::extract_randomness_rounds`.
         if tokio::time::timeout(
             Duration::from_secs(120),
             self.wait_for_rebuilt_checkpoints(),
@@ -2670,8 +2672,10 @@ impl CheckpointService {
 
 impl CheckpointService {
     /// Waits until all checkpoints had been built before the node restarted
-    /// are rebuilt.
-    /// TODO: Add comments explain why we need to wait for checkpoints to be rebuilt.
+    /// are rebuilt. This is required to preserve the invariant that all checkpoints
+    /// (and their transactions) below the highest_synced_checkpoint watermark are
+    /// available. Once the checkpoints are constructed, we can be sure that the
+    /// transactions have also been executed.
     pub async fn wait_for_rebuilt_checkpoints(&self) {
         let highest_previously_built_seq = self.highest_previously_built_seq;
         let mut rx = self.highest_currently_built_seq_tx.subscribe();
```

### crates/sui-node/src/lib.rs
```diff
@@ -13,6 +13,7 @@ use arc_swap::ArcSwap;
 use fastcrypto_zkp::bn254::zk_login::JwkId;
 use fastcrypto_zkp::bn254::zk_login::OIDCProvider;
 use futures::future::BoxFuture;
+use mysten_common::debug_fatal;
 use mysten_network::server::SUI_TLS_SERVER_NAME;
 use prometheus::Registry;
 use std::collections::{BTreeSet, HashMap, HashSet};
@@ -47,6 +48,7 @@ use sui_rpc_api::ServerVersion;
 use sui_types::base_types::ConciseableName;
 use sui_types::crypto::RandomnessRound;
 use sui_types::digests::ChainIdentifier;
+use sui_types::executable_transaction::VerifiedExecutableTransaction;
 use sui_types::full_checkpoint_content::CheckpointData;
 use sui_types::messages_consensus::AuthorityCapabilitiesV2;
 use sui_types::messages_consensus::ConsensusTransactionKind;
@@ -838,22 +840,24 @@ impl SuiNode {
             .set(config.supported_protocol_versions.unwrap().max.as_u64() as i64);
 
         let validator_components = if state.is_validator(&epoch_store) {
-            Self::reenqueue_pending_consensus_certs(&epoch_store, &state).await;
-            let mut components = Self::construct_validator_components(
-                config.clone(),
-                state.clone(),
-                committee,
-                epoch_store.clone(),
-                checkpoint_store.clone(),
-                state_sync_handle.clone(),
-                randomness_handle.clone(),
-                Arc::downgrade(&accumulator),
-                backpressure_manager.clone(),
-                connection_monitor_status.clone(),
-                &registry_service,
-                sui_node_metrics.clone(),
-            )
-            .await?;
+            let (components, _) = futures::join!(
+                Self::construct_validator_components(
+                    config.clone(),
+                    state.clone(),
+                    committee,
+                    epoch_store.clone(),
+                    checkpoint_store.clone(),
+                    state_sync_handle.clone(),
+                    randomness_handle.clone(),
+                    Arc::downgrade(&accumulator),
+                    backpressure_manager.clone(),
+                    connection_monitor_status.clone(),
+                    &registry_service,
+                    sui_node_metrics.clone(),
+                ),
+                Self::reexecute_pending_consensus_certs(&epoch_store, &state,)
+            );
+            let mut components = components?;
 
             components.consensus_adapter.submit_recovered(&epoch_store);
 
@@ -1545,41 +1549,102 @@ impl SuiNode {
         }))
     }
 
-    /// Re-enqueue pending consensus certificates for execution.
-    // TODO: Add comments explain why we need to do this at start up.
-    async fn reenqueue_pending_consensus_certs(
+    /// Re-executes pending consensus certificates, which may not have been committed to disk
+    /// before the node restarted. This is necessary for the following reasons:
+    ///
+    /// 1. For any transaction for which we returned signed effects to a client, we must ensure
+    ///    that we have re-executed the transaction before we begin accepting grpc requests.
+    ///    Otherwise we would appear to have forgotten about the transaction.
+    /// 2. While this is running, we are concurrently waiting for all previously built checkpoints
+    ///    to be rebuilt. Since there may be dependencies in either direction (from checkpointed
+    ///    consensus transactions to pending consensus transactions, or vice versa), we must
+    ///    re-execute pending consensus transactions to ensure that both processes can complete.
+    /// 3. Also note that for any pending consensus transactions for which we wrote a signed effects
+    ///    digest to disk, we must re-execute using that digest as the expected effects digest,
+    ///    to ensure that we cannot arrive at different effects than what we previously signed.
+    async fn reexecute_pending_consensus_certs(
         epoch_store: &Arc<AuthorityPerEpochStore>,
         state: &Arc<AuthorityState>,
     ) {
-        let pending_consensus_certificates = epoch_store
-            .get_all_pending_consensus_transactions()
-            .into_iter()
-            .filter_map(|tx| match tx.kind {
-                ConsensusTransactionKind::CertifiedTransaction(tx) => {
-                    if tx.contains_shared_object() {
-                        // We cannot schedule shared object transactions for execution here
-                        // because they must come out of consensus to get prover version assignment.
-                        None
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
+                    // we only need to re-execute if we previously signed the effects (which indicates we
+                    // returned the effects to a client).
+                    if let Some(fx_digest) = epoch_store
+                        .get_signed_effects_digest(tx.digest())
+                        .expect("db error")
+                    {
+                        pending_consensus_certificates.push((tx, fx_digest));
                     } else {
-                        Some(VerifiedCertificate::new_unchecked(*tx))
+                        additional_certs.push(tx);
                     }
                 }
-                _ => None,
-            })
-            .collect::<Vec<_>>();
+                _ => (),
+            }
+        }
 
         let digests = pending_consensus_certificates
             .iter()
-            .map(|tx| *tx.digest())
+            .map(|(tx, _)| *tx.digest())
             .collect::<Vec<_>>();
 
         info!(
-            "re-enqueueing {} pending consensus certificates for execution: {:?}",
+            "reexecuting {} pending consensus certificates: {:?}",
             digests.len(),
             digests
         );
 
-        state.enqueue_certificates_for_execution(pending_consensus_certificates, epoch_store);
+        state.enqueue_with_expected_effects_digest(pending_consensus_certificates, epoch_store);
+        state.enqueue_transactions_for_execution(additional_certs, epoch_store);
+
+        // If this times out, the validator will still almost certainly start up fine. But, it is
+        // possible that it may temporarily "forget" about transactions that it had previously
+        // executed. This could confuse clients in some circumstances. However, the transactions
+        // are still in pending_consensus_certificates, so we cannot lose any finality guarantees.
+        let timeout = if cfg!(msim) { 120 } else { 60 };
+        if tokio::time::timeout(
+            std::time::Duration::from_secs(timeout),
+            state
+                .get_transaction_cache_reader()
+                .notify_read_executed_effects_digests(&digests),
+        )
+        .await
+        .is_err()
+        {
+            // Log all the digests that were not executed to help debugging.
+            let executed_effects_digests = state
+                .get_transaction_cache_reader()
+                .multi_get_executed_effects_digests(&digests);
+            let pending_digests = digests
+                .iter()
+                .zip(executed_effects_digests.iter())
+                .filter_map(|(digest, executed_effects_digest)| {
+                    if executed_effects_digest.is_none() {
+                        Some(digest)
+                    } else {
+                        None
+                    }
+                })
+                .collect::<Vec<_>>();
+            debug_fatal!(
+                "Timed out waiting for effects digests to be executed: {:?}",
+                pending_digests
+            );
+        }
     }
 
     pub fn state(&self) -> Arc<AuthorityState> {
```
