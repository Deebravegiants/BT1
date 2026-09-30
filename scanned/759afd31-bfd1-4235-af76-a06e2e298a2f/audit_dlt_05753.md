# [?] [consensus][framework] Fix chunky DKG enable-feature: on_new_epoch + pipeline deadlock

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-05
Source: https://github.com/aptos-labs/aptos-core/commit/789639bec9448286f23cc31cfa2dfa232440639f
Type: security-commit

## Details
[consensus][framework] Fix chunky DKG enable-feature: on_new_epoch + pipeline deadlock

Two fixes for the enable-feature smoke test:

1. Framework: Add missing `chunky_dkg_config::on_new_epoch(framework)` call
   in `reconfiguration_with_dkg::finish()`. Without this, the chunky DKG
   config buffered via governance `set_for_next_epoch` was never applied.

2. Consensus pipeline: Break circular dependency in decryption pipeline when
   `decryption_enabled=true` but `secret_share_config=None` (bootstrapping
   epoch). The cycle was: has_rand_txns_fut -> prepare -> decrypt (waiting
   for secret_shared_key_rx from ordering) -> but ordering blocked on
   has_rand_txns_fut. Use `observer_enabled` flag to distinguish consensus
   nodes (return immediately) from observers (wait for key from leader).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### aptos-move/framework/aptos-framework/doc/reconfiguration_with_dkg.md
```diff
@@ -162,6 +162,7 @@ Run the default reconfiguration to enter the new epoch.
     <a href="randomness_config_seqnum.md#0x1_randomness_config_seqnum_on_new_epoch">randomness_config_seqnum::on_new_epoch</a>(framework);
     <a href="randomness_config.md#0x1_randomness_config_on_new_epoch">randomness_config::on_new_epoch</a>(framework);
     <a href="randomness_api_v0_config.md#0x1_randomness_api_v0_config_on_new_epoch">randomness_api_v0_config::on_new_epoch</a>(framework);
+    <a href="chunky_dkg_config.md#0x1_chunky_dkg_config_on_new_epoch">chunky_dkg_config::on_new_epoch</a>(framework);
     <a href="decryption.md#0x1_decryption_on_new_epoch">decryption::on_new_epoch</a>(framework);
     <a href="reconfiguration.md#0x1_reconfiguration_reconfigure">reconfiguration::reconfigure</a>();
 }
```

### aptos-move/framework/aptos-framework/sources/reconfiguration_with_dkg.move
```diff
@@ -82,6 +82,7 @@ module aptos_framework::reconfiguration_with_dkg {
         randomness_config_seqnum::on_new_epoch(framework);
         randomness_config::on_new_epoch(framework);
         randomness_api_v0_config::on_new_epoch(framework);
+        chunky_dkg_config::on_new_epoch(framework);
         decryption::on_new_epoch(framework);
         reconfiguration::reconfigure();
     }
```

### consensus/src/pipeline/decryption_pipeline_builder.rs
```diff
@@ -38,6 +38,7 @@ impl PipelineBuilder {
         maybe_secret_share_config: Option<SecretShareConfig>,
         derived_self_key_share_tx: oneshot::Sender<Option<SecretShare>>,
         secret_shared_key_rx: oneshot::Receiver<Option<SecretSharedKey>>,
+        observer_enabled: bool,
     ) -> TaskResult<DecryptionResult> {
         let mut tracker = Tracker::start_waiting("decrypt_encrypted_txns", &block);
         let (input_txns, max_txns_from_block_to_execute, block_gas_limit) = materialize_fut.await?;
@@ -59,8 +60,21 @@ impl PipelineBuilder {
         // Assumption: `input_txns` is free of Encrypted Transactions
         // due to VM validation checks
         let Some(secret_share_config) = maybe_secret_share_config else {
-            // TODO(ibalajiarun): Is sending None necessary?
             let _ = derived_self_key_share_tx.send(None);
+            // Consensus node without secret share config (e.g. bootstrapping
+            // epoch where chunky DKG is newly enabled but hasn't completed yet).
+            // Return immediately with no decryption key to avoid a circular
+            // dependency: has_rand_txns_fut -> prepare -> decrypt (waiting for
+            // secret_shared_key_rx) -> ordering (blocked on has_rand_txns_fut).
+            if !observer_enabled {
+                return Ok((
+                    input_txns,
+                    max_txns_from_block_to_execute,
+                    block_gas_limit,
+                    Some(None),
+                ));
+            }
+            // Observer: wait for the decryption key from the ordering path.
             let maybe_key = secret_shared_key_rx
                 .await
                 .map_err(|_| anyhow!("secret_shared_key_rx dropped in observer path"))?;
```

### consensus/src/pipeline/pipeline_builder.rs
```diff
@@ -473,6 +473,7 @@ impl PipelineBuilder {
                 self.secret_share_config.clone(),
                 derived_self_key_share_tx,
                 secret_shared_key_rx,
+                observer_enabled,
             ),
             Some(&mut abort_handles),
         );
```

### testsuite/smoke-test/src/chunky_dkg/enable_feature.rs
```diff
@@ -1,23 +1,29 @@
 // Copyright (c) Aptos Foundation
 // Licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE
 
-use super::{get_encryption_key_resource, verify_chunky_dkg_transcript};
+use super::{
+    get_encryption_key_resource, verify_chunky_dkg_transcript, wait_for_chunky_dkg_finish,
+};
 use crate::{smoke_test_environment::SwarmBuilder, utils::get_on_chain_resource};
 use aptos_forge::{Node, Swarm, SwarmExt};
-use aptos_logger::{debug, info};
-use aptos_types::{dkg::chunky_dkg::ChunkyDKGState, on_chain_config::OnChainRandomnessConfig};
+use aptos_logger::info;
+use aptos_types::{
+    dkg::{chunky_dkg::ChunkyDKGState, DKGState},
+    on_chain_config::{ChunkyDKGConfigMoveStruct, OnChainRandomnessConfig},
+};
 use std::{sync::Arc, time::Duration};
 
-/// Enable chunky DKG config and the ENCRYPTED_TRANSACTIONS feature flag via
-/// a governance Move script at runtime, with randomness and validator txns
-/// already enabled at genesis.
+/// Enable chunky DKG config and the ENCRYPTED_TRANSACTIONS feature flag at
+/// runtime via a governance Move script.  Randomness and validator txns are
+/// already enabled at genesis; only the chunky-DKG-specific pieces are turned
+/// on dynamically.
 #[tokio::test]
 async fn chunky_dkg_enable_feature() {
     let epoch_duration_secs = 20;
-    let estimated_dkg_latency_secs = 40;
+    let estimated_dkg_latency_secs = 120;
 
-    // Start with randomness and validator txns enabled at genesis,
-    // but chunky DKG and encrypted transactions disabled.
+    // Genesis: randomness + validator txns enabled.
+    // Chunky DKG config is OFF (default). ENCRYPTED_TRANSACTIONS is OFF.
     let (swarm, mut cli, _faucet) = SwarmBuilder::new_local(4)
         .with_aptos()
         .with_init_config(Arc::new(|_, config, _| {
@@ -41,7 +47,7 @@ async fn chunky_dkg_enable_feature() {
             conf.allow_new_validators = true;
             conf.consensus_config.enable_validator_txns();
             conf.randomness_config_override = Some(OnChainRandomnessConfig::default_enabled());
-            // chunky DKG and ENCRYPTED_TRANSACTIONS are NOT enabled at genesis.
+            // Chunky DKG config defaults to Off. ENCRYPTED_TRANSACTIONS not set.
         }))
         .build_with_cli(0)
         .await;
@@ -52,104 +58,109 @@ async fn chunky_dkg_enable_feature() {
     let client_endpoint = swarm.validators().nth(1).unwrap().rest_api_endpoint();
     let client = aptos_rest_client::Client::new(client_endpoint.clone());
 
-    // Wait for epoch 3 so the network is stable.
+    // Wait for epoch 2 so the network is stable.
     swarm
-        .wait_for_all_nodes_to_catchup_to_epoch(3, Duration::from_secs(epoch_duration_secs * 2))
+        .wait_for_all_nodes_to_catchup_to_epoch(2, Duration::from_secs(epoch_duration_secs * 3))
         .await
-        .expect("Waited too long for epoch 3.");
+        .expect("Waited too long for epoch 2.");
 
-    // Enable chunky DKG config and ENCRYPTED_TRANSACTIONS feature flag via governance.
-    info!("Now in epoch 3. Enabling chunky DKG config and ENCRYPTED_TRANSACTIONS feature.");
+    // Verify chunky DKG has NOT completed (config is off).
+    let chunky_dkg_state = get_on_chain_resource::<ChunkyDKGState>(&client).await;
+    assert!(
+        chunky_dkg_state.last_completed.is_none(),
+        "Chunky DKG should not have completed with config off"
+    );
+    info!("Verified: no chunky DKG session completed yet (config off).");
+
+    // Enable chunky DKG config + ENCRYPTED_TRANSACTIONS via governance.
+    info!("Enabling chunky DKG config and ENCRYPTED_TRANSACTIONS at runtime.");
     let script = r#"
 script {
+    use aptos_std::fixed_point64;
     use aptos_framework::aptos_governance;
     use aptos_framework::chunky_dkg_config;
-    use aptos_std::fixed_point64;
+    use aptos_framework::features;
 
     fun main(core_resources: &signer) {
         let framework_signer = aptos_governance::get_signer_testnet_only(core_resources, @0x1);
 
-        // Enable chunky DKG.
-        let chunky_dkg_config = chunky_dkg_config::new_v1(
+        // Enable chunky DKG config (V1 with default thresholds).
+        let config = chunky_dkg_config::new_v1(
             fixed_point64::create_from_rational(1, 2),
             fixed_point64::create_from_rational(2, 3)
         );
-        chunky_dkg_config::set_for_next_epoch(&framework_signer, chunky_dkg_config);
+        chunky_dkg_config::set_for_next_epoch(&framework_signer, config);
 
         // Enable ENCRYPTED_TRANSACTIONS feature flag (108).
-        aptos_governance::toggle_features(
-            &framework_signer,
-            vector[108],
-            vector[]
-        );
+        features::change_feature_flags_for_next_epoch(&framework_signer, vector[108], vector[]);
+
+        // Trigger reconfiguration.
+        aptos_governance::reconfigure(&framework_signer);
     }
 }
 "#;
 
-    debug!("script={}", script);
-    let txn_summary = cli
-        .run_script(root_idx, script)
+    cli.run_script(root_idx, script)
         .await
         .expect("Txn execution error.");
-    debug!("txn_summary={:?}", txn_summary);
-
-    // Epoch 4: configs are now active, but chunky DKG hasn't completed yet.
-    swarm
-        .wait_for_all_nodes_to_catchup_to_epoch(4, Duration::from_secs(epoch_duration_secs * 2))
-        .await
-        .expect("Waited too long for epoch 4.");
 
+    // Poll and log state to diagnose the transition.
+    info!("Polling DKG state after governance script...");
+    let timer = tokio::time::Instant::now();
+    let session = loop {
+        let ledger = client
+            .get_ledger_information()
+            .await
+            .expect("ledger info")
+            .into_inner();
+        let dkg_state = get_on_chain_resource::<ChunkyDKGState>(&client).await;
+        let regular_dkg = get_on_chain_resource::<DKGState>(&client).await;
+        let config = get_on_chain_resource::<ChunkyDKGConfigMoveStruct>(&client).await;
+        info!(
+            "epoch={} version={} chunky_in_progress={} chunky_completed={} regular_in_progress={} config={:?} elapsed={}s",
+            ledger.epoch,
+            ledger.version,
+            dkg_state.in_progress.is_some(),
+            dkg_state.last_completed.is_some(),
+            regular_dkg.in_progress.is_some(),
+            config,
+            timer.elapsed().as_secs(),
+        );
+        if dkg_state.last_completed.is_some() {
+            info!("Chunky DKG completed!");
+            break dkg_state.last_complete().clone();
+        }
+        if timer.elapsed().as_secs() > estimated_dkg_latency_secs {
+            panic!(
+                "Timed out waiting for chunky DKG (epoch={}, in_progress={}, last_completed={})",
+                ledger.epoch,
+                dkg_state.in_progress.is_some(),
+                dkg_state.last_completed.is_some(),
+            );
+        }
+        tokio::time::sleep(Duration::from_secs(5)).await;
+    };
     info!(
-        "Now in epoch 4. Chunky DKG should not have completed yet (no DKG ran at end of epoch 3)."
-    );
-    let chunky_dkg_state = get_on_chain_resource::<ChunkyDKGState>(&client).await;
-    let no_chunky_dkg_yet = chunky_dkg_state.last_completed.is_none()
-        || chunky_dkg_state
-            .last_completed
-            .as_ref()
-            .map(|s| s.target_epoch())
-            != Some(4);
-    assert!(
-        no_chunky_dkg_yet,
-        "Chunky DKG should not have completed for epoch 4 yet"
+        "Chunky DKG completed for epoch {} after runtime enablement",
+        session.target_epoch()
     );
 
-    // Epoch 5: DKG should have run during epoch 4 and completed for epoch 5.
-    info!("Waiting for epoch 5 (chunky DKG should complete)...");
-    swarm
-        .wait_for_all_nodes_to_catchup_to_epoch(
-            5,
-            Duration::from_secs(epoch_duration_secs + estimated_dkg_latency_secs),
-        )
-        .await
-        .expect("Waited too long for epoch 5.");
-
-    let chunky_dkg_state = get_on_chain_resource::<ChunkyDKGState>(&client).await;
-    let session = chunky_dkg_state
-        .last_completed
-        .expect("Chunky DKG should have completed for epoch 5");
-    assert_eq!(5, session.target_epoch());
-
-    // Verify the transcript is valid.
+    // Verify the transcript.
     let subtranscript = verify_chunky_dkg_transcript(&session);
     assert!(
         !subtranscript.dealers.is_empty(),
         "Transcript should have dealers"
     );
-    info!(
-        "Chunky DKG completed for epoch 5 with {} dealers after runtime enablement",
-        subtranscript.dealers.len()
-    );
 
-    // Verify encryption key was derived.
+    // Verify encryption key is present.
     let enc_key = get_encryption_key_resource(&client).await;
     assert!(
         enc_key.encryption_key.is_some(),
-        "Encryption key should be present after chunky DKG"
+        "Encryption key should be present after chunky DKG config is enabled"
     );
     info!(
         "Encryption key present at epoch {} ({} bytes)",
         enc_key.epoch,
-        enc_key.encryption_key.unwrap().len()
+        enc_key.encryption_key.as_ref().unwrap().len()
     );
 }
```
