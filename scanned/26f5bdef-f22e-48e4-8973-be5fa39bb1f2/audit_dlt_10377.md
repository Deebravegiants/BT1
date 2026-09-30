# [?] Fix replica sequencer edge case where if the DA lagged, and the replica tried to process a batch from the leader with a visible slot number whose slot

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-07-01
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/283d726ec3b119ad3e37837b15fa51965d86adae
Type: security-commit

## Details
Fix replica sequencer edge case where if the DA lagged, and the replica tried to process a batch from the leader with a visible slot number whose slot header it didn't have, it would crash. (#3022)

## Patch
### crates/full-node/sov-sequencer/src/preferred/sync_sequencer_state/sync_state.rs
```diff
@@ -1255,6 +1255,11 @@ where
         let batch_from_master =
             Self::ensure_replica_batch_start_visible_slot_matches(&mut inner, batch_from_master)?;
 
+        Self::ensure_replica_batch_start_visible_slot_has_node_state(
+            &mut inner,
+            batch_from_master,
+        )?;
+
         Self::ensure_replica_batch_start_within_rebase_window(&mut inner, batch_from_master)?;
 
         inner
@@ -1405,6 +1410,38 @@ where
         ))
     }
 
+    fn ensure_replica_batch_start_visible_slot_has_node_state(
+        inner: &mut InnerGuard<'_, S, Rt>,
+        batch_from_master: BatchToStore,
+    ) -> Result<(), ReplicaError<S>> {
+        let node_latest_slot = inner.latest_info.slot_number;
+        let batch_visible_slot = batch_from_master
+            .visible_slot_number_after_increase
+            .as_true();
+
+        if batch_visible_slot <= node_latest_slot {
+            return Ok(());
+        }
+
+        tracing::warn!(
+            %batch_visible_slot,
+            %node_latest_slot,
+            "Replica batch start would advance the visible slot past the latest node slot. Rejecting batch start until node replay catches up."
+        );
+
+        let sync_details = SequencerNotReadyDetails::Syncing {
+            target_da_height: inner.latest_info.sync_status.target_da_height(),
+            synced_da_height: inner.latest_info.sync_status.synced_da_height(),
+        };
+
+        inner.is_ready = Err(sync_details.clone());
+
+        Err(ReplicaError::NotReady(
+            sync_details,
+            Box::new(DbData::BatchStart(batch_from_master)),
+        ))
+    }
+
     fn ensure_replica_batch_start_within_rebase_window(
         inner: &mut InnerGuard<'_, S, Rt>,
         batch_from_master: BatchToStore,
```

### crates/utils/sov-test-utils/src/test_rollup.rs
```diff
@@ -938,6 +938,27 @@ where
         .await
     }
 
+    /// Checks if the sequencer is not ready specifically because it is syncing, i.e. its node has
+    /// fallen behind the DA head (see `SequencerNotReadyDetails::Syncing`).
+    pub async fn is_sequencer_syncing(&self) -> bool {
+        match self.client.client.is_ready().await {
+            Err(err) => err.to_string().contains("fell out of sync"),
+            Ok(_) => false,
+        }
+    }
+
+    /// Polls the sequencer until it reports the syncing (node-behind) not-ready reason.
+    ///
+    /// Times out after TestRollup::POLLING_TIMEOUT seconds. Fails fast if the rollup crashes (see
+    /// [`TestRollup::wait_for_condition`]).
+    pub async fn wait_for_sequencer_syncing(&self) -> anyhow::Result<()> {
+        self.wait_for_condition(
+            || async { Ok(self.is_sequencer_syncing().await) },
+            "sequencer to enter syncing",
+        )
+        .await
+    }
+
     /// Generic helper for waiting on a condition with timeout and polling.
     ///  * condition_string: inserted into "Timeout waiting for {condition_string}", format accordingly
     async fn wait_for_condition<F, Fut>(
@@ -951,6 +972,13 @@ where
     {
         let wait_loop = async {
             loop {
+                // Fail fast if the rollup crashed instead of reaching the awaited condition, so a
+                // regression surfaces as a clear crash error rather than waiting out the timeout.
+                anyhow::ensure!(
+                    !self.is_rollup_crashed(),
+                    "rollup crashed while waiting for {}",
+                    condition_string
+                );
                 match condition_check().await {
                     Ok(true) => return Ok(()),
                     Ok(false) => tokio::time::sleep(Duration::from_millis(100)).await,
```

### examples/demo-rollup/tests/replica/mod.rs
```diff
@@ -2,6 +2,7 @@ mod db_elected;
 mod proofs;
 mod recovery;
 mod replica_gets_txs_from_master;
+mod replica_node_lag;
 mod replica_partitioned_db;
 mod replica_registers_in_db;
 mod root_hash_checker;
@@ -335,3 +336,23 @@ async fn establish_leader_and_replica(
 
     (leader, replica)
 }
+
+async fn verify_replica_processes_tx(
+    leader: &TestRollup<Rollup>,
+    replica: &TestRollup<Rollup>,
+    key: &<<S as Spec>::CryptoSpec as CryptoSpec>::PrivateKey,
+    token_id: sov_bank::TokenId,
+    receiver_addr: <S as Spec>::Address,
+    nonce: u64,
+) {
+    let tx = build_transfer_token_tx::<S>(key, token_id, receiver_addr, AMOUNT, nonce);
+
+    let mut event_subscription = replica
+        .api_client()
+        .subscribe_to_events_with_filter("Bank/*")
+        .await
+        .unwrap();
+
+    leader.send_tx_to_sequencer(&tx).await.unwrap();
+    wait_for_all_events_with_timeout(Duration::from_millis(3500), 1, &mut event_subscription).await;
+}
```

### examples/demo-rollup/tests/replica/recovery.rs
```diff
@@ -207,23 +207,3 @@ async fn test_db_elected_replica_recovers_after_only_replica_is_paused() {
     leader.shutdown().await.unwrap();
     setup.shutdown().await;
 }
-
-async fn verify_replica_processes_tx(
-    leader: &TestRollup<Rollup>,
-    replica: &TestRollup<Rollup>,
-    key: &<<S as Spec>::CryptoSpec as CryptoSpec>::PrivateKey,
-    token_id: sov_bank::TokenId,
-    receiver_addr: <S as Spec>::Address,
-    nonce: u64,
-) {
-    let tx = build_transfer_token_tx::<S>(key, token_id, receiver_addr, AMOUNT, nonce);
-
-    let mut event_subscription = replica
-        .api_client()
-        .subscribe_to_events_with_filter("Bank/*")
-        .await
-        .unwrap();
-
-    leader.send_tx_to_sequencer(&tx).await.unwrap();
-    wait_for_all_events_with_timeout(Duration::from_millis(3500), 1, &mut event_subscription).await;
-}
```

### examples/demo-rollup/tests/replica/replica_node_lag.rs
```diff
@@ -0,0 +1,97 @@
+use super::*;
+
+/// Regression test for `ensure_replica_batch_start_visible_slot_has_node_state`.
+///
+/// When a replica's node state lags behind the leader, the leader persists a batch-start whose
+/// `visible_slot_number_after_increase` is past the replica node's latest slot. The replica must
+/// reject that batch-start, surface the `Syncing` not-ready reason, and keep retrying without
+/// crashing, then recover once its node catches up.
+///
+/// We reproduce the lag by pausing only the replica's `update_state` loop (which freezes its
+/// `latest_info.slot_number`) while the leader keeps advancing on a healthy Postgres + DA.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_replica_rejects_batch_start_beyond_node_state_and_recovers() {
+    std::env::set_var("SOV_TEST_CONST_OVERRIDE_STATE_ROOT_DELAY_BLOCKS", "5");
+    let Some(setup) = NodeDiscoveryTestSetup::new().await else {
+        return;
+    };
+
+    let key_and_address = read_private_key::<S>("tx_signer_private_key.json");
+
+    let node_1 = setup
+        .start_node("node_1", ConfiguredNodeRole::DbElected)
+        .await;
+    let node_2 = setup
+        .start_node("node_2", ConfiguredNodeRole::DbElected)
+        .await;
+
+    node_1.wait_for_sequencer_ready().await.unwrap();
+    node_2.wait_for_sequencer_ready().await.unwrap();
+
+    let (leader, replica) = establish_leader_and_replica(node_1, node_2).await;
+
+    let token_id = config_gas_token_id();
+    let receiver_addr = random_address();
+
+    // Confirm the cluster is healthy and the replica has finished startup and caught up, so the
+    // guard returns `Syncing` (node behind) rather than `Startup`.
+    verify_replica_processes_tx(
+        &leader,
+        &replica,
+        &key_and_address.private_key,
+        token_id,
+        receiver_addr,
+        0,
+    )
+    .await;
+
+    // Freeze ONLY the replica's node state by pausing its `update_state` loop. Postgres stays
+    // healthy, so the replica keeps pulling the leader's batch-starts from the shared DB.
+    replica.pause_preferred_batches_for_node().await;
+
+    // Keep the leader producing real batches while the DA advances, so it persists batch-starts
+    // whose `visible_slot_number_after_increase` climbs past the replica's now-frozen node slot,
+    // tripping `ensure_replica_batch_start_visible_slot_has_node_state`.
+    send_transfers(
+        1,
+        3,
+        read_private_key::<S>("tx_signer_private_key.json"),
+        receiver_addr,
+        leader.api_client().clone(),
+    )
+    .await;
+
+    for _ in 0..60 {
+        setup.da_service.produce_block_now().await.unwrap();
+    }
+
+    // The replica rejects the future-slot batch-start with `Syncing` and keeps retrying without
+    // crashing. `wait_for_sequencer_syncing` fails fast if the replica crashes instead.
+    replica.wait_for_sequencer_syncing().await.unwrap();
+    assert!(
+        !replica.is_rollup_crashed(),
+        "the replica batch-start guard must reject the batch without crashing the rollup"
+    );
+
+    // Resume the replica: its node catches up past the batch's visible slot and it becomes ready.
+    leader.wait_for_node_synced().await.unwrap();
+    replica.resume_preferred_batches_for_node().await;
+    setup.da_service.produce_block_now().await.unwrap();
+    replica.wait_for_sequencer_ready().await.unwrap();
+
+    // Confirm the cluster still works end-to-end after recovery. Nonces 1-3 were used by the
+    // transfers sent during the replica's downtime above, so the next transfer uses nonce 4.
+    verify_replica_processes_tx(
+        &leader,
+        &replica,
+        &key_and_address.private_key,
+        token_id,
+        receiver_addr,
+        4,
+    )
+    .await;
+
+    replica.shutdown().await.unwrap();
+    leader.shutdown().await.unwrap();
+    setup.shutdown().await;
+}
```
