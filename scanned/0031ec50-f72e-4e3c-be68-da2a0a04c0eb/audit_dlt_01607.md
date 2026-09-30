# [?] [mfp] Enable DoS protection for MFP submitted user tx (#23334)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-09-11
Source: https://github.com/MystenLabs/sui/commit/606de5ea650f7f02a265b98329c48f5935c35725
Type: security-commit

## Details
[mfp] Enable DoS protection for MFP submitted user tx (#23334)

## Description 

Implements a submitted transaction cache to prevent DoS attacks through
excessive transaction resubmissions. The cache tracks all transactions
submitted to consensus and applies spam weights to clients that exceed
submission limits, integrating with the existing traffic controller for
throttling.

Submitted Transaction Cache (submitted_transaction_cache.rs)
- Tracks all transactions submitted through mfp
- Gas-price-based amplification factor allowing higher gas transactions
more resubmissions
- Allow for additional retry tolerance on top of amplification factor
- Round-based garbage collection following existing consensus cache
patterns
- Tracks submitter client IP for traffic attribution

Traffic Controller Integration
- ConsensusHandler increments submission count when seeing transactions
in consensus output
- Calculates spam weight using a simple Weight::one() for all excess
transaction resubmissions
- Applies spam weight to the original submitter's IP address via traffic
controller tally

## Test plan 

pending ptn tests

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

### crates/sui-core/src/authority.rs
```diff
@@ -244,6 +244,7 @@ pub mod epoch_start_configuration;
 pub mod execution_time_estimator;
 pub mod shared_object_congestion_tracker;
 pub mod shared_object_version_manager;
+pub mod submitted_transaction_cache;
 pub mod test_authority_builder;
 pub mod transaction_deferral;
 pub mod transaction_reject_reason_cache;
```

### crates/sui-core/src/authority/authority_per_epoch_store.rs
```diff
@@ -92,6 +92,9 @@ use super::shared_object_congestion_tracker::{
     CongestionPerObjectDebt, SharedObjectCongestionTracker,
 };
 use super::shared_object_version_manager::AssignedVersions;
+use super::submitted_transaction_cache::{
+    SubmittedTransactionCache, SubmittedTransactionCacheMetrics,
+};
 use super::transaction_deferral::{transaction_deferral_within_limit, DeferralKey, DeferralReason};
 use super::transaction_reject_reason_cache::TransactionRejectReasonCache;
 use crate::authority::epoch_start_configuration::EpochStartConfiguration;
@@ -424,6 +427,9 @@ pub struct AuthorityPerEpochStore {
     /// A cache that maintains the reject vote reason for a transaction.
     pub(crate) tx_reject_reason_cache: Option<TransactionRejectReasonCache>,
 
+    /// A cache that tracks submitted transactions to prevent DoS through excessive resubmissions.
+    pub(crate) submitted_transaction_cache: SubmittedTransactionCache,
+
     /// Waiters for settlement transactions. Used by execution scheduler to wait for
     /// settlement transaction keys to resolve to transactions.
     /// Stored in AuthorityPerEpochStore so that it is automatically cleaned up at the end of the epoch.
@@ -968,6 +974,7 @@ impl AuthorityPerEpochStore {
         expensive_safety_check_config: &ExpensiveSafetyCheckConfig,
         chain: (ChainIdentifier, Chain),
         highest_executed_checkpoint: CheckpointSequenceNumber,
+        submitted_transaction_cache_metrics: Arc<SubmittedTransactionCacheMetrics>,
     ) -> SuiResult<Arc<Self>> {
         let current_time = Instant::now();
         let epoch_id = committee.epoch;
@@ -1130,6 +1137,9 @@ impl AuthorityPerEpochStore {
             None
         };
 
+        let submitted_transaction_cache =
+            SubmittedTransactionCache::new(None, submitted_transaction_cache_metrics);
+
         let s = Arc::new(Self {
             name,
             committee: committee.clone(),
@@ -1171,6 +1181,7 @@ impl AuthorityPerEpochStore {
             end_of_epoch_execution_time_observations: OnceCell::new(),
             consensus_tx_status_cache,
             tx_reject_reason_cache,
+            submitted_transaction_cache,
             settlement_registrations: Default::default(),
         });
 
@@ -1324,6 +1335,7 @@ impl AuthorityPerEpochStore {
             expensive_safety_check_config,
             self.chain,
             previous_epoch_last_checkpoint,
+            self.submitted_transaction_cache.metrics(),
         )
     }
 
```

### crates/sui-core/src/authority/submitted_transaction_cache.rs
```diff
@@ -0,0 +1,405 @@
+// Copyright (c) Mysten Labs, Inc.
+// SPDX-License-Identifier: Apache-2.0
+
+use lru::LruCache;
+use parking_lot::RwLock;
+use prometheus::{
+    register_histogram_with_registry, register_int_counter_with_registry,
+    register_int_gauge_with_registry, Histogram, IntCounter, IntGauge, Registry,
+};
+use std::collections::BTreeSet;
+use std::net::IpAddr;
+use std::num::NonZeroUsize;
+use std::sync::Arc;
+use sui_types::digests::TransactionDigest;
+use sui_types::traffic_control::Weight;
+use tracing::debug;
+
+pub(crate) const DEFAULT_CACHE_CAPACITY: usize = 100_000;
+
+pub struct SubmittedTransactionCacheMetrics {
+    pub transactions_tracked: IntGauge,
+    pub spam_detected: IntCounter,
+    pub submission_count_exceeded: Histogram,
+    pub amplification_factor_distribution: Histogram,
+}
+
+impl SubmittedTransactionCacheMetrics {
+    pub fn new(registry: &Registry) -> Self {
+        Self {
+            transactions_tracked: register_int_gauge_with_registry!(
+                "submitted_transaction_cache_transactions_tracked",
+                "Number of transactions currently tracked in the submission cache",
+                registry,
+            )
+            .unwrap(),
+            spam_detected: register_int_counter_with_registry!(
+                "submitted_transaction_cache_spam_detected",
+                "Number of transactions that exceeded submission limits",
+                registry,
+            )
+            .unwrap(),
+            submission_count_exceeded: register_histogram_with_registry!(
+                "submitted_transaction_cache_submission_count_exceeded",
+                "Distribution of submission counts when spam is detected",
+                vec![
+                    1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0,
+                    10000.0,
+                ],
+                registry,
+            )
+            .unwrap(),
+            amplification_factor_distribution: register_histogram_with_registry!(
+                "submitted_transaction_cache_amplification_factor_distribution",
+                "Distribution of amplification factors used for transaction submissions",
+                vec![
+                    1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0,
+                    10000.0,
+                ],
+                registry,
+            )
+            .unwrap(),
+        }
+    }
+
+    #[cfg(test)]
+    pub(crate) fn new_test() -> Self {
+        Self::new(&Registry::new())
+    }
+}
+
+/// Cache for tracking submitted transactions to prevent DoS through excessive resubmissions.
+/// Uses LRU eviction to automatically remove least recently used entries when at capacity.
+/// Tracks submission counts and enforces gas-price-based amplification limits.
+pub(crate) struct SubmittedTransactionCache {
+    inner: RwLock<Inner>,
+    metrics: Arc<SubmittedTransactionCacheMetrics>,
+}
+
+struct Inner {
+    transactions: LruCache<TransactionDigest, SubmissionMetadata>,
+}
+
+#[derive(Debug, Clone)]
+struct SubmissionMetadata {
+    /// Number of times this transaction has been submitted
+    submission_count: u32,
+    /// Maximum allowed submissions based on gas price amplification
+    max_allowed_submissions: u32,
+    /// Set of client IP addresses that have submitted this transaction
+    submitter_client_addrs: BTreeSet<IpAddr>,
+}
+
+impl SubmittedTransactionCache {
+    pub(crate) fn new(
+        cache_capacity: Option<usize>,
+        metrics: Arc<SubmittedTransactionCacheMetrics>,
+    ) -> Self {
+        let capacity = cache_capacity
+            .and_then(NonZeroUsize::new)
+            .unwrap_or_else(|| NonZeroUsize::new(DEFAULT_CACHE_CAPACITY).unwrap());
+
+        Self {
+            inner: RwLock::new(Inner {
+                transactions: LruCache::new(capacity),
+            }),
+            metrics,
+        }
+    }
+
+    pub(crate) fn metrics(&self) -> Arc<SubmittedTransactionCacheMetrics> {
+        self.metrics.clone()
+    }
+
+    pub(crate) fn record_submitted_tx(
+        &self,
+        digest: &TransactionDigest,
+        amplification_factor: u32,
+        submitter_client_addr: Option<IpAddr>,
+    ) {
+        let mut inner = self.inner.write();
+
+        let max_allowed_submissions = amplification_factor;
+
+        if let Some(metadata) = inner.transactions.get_mut(digest) {
+            // Track additional client addresses for resubmissions
+            if let Some(addr) = submitter_client_addr {
+                if metadata.submitter_client_addrs.insert(addr) {
+                    debug!("Added new client address {addr} for transaction {digest}");
+                }
+            }
+            debug!("Transaction {digest} already tracked in submission cache");
+        } else {
+            // First time we're submitting this transaction, however we will wait till
+            // we see the transaction in consensus output to increment the submission count.
+            let submitter_client_addrs = submitter_client_addr.into_iter().collect();
+            let metadata = SubmissionMetadata {
+                submission_count: 0,
+                max_allowed_submissions,
+                submitter_client_addrs,
+            };
+
+            inner.transactions.put(*digest, metadata);
+
+            self.metrics
+                .transactions_tracked
+                .set(inner.transactions.len() as i64);
+            self.metrics
+                .amplification_factor_distribution
+                .observe(amplification_factor as f64);
+
+            debug!(
+                "First submission of transaction {digest} (max_allowed: {max_allowed_submissions})",
+            );
+        }
+    }
+
+    /// Increments the submission count when we see a transaction in consensus output.
+    /// This tracks how many times the transaction has appeared in consensus (from any validator).
+    /// Returns the spam weight and set of submitter client addresses if the transaction exceeds allowed submissions.
+    pub(crate) fn increment_submission_count(
+        &self,
+        digest: &TransactionDigest,
+    ) -> Option<(Weight, BTreeSet<IpAddr>)> {
+        let mut inner = self.inner.write();
+
+        if let Some(metadata) = inner.transactions.get_mut(digest) {
+            metadata.submission_count += 1;
+
+            if metadata.submission_count > metadata.max_allowed_submissions {
+                let spam_weight = Weight::one();
+                self.metrics.spam_detected.inc();
+                self.metrics
+                    .submission_count_exceeded
+                    .observe(metadata.submission_count as f64);
+
+                debug!(
+                    "Transaction {} seen in consensus {} times, exceeds limit {} (spam_weight: {:?})",
+                    digest,
+                    metadata.submission_count,
+                    metadata.max_allowed_submissions,
+                    spam_weight
+                );
+
+                return Some((spam_weight, metadata.submitter_client_addrs.clone()));
+            }
+        }
+        // If we don't know about this transaction, it was submitted by another validator
+        // We don't track spam weight for transactions we didn't submit
+        None
+    }
+
+    #[cfg(test)]
+    pub(crate) fn contains(&self, digest: &TransactionDigest) -> bool {
+        self.inner.read().transactions.contains(digest)
+    }
+
+    #[cfg(test)]
+    pub(crate) fn get_submission_count(&self, digest: &TransactionDigest) -> Option<u32> {
+        self.inner
+            .read()
+            .transactions
+            .peek(digest)
+            .map(|m| m.submission_count)
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use std::net::{IpAddr, Ipv4Addr};
+
+    fn create_test_digest(val: u8) -> TransactionDigest {
+        let mut bytes = [0u8; 32];
+        bytes[0] = val;
+        TransactionDigest::new(bytes)
+    }
+
+    #[test]
+    fn test_first_submission_allowed() {
+        let cache = SubmittedTransactionCache::new(
+            None,
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+        let digest = create_test_digest(1);
+
+        cache.record_submitted_tx(&digest, 1, None);
+        assert!(cache.contains(&digest));
+        assert_eq!(cache.get_submission_count(&digest), Some(0));
+
+        let spam_weight = cache.increment_submission_count(&digest);
+        assert_eq!(spam_weight, None);
+        assert_eq!(cache.get_submission_count(&digest), Some(1));
+    }
+
+    #[test]
+    fn test_amplification_factor() {
+        let cache = SubmittedTransactionCache::new(
+            None,
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+        let digest = create_test_digest(1);
+
+        // Record with amplification_factor=5, should allow 5 submissions
+        cache.record_submitted_tx(&digest, 5, None);
+
+        // Should allow 5 submissions
+        for i in 0..5 {
+            let spam_weight = cache.increment_submission_count(&digest);
+            assert_eq!(spam_weight, None, "Submission {} should be allowed", i + 1);
+        }
+
+        // 6th submission should trigger spam weight
+        let spam_weight = cache.increment_submission_count(&digest);
+        assert_eq!(spam_weight.map(|(w, _)| w), Some(Weight::one()));
+
+        // Additional submissions should also trigger spam weight
+        for i in 6..10 {
+            let spam_weight = cache.increment_submission_count(&digest);
+            assert_eq!(
+                spam_weight.map(|(w, _)| w),
+                Some(Weight::one()),
+                "Submission {} should trigger spam weight",
+                i + 1
+            );
+        }
+    }
+
+    #[test]
+    fn test_lru_eviction() {
+        // Create a cache with capacity for only 3 transactions
+        let cache = SubmittedTransactionCache::new(
+            Some(3),
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+
+        // Add 3 transactions
+        for i in 1..=3 {
+            let digest = create_test_digest(i);
+            cache.record_submitted_tx(&digest, 1, None);
+        }
+
+        // Verify all 3 transactions are in cache
+        for i in 1..=3 {
+            let digest = create_test_digest(i);
+            assert!(cache.contains(&digest));
+        }
+
+        // Add a 4th transaction, which should evict the least recently used (digest 1)
+        let digest4 = create_test_digest(4);
+        cache.record_submitted_tx(&digest4, 1, None);
+
+        // Transaction 1 should be evicted (least recently used)
+        assert!(!cache.contains(&create_test_digest(1)));
+        // Transactions 2, 3, and 4 should still be in cache
+        assert!(cache.contains(&create_test_digest(2)));
+        assert!(cache.contains(&create_test_digest(3)));
+        assert!(cache.contains(&digest4));
+    }
+
+    #[test]
+    fn test_lru_access_updates_position() {
+        // Create a cache with capacity for only 3 transactions
+        let cache = SubmittedTransactionCache::new(
+            Some(3),
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+
+        // Add 3 transactions
+        for i in 1..=3 {
+            let digest = create_test_digest(i);
+            cache.record_submitted_tx(&digest, 1, None);
+        }
+
+        // Access transaction 1 (moves it to front of LRU)
+        let digest1 = create_test_digest(1);
+        cache.increment_submission_count(&digest1);
+
+        // Add a 4th transaction, which should now evict transaction 2 (now least recently used)
+        let digest4 = create_test_digest(4);
+        cache.record_submitted_tx(&digest4, 1, None);
+
+        // Transaction 2 should be evicted
+        assert!(!cache.contains(&create_test_digest(2)));
+        // Transactions 1, 3, and 4 should still be in cache
+        assert!(cache.contains(&digest1));
+        assert!(cache.contains(&create_test_digest(3)));
+        assert!(cache.contains(&digest4));
+    }
+
+    #[test]
+    fn test_multiple_client_addresses() {
+        let cache = SubmittedTransactionCache::new(
+            None,
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+        let digest = create_test_digest(1);
+        let addr1 = IpAddr::V4(Ipv4Addr::new(127, 0, 0, 1));
+        let addr2 = IpAddr::V4(Ipv4Addr::new(127, 0, 0, 2));
+        let addr3 = IpAddr::V4(Ipv4Addr::new(127, 0, 0, 3));
+
+        // First submission with addr1
+        cache.record_submitted_tx(&digest, 2, Some(addr1));
+
+        // Resubmission with addr2 - should track both addresses
+        cache.record_submitted_tx(&digest, 2, Some(addr2));
+
+        // Resubmission with addr1 again - should not duplicate
+        cache.record_submitted_tx(&digest, 2, Some(addr1));
+
+        // Resubmission with addr3 - should track all three
+        cache.record_submitted_tx(&digest, 2, Some(addr3));
+
+        // Increment submission count twice to exceed limit
+        cache.increment_submission_count(&digest);
+        cache.increment_submission_count(&digest);
+
+        // Third submission should trigger spam weight for all addresses
+        let result = cache.increment_submission_count(&digest);
+        assert!(result.is_some());
+
+        let (spam_weight, addrs) = result.unwrap();
+        assert_eq!(spam_weight, Weight::one());
+        assert_eq!(addrs.len(), 3);
+        assert!(addrs.contains(&addr1));
+        assert!(addrs.contains(&addr2));
+        assert!(addrs.contains(&addr3));
+    }
+
+    #[test]
+    fn test_retry_tracking() {
+        // Create a cache with capacity for only 3 transactions
+        let cache = SubmittedTransactionCache::new(
+            Some(3),
+            Arc::new(SubmittedTransactionCacheMetrics::new_test()),
+        );
+        let digest1 = create_test_digest(1);
+        let digest2 = create_test_digest(2);
+        let digest3 = create_test_digest(3);
+        let digest4 = create_test_digest(4);
+
+        // Add 3 transactions
+        cache.record_submitted_tx(&digest1, 1, None);
+        cache.record_submitted_tx(&digest2, 1, None);
+        cache.record_submitted_tx(&digest3, 1, None);
+
+        // Verify all 3 transactions are in cache
+        assert!(cache.contains(&digest1));
+        assert!(cache.contains(&digest2));
+        assert!(cache.contains(&digest3));
+
+        // Retry digest1 - this should move it to the front of LRU
+        cache.record_submitted_tx(&digest1, 1, None);
+
+        // Add a 4th transaction, which should evict the least recently used (digest2)
+        cache.record_submitted_tx(&digest4, 1, None);
+
+        // digest1 should still be in cache (moved to front by retry)
+        assert!(cache.contains(&digest1));
+        // digest2 should be evicted (was least recently used)
+        assert!(!cache.contains(&digest2));
+        // digest3 and digest4 should still be in cache
+        assert!(cache.contains(&digest3));
+        assert!(cache.contains(&digest4));
+    }
+}
```

### crates/sui-core/src/authority/test_authority_builder.rs
```diff
@@ -10,6 +10,7 @@ use crate::authority::authority_store_tables::{
     AuthorityPerpetualTables, AuthorityPerpetualTablesOptions, AuthorityPrunerTables,
 };
 use crate::authority::epoch_start_configuration::EpochStartConfiguration;
+use crate::authority::submitted_transaction_cache::SubmittedTransactionCacheMetrics;
 use crate::authority::{AuthorityState, AuthorityStore};
 use crate::checkpoints::CheckpointStore;
 use crate::epoch::committee_store::CommitteeStore;
@@ -290,6 +291,7 @@ impl<'a> TestAuthorityBuilder<'a> {
                 .get_highest_executed_checkpoint_seq_number()
                 .unwrap()
                 .unwrap_or(0),
+            Arc::new(SubmittedTransactionCacheMetrics::new(&registry)),
         )
         .expect("failed to create authority per epoch store");
         let committee_store = Arc::new(CommitteeStore::new(
```

### crates/sui-core/src/authority_server.rs
```diff
@@ -559,8 +559,15 @@ impl ValidatorService {
             consensus_adapter,
             metrics,
             traffic_controller: _,
-            client_id_source: _,
+            client_id_source,
         } = self.clone();
+
+        let submitter_client_addr = if let Some(client_id_source) = &client_id_source {
+            self.get_client_ip_addr(&request, client_id_source)
+        } else {
+            self.get_client_ip_addr(&request, &ClientIdSource::SocketAddr)
+        };
+
         let epoch_store = state.load_epoch_store_one_call_per_task();
         if !epoch_store.protocol_config().mysticeti_fastpath() {
             return Err(SuiError::UnsupportedFeatureError {
@@ -813,11 +820,16 @@ impl ValidatorService {
             self.handle_submit_to_consensus_for_position(
                 NonEmpty::from_vec(consensus_transactions).unwrap(),
                 &epoch_store,
+                submitter_client_addr,
             )
             .await?
         } else {
             let futures = consensus_transactions.into_iter().map(|t| {
-                self.handle_submit_to_consensus_for_position(NonEmpty::new(t), &epoch_store)
+                self.handle_submit_to_consensus_for_position(
+                    NonEmpty::new(t),
+                    &epoch_store,
+                    submitter_client_addr,
+                )
             });
             future::try_join_all(futures)
                 .await?
@@ -1016,6 +1028,7 @@ impl ValidatorService {
         &self,
         consensus_transactions: NonEmpty<ConsensusTransaction>,
         epoch_store: &Arc<AuthorityPerEpochStore>,
+        submitter_client_addr: Option<IpAddr>,
     ) -> Result<Vec<ConsensusPosition>, tonic::Status> {
         let consensus_transactions: Vec<_> = consensus_transactions.into();
         let (tx_consensus_positions, rx_consensus_positions) = oneshot::channel();
@@ -1038,6 +1051,7 @@ impl ValidatorService {
                 Some(&reconfiguration_lock),
                 epoch_store,
                 Some(tx_consensus_positions),
+                submitter_client_addr,
             )?;
         }
 
@@ -1079,6 +1093,7 @@ impl ValidatorService {
                     Some(&reconfiguration_lock),
                     epoch_store,
                     None,
+                    None, // not tracking submitter client addr for quorum driver path
                 )?;
                 // Do not wait for the result, because the transaction might have already executed.
                 // Instead, check or wait for the existence of certificate effects below.
```

### crates/sui-core/src/consensus_adapter.rs
```diff
@@ -3,6 +3,7 @@
 
 use std::collections::HashMap;
 use std::future::Future;
+use std::net::IpAddr;
 use std::ops::Deref;
 use std::sync::atomic::AtomicU64;
 use std::sync::atomic::Ordering;
@@ -372,7 +373,7 @@ impl ConsensusAdapter {
             if transaction.is_end_of_publish() {
                 info!(epoch=?epoch_store.epoch(), "Submitting EndOfPublish message to consensus");
             }
-            self.submit_unchecked(&[transaction], epoch_store, None);
+            self.submit_unchecked(&[transaction], epoch_store, None, None);
         }
     }
 
@@ -620,8 +621,15 @@ impl ConsensusAdapter {
         lock: Option<&RwLockReadGuard<ReconfigState>>,
         epoch_store: &Arc<AuthorityPerEpochStore>,
         tx_consensus_position: Option<oneshot::Sender<Vec<ConsensusPosition>>>,
+        submitter_client_addr: Option<IpAddr>,
     ) -> SuiResult<JoinHandle<()>> {
-        self.submit_batch(&[transaction], lock, epoch_store, tx_consensus_position)
+        self.submit_batch(
+            &[transaction],
+            lock,
+            epoch_store,
+            tx_consensus_position,
+            submitter_client_addr,
+        )
     }
 
     pub fn submit_batch(
@@ -630,6 +638,7 @@ impl ConsensusAdapter {
         lock: Option<&RwLockReadGuard<ReconfigState>>,
         epoch_store: &Arc<AuthorityPerEpochStore>,
         tx_consensus_position: Option<oneshot::Sender<Vec<ConsensusPosition>>>,
+        submitter_client_addr: Option<IpAddr>,
     ) -> SuiResult<JoinHandle<()>> {
         if transactions.len() > 1 {
             // When batching multiple transactions, ensure they are all of the same kind
@@ -668,7 +677,12 @@ impl ConsensusAdapter {
         }
 
         epoch_store.insert_pending_consensus_transactions(transactions, lock)?;
-        Ok(self.submit_unchecked(transactions, epoch_store, tx_consensus_position))
+        Ok(self.submit_unchecked(
+            transactions,
+            epoch_store,
+            tx_consensus_position,
+            submitter_client_addr,
+        ))
     }
 
     /// Performs weakly consistent checks on internal buffers to quickly
@@ -689,6 +703,7 @@ impl ConsensusAdapter {
         transactions: &[ConsensusTransaction],
         epoch_store: &Arc<AuthorityPerEpochStore>,
         tx_consensus_position: Option<oneshot::Sender<Vec<ConsensusPosition>>>,
+        submitter_client_addr: Option<IpAddr>,
     ) -> JoinHandle<()> {
         // Reconfiguration lock is dropped when pending_consensus_transactions is persisted, before it is handled by consensus
         let async_stage = self
@@ -697,6 +712,7 @@ impl ConsensusAdapter {
                 transactions.to_vec(),
                 epoch_store.clone(),
                 tx_consensus_position,
+                submitter_client_addr,
             )
             .in_current_span();
         // Number of these tasks is weakly limited based on `num_inflight_transactions`.
@@ -710,6 +726,7 @@ impl ConsensusAdapter {
         transactions: Vec<ConsensusTransaction>,
         epoch_store: Arc<AuthorityPerEpochStore>,
         tx_consensus_position: Option<oneshot::Sender<Vec<ConsensusPosition>>>,
+        submitter_client_addr: Option<IpAddr>,
     ) {
         // When epoch_terminated signal is received all pending submit_and_wait_inner are dropped.
         //
@@ -727,6 +744,7 @@ impl ConsensusAdapter {
                 transactions,
                 &epoch_store,
                 tx_consensus_position,
+                submitter_client_addr,
             ))
             .await
             .ok(); // result here indicates if epoch ended earlier, we don't care about it
@@ -739,11 +757,28 @@ impl ConsensusAdapter {
         transactions: Vec<ConsensusTransaction>,
         epoch_store: &Arc<AuthorityPerEpochStore>,
         tx_consensus_positions: Option<oneshot::Sender<Vec<ConsensusPosition>>>,
+        submitter_client_addr: Option<IpAddr>,
     ) {
         if transactions.is_empty() {
             return;
         }
 
+        // Record submitted transactions early for DoS protection
+        if epoch_store.protocol_config().mysticeti_fastpath() {
+            for transaction in &transactions {
+                if let ConsensusTransactionKind::UserTransaction(tx) = &transaction.kind {
+                    let amplification_factor = (tx.data().transaction_data().gas_price()
+                        / epoch_store.reference_gas_price().max(1))
+                    .max(1);
+                    epoch_store.submitted_transaction_cache.record_submitted_tx(
+                        tx.digest(),
+                        amplification_factor as u32,
+                        submitter_client_addr,
+                    );
+                }
+            }
+        }
+
         // If tx_consensus_positions channel is provided, the caller is looking for a
         // consensus position for mfp. Therefore we will skip shortcutting submission
         // if txes have already been processed.
@@ -977,6 +1012,7 @@ impl ConsensusAdapter {
                 None,
                 epoch_store,
                 None,
+                None,
             ) {
                 warn!("Error when sending end of publish message: {:?}", err);
             } else {
@@ -1225,6 +1261,7 @@ impl ReconfigurationInitiator for Arc<ConsensusAdapter> {
                 None,
                 epoch_store,
                 None,
+                None,
             ) {
                 warn!("Error when sending end of publish message: {:?}", err);
             } else {
@@ -1375,7 +1412,7 @@ impl SubmitToConsensus for Arc<ConsensusAdapter> {
         transactions: &[ConsensusTransaction],
         epoch_store: &Arc<AuthorityPerEpochStore>,
     ) -> SuiResult {
-        self.submit_batch(transactions, None, epoch_store, None)
+        self.submit_batch(transactions, None, epoch_store, None, None)
             .map(|_| ())
     }
 
```

### crates/sui-core/src/consensus_handler.rs
```diff
@@ -61,6 +61,7 @@ use crate::{
     execution_cache::ObjectCacheRead,
     execution_scheduler::{ExecutionScheduler, SchedulingSource},
     scoring_decision::update_low_scoring_authorities,
+    traffic_controller::policies::TrafficTally,
 };
 
 pub struct ConsensusHandlerInitializer {
@@ -134,6 +135,7 @@ impl ConsensusHandlerInitializer {
             self.state.metrics.clone(),
             self.throughput_calculator.clone(),
             self.backpressure_manager.subscribe(),
+            self.state.clone(),
         )
     }
 
@@ -544,6 +546,8 @@ pub struct ConsensusHandler<C> {
     additional_consensus_state: AdditionalConsensusState,
 
     backpressure_subscriber: BackpressureSubscriber,
+
+    state: Arc<AuthorityState>,
 }
 
 const PROCESSED_CACHE_CAP: usize = 1024 * 1024;
@@ -560,6 +564,7 @@ impl<C> ConsensusHandler<C> {
         metrics: Arc<AuthorityMetrics>,
         throughput_calculator: Arc<ConsensusThroughputCalculator>,
         backpressure_subscriber: BackpressureSubscriber,
+        state: Arc<AuthorityState>,
     ) -> Self {
         // Recover last_consensus_stats so it is consistent across validators.
         let mut last_consensus_stats = epoch_store
@@ -592,6 +597,7 @@ impl<C> ConsensusHandler<C> {
                 commit_rate_estimate_window_size,
             ),
             backpressure_subscriber,
+            state,
         }
     }
 
@@ -782,6 +788,45 @@ impl<C: CheckpointServiceNotify + Send + Sync> ConsensusHandler<C> {
                         block,
                         index: tx_index as TransactionIndex,
                     };
+
+                    // Transaction has appeared in consensus output, we can increment the submission count
+                    // for this tx for DoS protection.
+                    if self.epoch_store.protocol_config().mysticeti_fastpath() {
+                        if let ConsensusTransactionKind::UserTransaction(tx) =
+                            &parsed.transaction.kind
+                        {
+                            let digest = tx.digest();
+                            if let Some((spam_weight, submitter_client_addrs)) = self
+                                .epoch_store
+                                .submitted_transaction_cache
+                                .increment_submission_count(digest)
+                            {
+                                if let Some(ref traffic_controller) = self.state.traffic_controller
+                                {
+                                    debug!(
+                                        "Transaction {digest} exceeded submission limits, spam_weight: {spam_weight:?} applied to {} client addresses",
+                                        submitter_client_addrs.len()
+                                    );
+
+                                    // Apply spam weight to all client addresses that submitted this transaction
+                                    for addr in submitter_client_addrs {
+                                        traffic_controller.tally(TrafficTally::new(
+                                            Some(addr),
+                                            None,
+                                            None,
+                                            spam_weight.clone(),
+                                        ));
+                                    }
+                                } else {
+                                    warn!(
+                                        "Transaction {digest} exceeded submission limits, spam_weight: {spam_weight:?} for {} client addresses (traffic controller not configured)",
+                                        submitter_client_addrs.len()
+                                    );
+                                }
+                            }
+                        }
+                    }
+
                     if parsed.rejected {
                         if parsed.transaction.kind.is_user_transaction() {
                             self.epoch_store
@@ -951,7 +996,7 @@ impl<C: CheckpointServiceNotify + Send + Sync> ConsensusHandler<C> {
         let end_of_publish = ConsensusTransaction::new_end_of_publish(self.epoch_store.name);
         if let Err(err) =
             self.consensus_adapter
-                .submit(end_of_publish, None, &self.epoch_store, None)
+                .submit(end_of_publish, None, &self.epoch_store, None, None)
         {
             warn!(
                 "Error when sending EndOfPublish message from ConsensusHandler: {:?}",
@@ -1629,6 +1674,7 @@ mod tests {
             metrics,
             Arc::new(throughput_calculator),
             backpressure_manager.subscribe(),
+            state.clone(),
         );
 
         // AND create test user transactions alternating between owned and shared input.
@@ -2120,6 +2166,7 @@ mod tests {
             metrics,
             Arc::new(throughput),
             backpressure.subscribe(),
+            state.clone(),
         );
 
         handler.handle_consensus_commit(commit).await;
```

### crates/sui-core/src/unit_tests/consensus_tests.rs
```diff
@@ -360,6 +360,7 @@ async fn submit_transaction_to_consensus_adapter() {
             Some(&epoch_store.get_reconfig_state_read_lock_guard()),
             &epoch_store,
             None,
+            None,
         )
         .unwrap();
     waiter.await.unwrap();
@@ -406,6 +407,7 @@ async fn submit_multiple_transactions_to_consensus_adapter() {
             Some(&epoch_store.get_reconfig_state_read_lock_guard()),
             &epoch_store,
             None,
+            None,
         )
         .unwrap();
     waiter.await.unwrap();
@@ -492,6 +494,7 @@ async fn submit_checkpoint_signature_to_consensus_adapter() {
                 Some(&epoch_store.get_reconfig_state_read_lock_guard()),
                 &epoch_store,
                 None,
+                None,
             )
             .unwrap();
         waiter.await.unwrap();
```

### crates/sui-node/src/lib.rs
```diff
@@ -81,6 +81,7 @@ use sui_core::authority::authority_per_epoch_store::AuthorityPerEpochStore;
 use sui_core::authority::authority_store_tables::AuthorityPerpetualTables;
 use sui_core::authority::epoch_start_configuration::EpochStartConfigTrait;
 use sui_core::authority::epoch_start_configuration::EpochStartConfiguration;
+use sui_core::authority::submitted_transaction_cache::SubmittedTransactionCacheMetrics;
 use sui_core::authority_aggregator::{AuthAggMetrics, AuthorityAggregator};
 use sui_core::authority_server::{ValidatorService, ValidatorServiceMetrics};
 use sui_core::checkpoints::checkpoint_executor::metrics::CheckpointExecutorMetrics;
@@ -429,7 +430,7 @@ impl SuiNode {
                                     info!("Submitting JWK to consensus: {:?}", id);
 
                                     let txn = ConsensusTransaction::new_jwk_fetched(authority, id, jwk);
-                                    consensus_adapter.submit(txn, None, &epoch_store, None)
+                                    consensus_adapter.submit(txn, None, &epoch_store, None, None)
                                         .tap_err(|e| warn!("Error when submitting JWKs to consensus {:?}", e))
                                         .ok();
                                 }
@@ -583,6 +584,9 @@ impl SuiNode {
                 .get_highest_executed_checkpoint_seq_number()
                 .expect("checkpoint store read cannot fail")
                 .unwrap_or(0),
+            Arc::new(SubmittedTransactionCacheMetrics::new(
+                &registry_service.default_registry(),
+            )),
         )?;
 
         info!("created epoch store");
@@ -1810,9 +1814,13 @@ impl SuiNode {
                     ))
                 };
                 info!(?transaction, "submitting capabilities to consensus");
-                components
-                    .consensus_adapter
-                    .submit(transaction, None, &cur_epoch_store, None)?;
+                components.consensus_adapter.submit(
+                    transaction,
+                    None,
+                    &cur_epoch_store,
+                    None,
+                    None,
+                )?;
             }
 
             let stop_condition = checkpoint_executor.run_epoch(run_with_range).await;
```
