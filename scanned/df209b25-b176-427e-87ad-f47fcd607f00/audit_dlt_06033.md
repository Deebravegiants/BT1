# [?] fix(consensus-adapter): actually insert `EndOfPublish` (if absent) for re-submission on crash recovery (#10578)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-03-04
Source: https://github.com/iotaledger/iota/commit/41729efe0580c5cf41f13844a737813f5faf7a00
Type: security-commit

## Details
fix(consensus-adapter): actually insert `EndOfPublish` (if absent) for re-submission on crash recovery (#10578)

# Description of change

This PR fixes a plain inversion bug in `submit_recovered` of
`ConsensusAdapter`. Specifically, if the list of `recovered` pending
consensus transactions does not contain an `EndOfPublish` transaction,
the condition
`recovered.iter().any(ConsensusTransaction::is_end_of_publish)` is
`false`, which means `EndOfPublish` will never be resubmitted in the
case of crash recovery, likely leading to epoch transitioning getting
stuck. In contrast, if `EndOfPublish` is already present in recovered,
the current code on `develop` needlessly inserts another `EndOfPublish`.
However, in the actual crash-recovery scenario, we would like to insert
`EndOfPublish` into `recovered` if it was absent; hence, the inverted
condition
`!recovered.iter().any(ConsensusTransaction::is_end_of_publish)` is
correct.

Other minor changes include improving the corresponding comments and
removing `#[expect(clippy::collapsible_if)]` as it is no longer needed.

> [!NOTE]
> 1. The bug was discovered during the certificate-less epoch change PoC
([branch](https://github.com/iotaledger/iota/tree/protocol-research/feat/certificate-less-epoch-boundary-coordination)).
> 2. Upstream added this fix as a part of
https://github.com/MystenLabs/sui/pull/23122.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

---------

Signed-off-by: Roman Overko <roman.overko@iota.org>

### crates/iota-core/src/consensus_adapter.rs
```diff
@@ -342,24 +342,24 @@ impl ConsensusAdapter {
         // be a big deal but can be optimized
         let mut recovered = epoch_store.get_all_pending_consensus_transactions();
 
-        #[expect(clippy::collapsible_if)] // This if can be collapsed but it will be ugly
         if epoch_store
             .get_reconfig_state_read_lock_guard()
             .is_reject_user_certs()
             && epoch_store.pending_consensus_certificates_empty()
         {
-            if recovered
+            // If `recovered` does not contain `EndOfPublish` yet, we need to insert it.
+            if !recovered
                 .iter()
                 .any(ConsensusTransaction::is_end_of_publish)
             {
-                // There are two cases when this is needed
-                // (1) We send EndOfPublish message after removing pending certificates in
-                // submit_and_wait_inner It is possible that node will crash
+                // There are two cases when this is needed:
+                // (1) We send `EndOfPublish` message after removing pending certificates in
+                // `submit_and_wait_inner`. It is possible that node will crash
                 // between those two steps, in which case we might need to
-                // re-introduce EndOfPublish message on restart
-                // (2) If node crashed inside ConsensusAdapter::close_epoch,
+                // re-introduce `EndOfPublish` message on restart.
+                // (2) If node crashed inside `ConsensusAdapter::close_epoch`,
                 // after reconfig lock state was written to DB and before we persisted
-                // EndOfPublish message
+                // `EndOfPublish` message.
                 recovered.push(ConsensusTransaction::new_end_of_publish(self.authority));
             }
         }
```

### crates/iota-core/src/unit_tests/consensus_tests.rs
```diff
@@ -400,3 +400,226 @@ async fn submit_checkpoint_signature_to_consensus_adapter() {
     t1.await.unwrap();
     t2.await.unwrap();
 }
+
+/// Regression test for the inverted condition to re-submit
+/// `EndOfPublish` in `ConsensusAdapter::submit_recovered`.
+///
+/// The original condition was:
+/// ```rust
+/// if recovered
+///     .iter()
+///     .any(ConsensusTransaction::is_end_of_publish)
+/// {
+///     recovered.push(ConsensusTransaction::EndOfPublish)
+/// }
+/// ```
+/// This was a bug since the logic is backwards - it added a duplicate
+/// `EndOfPublish` when one was already in the DB, and did nothing when
+/// `EndOfPublish` was missing (the exact crash recovery case).
+///
+/// The fix adds `!` to make the condition correct.
+///
+/// This test covers two crash scenarios:
+///
+/// Scenario 1: crash between pending consensus certificates removal and
+/// `EndOfPublish` submission. In this case, a node is in `RejectUserCerts`
+/// state, pending consensus certificates are empty, but `EndOfPublish` was
+/// never persisted. Without the fix, `submit_recovered` submits nothing,
+/// in which case epoch stalls permanently. Scenario 1 covers both cases
+/// described in the comments in `ConsensusAdapter::submit_recovered`.
+///
+/// Scenario 2: crash after `EndOfPublish` was persisted but before it was
+/// sequenced. Without the fix, a duplicate `EndOfPublish` is added and two
+/// are submitted instead of one.
+#[tokio::test]
+async fn submit_recovered_end_of_publish_crash_recovery() {
+    use consensus_core::{BlockRef, BlockStatus};
+    use tokio::sync::Notify;
+
+    use crate::mock_consensus::with_block_status;
+
+    /// A minimal consensus client that records what was submitted to it.
+    /// The `notify` fires each time `submit` is called, allowing the test
+    /// to synchronize without polling.
+    struct RecordingClient {
+        submitted: Arc<Mutex<Vec<ConsensusTransaction>>>,
+        notify: Arc<Notify>,
+    }
+
+    #[async_trait::async_trait]
+    impl ConsensusClient for RecordingClient {
+        /// Return `BlockStatus::Sequenced` so `submit_inner` resolves.
+        /// The task then waits on the consensus-processed notification,
+        /// which is harmless for this test.
+        async fn submit(
+            &self,
+            transactions: &[ConsensusTransaction],
+            _epoch_store: &Arc<AuthorityPerEpochStore>,
+        ) -> IotaResult<BlockStatusReceiver> {
+            self.submitted.lock().extend_from_slice(transactions);
+            self.notify.notify_one();
+
+            Ok(with_block_status(BlockStatus::Sequenced(BlockRef::MIN)))
+        }
+    }
+
+    // -----------------------------------------------------------------------
+    // Scenario 1: crash after all pending consensus certificates were removed
+    // but before `EndOfPublish` was ever persisted.
+    //
+    // State on restart:
+    //   - Reconfig state: `RejectUserCerts`.
+    //   - Pending consensus certificates are empty.
+    //   - `EndOfPublish` was not persisted before crash.
+    //
+    // Expected behavior: `ConsensusAdapter::submit_recovered` synthesizes a new
+    // `EndOfPublish` and submits it.
+    // -----------------------------------------------------------------------
+    {
+        let state = init_state_with_objects(vec![]).await;
+        let epoch_store = state.epoch_store_for_testing();
+        epoch_store.close_user_certs(epoch_store.get_reconfig_state_write_lock_guard());
+
+        // Verify that all pre-conditions match the crash scenario.
+        assert!(
+            epoch_store
+                .get_reconfig_state_read_lock_guard()
+                .is_reject_user_certs(),
+            "Scenario 1: reconfig state must be RejectUserCerts"
+        );
+        assert!(
+            epoch_store.pending_consensus_certificates_empty(),
+            "Scenario 1: pending consensus certificates must be empty"
+        );
+        assert!(
+            !epoch_store
+                .get_all_pending_consensus_transactions()
+                .iter()
+                .any(|tx| tx.is_end_of_publish()),
+            "Scenario 1: `EndOfPublish` must not be persisted in DB before crash"
+        );
+
+        let submitted = Arc::new(Mutex::new(vec![]));
+        let notify = Arc::new(Notify::new());
+        let adapter = Arc::new(ConsensusAdapter::new(
+            Arc::new(RecordingClient {
+                submitted: submitted.clone(),
+                notify: notify.clone(),
+            }),
+            state.checkpoint_store.clone(),
+            state.name,
+            Arc::new(ConnectionMonitorStatusForTests {}),
+            100_000,
+            100_000,
+            None,
+            None,
+            ConsensusAdapterMetrics::new_test(),
+        ));
+
+        adapter.submit_recovered(&epoch_store);
+
+        // Wait for the spawned task to reach the mock's `submit`.
+        // A timeout here means `EndOfPublish` was never submitted,
+        // in which case the epoch stalls - this was the bug the
+        // original condition caused.
+        tokio::time::timeout(Duration::from_secs(5), notify.notified())
+            .await
+            .expect(
+                "Scenario 1: ConsensusAdapter::submit_recovered did not submit \
+                    `EndOfPublish`, so epoch stalls",
+            );
+
+        assert!(
+            submitted
+                .lock()
+                .iter()
+                .any(|tx: &ConsensusTransaction| tx.is_end_of_publish()),
+            "Scenario 1: ConsensusAdapter::submit_recovered must submit EndOfPublish after crash"
+        );
+    }
+
+    // -----------------------------------------------------------------------
+    // Scenario 2: crash after `EndOfPublish` was persisted but before it was
+    // sequenced.
+    //
+    // State on restart:
+    //   - Reconfig state: `RejectUserCerts`.
+    //   - Pending consensus certificates are empty.
+    //   - `EndOfPublish` was persisted before crash.
+    //
+    // Expected behavior: exactly one `EndOfPublish` submitted (the one
+    // recovered from DB).
+    // -----------------------------------------------------------------------
+    {
+        let state = init_state_with_objects(vec![]).await;
+        let epoch_store = state.epoch_store_for_testing();
+        epoch_store.close_user_certs(epoch_store.get_reconfig_state_write_lock_guard());
+
+        // Simulate `EndOfPublish` persisted to DB before the crash.
+        let end_of_publish = ConsensusTransaction::new_end_of_publish(state.name);
+        epoch_store
+            .insert_pending_consensus_transactions(&[end_of_publish], None)
+            .expect("Scenario 2: failed to insert EndOfPublish");
+
+        // Verify that all pre-conditions match the crash scenario.
+        assert!(
+            epoch_store
+                .get_reconfig_state_read_lock_guard()
+                .is_reject_user_certs(),
+            "Scenario 2: reconfig state must be RejectUserCerts"
+        );
+        assert!(
+            epoch_store.pending_consensus_certificates_empty(),
+            "Scenario 2: pending consensus certificates must be empty"
+        );
+        assert!(
+            epoch_store
+                .get_all_pending_consensus_transactions()
+                .iter()
+                .any(|tx| tx.is_end_of_publish()),
+            "Scenario 2: `EndOfPublish` must be persisted in DB before crash"
+        );
+
+        let submitted = Arc::new(Mutex::new(vec![]));
+        let notify = Arc::new(Notify::new());
+        let adapter = Arc::new(ConsensusAdapter::new(
+            Arc::new(RecordingClient {
+                submitted: submitted.clone(),
+                notify: notify.clone(),
+            }),
+            state.checkpoint_store.clone(),
+            state.name,
+            Arc::new(ConnectionMonitorStatusForTests {}),
+            100_000,
+            100_000,
+            None,
+            None,
+            ConsensusAdapterMetrics::new_test(),
+        ));
+
+        adapter.submit_recovered(&epoch_store);
+
+        tokio::time::timeout(Duration::from_secs(5), notify.notified())
+            .await
+            .expect(
+                "Scenario 2: ConsensusAdapter::submit_recovered did not submit \
+                    `EndOfPublish`, so epoch stalls",
+            );
+
+        // Allow any potential second submission task to also reach the mock.
+        tokio::task::yield_now().await;
+
+        let end_of_publish_count = submitted
+            .lock()
+            .iter()
+            .filter(|tx: &&ConsensusTransaction| tx.is_end_of_publish())
+            .count();
+
+        // Without the fix, a duplicate `EndOfPublish` would be pushed.
+        assert_eq!(
+            end_of_publish_count, 1,
+            "Scenario 2: ConsensusAdapter::submit_recovered must not duplicate `EndOfPublish` \
+                if it was already in DB, got {end_of_publish_count} EndOfPublish"
+        );
+    }
+}
```
