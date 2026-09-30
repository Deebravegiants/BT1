# [?] Use runner internal secondary shutdown for runner tasks to avoid deadlock (#2799)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-05-01
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/a4af1d22c17732ce8e128bcc287140164ed09c65
Type: security-commit

## Details
Use runner internal secondary shutdown for runner tasks to avoid deadlock (#2799)

## Patch
### crates/full-node/sov-stf-runner/src/runner.rs
```diff
@@ -238,7 +238,7 @@ where
             first_unprocessed_height_at_startup,
             runner_config.concurrent_sync_tasks,
             runner_config.pre_fetched_blocks_capacity.get(),
-            shutdown_receiver.clone(),
+            secondary_shutdown_receiver.clone(),
         )
         .await?;
         background_handles.push(fetcher_background_handle);
@@ -400,8 +400,10 @@ where
 
         let mut next_da_height = self.first_unprocessed_height_at_startup;
 
-        let status_updater_handle = self
-            .spawn_sync_status_updater(self.da_polling_interval, self.shutdown_receiver.clone());
+        let status_updater_handle = self.spawn_sync_status_updater(
+            self.da_polling_interval,
+            self.secondary_shutdown_sender.subscribe(),
+        );
 
         let start_at_rollup_height = self.start_at_rollup_height;
         let stop_at_rollup_height = self.stop_at_rollup_height;
```

### crates/full-node/sov-stf-runner/tests/integration/helpers/hash_stf.rs
```diff
@@ -221,7 +221,7 @@ impl<Da: DaSpec> StateTransitionFunction<Da> for HashStf {
             batch_receipts: vec![],
             discarded_blobs: vec![],
             witness,
-            rollup_height: RollupHeight::new(0),
+            rollup_height: RollupHeight::new(slot_header.height()),
         }
     }
 }
```

### crates/full-node/sov-stf-runner/tests/integration/helpers/runner_init.rs
```diff
@@ -165,6 +165,25 @@ pub async fn initialize_runner(
     init_variant: MockInitVariant,
     aggregated_proof_block_jump: usize,
     nb_of_prover_threads: Option<usize>,
+) -> (HashStfRunner<MockDaService>, StateRoot, TestNode) {
+    initialize_runner_with_stop_at(
+        da_service,
+        path,
+        init_variant,
+        aggregated_proof_block_jump,
+        nb_of_prover_threads,
+        None,
+    )
+    .await
+}
+
+pub async fn initialize_runner_with_stop_at(
+    da_service: Arc<MockDaService>,
+    path: &std::path::Path,
+    init_variant: MockInitVariant,
+    aggregated_proof_block_jump: usize,
+    nb_of_prover_threads: Option<usize>,
+    stop_at_rollup_height: Option<sov_rollup_interface::common::RollupHeight>,
 ) -> (HashStfRunner<MockDaService>, StateRoot, TestNode) {
     let stf = HashStf::new();
     let inner_vm = MockZkvmHost::new();
@@ -207,9 +226,10 @@ pub async fn initialize_runner(
         .unwrap();
     let ledger_db = LedgerDb::with_reader(ledger_state).unwrap();
 
-    let da_sync_state = make_da_sync_state(0, None, &ledger_db, &da_service_with_cache)
-        .await
-        .unwrap();
+    let da_sync_state =
+        make_da_sync_state(0, stop_at_rollup_height, &ledger_db, &da_service_with_cache)
+            .await
+            .unwrap();
     let _sync_status_receiver = da_sync_state.sync_status_sender.subscribe();
     let state_channel = StateChannel::new(
         bootstrap_state_update_info(&mut storage_manager, da_sync_state.as_ref())
@@ -266,7 +286,7 @@ pub async fn initialize_runner(
         Box::new(InfiniteHeight),
         shutdown_receiver.clone(),
         None,
-        None,
+        stop_at_rollup_height,
         da_sync_state,
         da_service_with_cache,
         0,
```

### crates/full-node/sov-stf-runner/tests/integration/runner_reorg_tests.rs
```diff
@@ -2,7 +2,8 @@ use std::sync::Arc;
 
 use crate::helpers::hash_stf::{HashStf, S};
 use crate::helpers::runner_init::{
-    bootstrap_state_update_info, initialize_runner, HashStfRunner, InitVariant,
+    bootstrap_state_update_info, initialize_runner, initialize_runner_with_stop_at, HashStfRunner,
+    InitVariant,
 };
 use anyhow::Context;
 use sov_db::config::RollupDbConfig;
@@ -18,6 +19,7 @@ use sov_mock_da::{
 use sov_modules_api::provable_height_tracker::InfiniteHeight;
 use sov_modules_api::{FullyBakedTx, StateTransitionFunction};
 use sov_rollup_full_node_interface::StateChannel;
+use sov_rollup_interface::common::RollupHeight;
 use sov_rollup_interface::node::da::{DaService, SlotData};
 use sov_rollup_interface::node::SyncStatus;
 use sov_rollup_interface::storage::HierarchicalStorageManager;
@@ -396,6 +398,42 @@ async fn check_runner(
     assert_eq!(expected_state_root, after);
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn test_stop_at_rollup_height_stops_with_prefetch_backlog() -> anyhow::Result<()> {
+    let tmp_dir = tempfile::tempdir()?;
+    let sequencer_address = MockAddress::new([11u8; 32]);
+    let genesis_params = vec![1, 2, 3, 4, 5];
+    let stop_at_height = RollupHeight::new(3);
+
+    let da_service = Arc::new(MockDaService::new(sequencer_address).with_wait_attempts(2));
+    let genesis_block = da_service.get_block_at(0).await?;
+
+    for _ in 0..100 {
+        da_service.send_transaction(&batch(vec![1])).await.await??;
+    }
+
+    let init_variant: MockInitVariant = InitVariant::Genesis {
+        block: genesis_block,
+        genesis_params: genesis_params.into(),
+    };
+
+    let (mut runner, _before, test_node) = initialize_runner_with_stop_at(
+        da_service,
+        tmp_dir.path(),
+        init_variant,
+        1,
+        None,
+        Some(stop_at_height),
+    )
+    .await;
+
+    tokio::time::timeout(std::time::Duration::from_secs(20), runner.run_in_process()).await??;
+    drop(runner);
+    test_node.stop().await;
+
+    Ok(())
+}
+
 fn get_saved_root_hash(
     path: &std::path::Path,
 ) -> anyhow::Result<Option<<TestStorage as Storage>::Root>> {
```
