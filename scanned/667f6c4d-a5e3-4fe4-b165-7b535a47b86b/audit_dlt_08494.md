# [?] Fix crash of synced parachain node run with `--sync=warp` (#3523)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2024-03-01
Source: https://github.com/paritytech/polkadot-sdk/commit/a1b57a8c181bc39b254ff4d6d774f6ff348e509d
Type: security-commit

## Details
Fix crash of synced parachain node run with `--sync=warp` (#3523)

Fixes https://github.com/paritytech/polkadot-sdk/issues/3496.

## Patch
### prdoc/pr_3523.prdoc
```diff
@@ -0,0 +1,19 @@
+title: Fix crash of synced parachain node run with `--sync=warp`
+
+doc:
+  - audience: Node Operator
+    description: |
+      Fix crash of `SyncingEngine` when an already synced parachain node is run with `--sync=warp`
+      (issue https://github.com/paritytech/polkadot-sdk/issues/3496).
+      The issue manifests itself by errors in the logs:
+      ```
+      [Parachain] Cannot set warp sync target block: no warp sync strategy is active.
+      [Parachain] Failed to set warp sync target block header, terminating `SyncingEngine`.
+      ```
+      Followed by a stream of messages:
+      ```
+      [Parachain] Protocol command streams have been shut down
+      ```
+
+crates:
+  - name: sc-network-sync
```

### substrate/client/network/sync/src/engine.rs
```diff
@@ -656,6 +656,8 @@ where
 					Some(event) => self.process_notification_event(event),
 					None => return,
 				},
+				// TODO: setting of warp sync target block should be moved to the initialization of
+				// `SyncingEngine`, see https://github.com/paritytech/polkadot-sdk/issues/3537.
 				warp_target_block_header = &mut self.warp_sync_target_block_header_rx_fused => {
 					if let Err(_) = self.pass_warp_sync_target_block_header(warp_target_block_header) {
 						error!(
```

### substrate/client/network/sync/src/strategy.rs
```diff
@@ -30,7 +30,7 @@ use crate::{
 };
 use chain_sync::{ChainSync, ChainSyncAction, ChainSyncMode};
 use libp2p::PeerId;
-use log::{debug, error, info};
+use log::{debug, error, info, warn};
 use prometheus_endpoint::Registry;
 use sc_client_api::{BlockBackend, ProofProvider};
 use sc_consensus::{BlockImportError, BlockImportStatus, IncomingBlock};
@@ -159,7 +159,7 @@ impl<B: BlockT> From<ChainSyncAction<B>> for SyncingAction<B> {
 
 /// Proxy to specific syncing strategies.
 pub struct SyncingStrategy<B: BlockT, Client> {
-	/// Syncing configuration.
+	/// Initial syncing configuration.
 	config: SyncingConfig,
 	/// Client used by syncing strategies.
 	client: Arc<Client>,
@@ -466,15 +466,27 @@ where
 		&mut self,
 		target_header: B::Header,
 	) -> Result<(), ()> {
-		match self.warp {
-			Some(ref mut warp) => {
-				warp.set_target_block(target_header);
-				Ok(())
+		match self.config.mode {
+			SyncMode::Warp => match self.warp {
+				Some(ref mut warp) => {
+					warp.set_target_block(target_header);
+					Ok(())
+				},
+				None => {
+					// As mode is set to warp sync, but no warp sync strategy is active, this means
+					// that warp sync has already finished / was skipped.
+					warn!(
+						target: LOG_TARGET,
+						"Discarding warp sync target, as warp sync was seemingly skipped due \
+						 to node being (partially) synced.",
+					);
+					Ok(())
+				},
 			},
-			None => {
+			_ => {
 				error!(
 					target: LOG_TARGET,
-					"Cannot set warp sync target block: no warp sync strategy is active."
+					"Cannot set warp sync target block: not in warp sync mode."
 				);
 				debug_assert!(false);
 				Err(())
@@ -587,3 +599,63 @@ where
 		}
 	}
 }
+
+#[cfg(test)]
+mod test {
+	use super::*;
+	use futures::executor::block_on;
+	use sc_block_builder::BlockBuilderBuilder;
+	use substrate_test_runtime_client::{
+		ClientBlockImportExt, ClientExt, DefaultTestClientBuilderExt, TestClientBuilder,
+		TestClientBuilderExt,
+	};
+
+	/// Regression test for crash when starting already synced parachain node with `--sync=warp`.
+	/// We must remove this after setting of warp sync target block is moved to initialization of
+	/// `SyncingEngine` (issue https://github.com/paritytech/polkadot-sdk/issues/3537).
+	#[test]
+	fn set_target_block_finished_warp_sync() {
+		// Populate database with finalized state.
+		let mut client = Arc::new(TestClientBuilder::new().build());
+		let block = BlockBuilderBuilder::new(&*client)
+			.on_parent_block(client.chain_info().best_hash)
+			.with_parent_block_number(client.chain_info().best_number)
+			.build()
+			.unwrap()
+			.build()
+			.unwrap()
+			.block;
+		block_on(client.import(BlockOrigin::Own, block.clone())).unwrap();
+		let just = (*b"TEST", Vec::new());
+		client.finalize_block(block.hash(), Some(just)).unwrap();
+		let target_block = BlockBuilderBuilder::new(&*client)
+			.on_parent_block(client.chain_info().best_hash)
+			.with_parent_block_number(client.chain_info().best_number)
+			.build()
+			.unwrap()
+			.build()
+			.unwrap()
+			.block;
+
+		// Initialize syncing strategy.
+		let config = SyncingConfig {
+			mode: SyncMode::Warp,
+			max_parallel_downloads: 3,
+			max_blocks_per_request: 64,
+			metrics_registry: None,
+		};
+		let mut strategy =
+			SyncingStrategy::new(config, client, Some(WarpSyncConfig::WaitForTarget)).unwrap();
+
+		// Warp sync instantly finishes as we have finalized state in DB.
+		let actions = strategy.actions().unwrap();
+		assert_eq!(actions.len(), 1);
+		assert!(matches!(actions[0], SyncingAction::Finished));
+		assert!(strategy.warp.is_none());
+
+		// Try setting the target block. We mustn't crash.
+		strategy
+			.set_warp_sync_target_block_header(target_block.header().clone())
+			.unwrap();
+	}
+}
```
