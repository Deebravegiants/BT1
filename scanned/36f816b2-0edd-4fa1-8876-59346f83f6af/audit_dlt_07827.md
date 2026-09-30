# [?] Reduce size of futures in HTTP API to prevent stack overflows (#5104)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-01-23
Source: https://github.com/sigp/lighthouse/commit/a403138ed02f981143f41d53c24e2cae0af07baa
Type: security-commit

## Details
Reduce size of futures in HTTP API to prevent stack overflows (#5104)

* Box::pin a few big futures

* Arc the blocks early in publication

* Fix more tests

## Patch
### beacon_node/beacon_chain/src/block_verification.rs
```diff
@@ -722,7 +722,7 @@ impl<T: BeaconChainTypes> IntoGossipVerifiedBlockContents<T> for PublishBlockReq
                 Ok::<_, BlockContentsError<T::EthSpec>>(gossip_verified_blobs)
             })
             .transpose()?;
-        let gossip_verified_block = GossipVerifiedBlock::new(Arc::new(block), chain)?;
+        let gossip_verified_block = GossipVerifiedBlock::new(block, chain)?;
 
         Ok((gossip_verified_block, gossip_verified_blobs))
     }
```

### beacon_node/beacon_chain/src/data_availability_checker/overflow_lru_cache.rs
```diff
@@ -952,7 +952,7 @@ mod test {
         };
 
         let availability_pending_block = AvailabilityPendingExecutedBlock {
-            block: Arc::new(block),
+            block,
             import_data,
             payload_verification_outcome,
         };
```

### beacon_node/beacon_chain/src/test_utils.rs
```diff
@@ -822,7 +822,7 @@ where
         slot: Slot,
     ) -> (SignedBlindedBeaconBlock<E>, BeaconState<E>) {
         let (unblinded, new_state) = self.make_block(state, slot).await;
-        (unblinded.0.into(), new_state)
+        ((*unblinded.0).clone().into(), new_state)
     }
 
     /// Returns a newly created block, signed by the proposer for the given slot.
@@ -866,14 +866,14 @@ where
             panic!("Should always be a full payload response");
         };
 
-        let signed_block = block_response.block.sign(
+        let signed_block = Arc::new(block_response.block.sign(
             &self.validator_keypairs[proposer_index].sk,
             &block_response.state.fork(),
             block_response.state.genesis_validators_root(),
             &self.spec,
-        );
+        ));
 
-        let block_contents: SignedBlockContentsTuple<E> = match &signed_block {
+        let block_contents: SignedBlockContentsTuple<E> = match *signed_block {
             SignedBeaconBlock::Base(_)
             | SignedBeaconBlock::Altair(_)
             | SignedBeaconBlock::Merge(_)
@@ -928,14 +928,14 @@ where
             panic!("Should always be a full payload response");
         };
 
-        let signed_block = block_response.block.sign(
+        let signed_block = Arc::new(block_response.block.sign(
             &self.validator_keypairs[proposer_index].sk,
             &block_response.state.fork(),
             block_response.state.genesis_validators_root(),
             &self.spec,
-        );
+        ));
 
-        let block_contents: SignedBlockContentsTuple<E> = match &signed_block {
+        let block_contents: SignedBlockContentsTuple<E> = match *signed_block {
             SignedBeaconBlock::Base(_)
             | SignedBeaconBlock::Altair(_)
             | SignedBeaconBlock::Merge(_)
@@ -1742,7 +1742,7 @@ where
 
         let ((block, blobs), state) = self.make_block_return_pre_state(state, slot).await;
 
-        let (mut block, _) = block.deconstruct();
+        let (mut block, _) = (*block).clone().deconstruct();
 
         block_modifier(&mut block);
 
@@ -1754,7 +1754,7 @@ where
             state.genesis_validators_root(),
             &self.spec,
         );
-        ((signed_block, blobs), state)
+        ((Arc::new(signed_block), blobs), state)
     }
 
     pub async fn make_blob_with_modifier(
@@ -1768,7 +1768,7 @@ where
 
         let ((block, mut blobs), state) = self.make_block_return_pre_state(state, slot).await;
 
-        let (block, _) = block.deconstruct();
+        let (block, _) = (*block).clone().deconstruct();
 
         blob_modifier(&mut blobs.as_mut().unwrap().1);
 
@@ -1780,7 +1780,7 @@ where
             state.genesis_validators_root(),
             &self.spec,
         );
-        ((signed_block, blobs), state)
+        ((Arc::new(signed_block), blobs), state)
     }
 
     pub fn make_deposits<'a>(
@@ -1873,7 +1873,7 @@ where
             .chain
             .process_block(
                 block_root,
-                RpcBlock::new(Some(block_root), Arc::new(block), sidecars).unwrap(),
+                RpcBlock::new(Some(block_root), block, sidecars).unwrap(),
                 NotifyExecutionLayer::Yes,
                 || Ok(()),
             )
@@ -1899,7 +1899,7 @@ where
             .chain
             .process_block(
                 block_root,
-                RpcBlock::new(Some(block_root), Arc::new(block), sidecars).unwrap(),
+                RpcBlock::new(Some(block_root), block, sidecars).unwrap(),
                 NotifyExecutionLayer::Yes,
                 || Ok(()),
             )
```

### beacon_node/beacon_chain/tests/block_verification.rs
```diff
@@ -1142,11 +1142,7 @@ async fn verify_block_for_gossip_slashing_detection() {
     let ((block1, blobs1), _) = harness.make_block(state.clone(), Slot::new(1)).await;
     let ((block2, _blobs2), _) = harness.make_block(state, Slot::new(1)).await;
 
-    let verified_block = harness
-        .chain
-        .verify_block_for_gossip(Arc::new(block1))
-        .await
-        .unwrap();
+    let verified_block = harness.chain.verify_block_for_gossip(block1).await.unwrap();
 
     if let Some((kzg_proofs, blobs)) = blobs1 {
         let sidecars =
@@ -1174,12 +1170,7 @@ async fn verify_block_for_gossip_slashing_detection() {
         )
         .await
         .unwrap();
-    unwrap_err(
-        harness
-            .chain
-            .verify_block_for_gossip(Arc::new(block2))
-            .await,
-    );
+    unwrap_err(harness.chain.verify_block_for_gossip(block2).await);
 
     // Slasher should have been handed the two conflicting blocks and crafted a slashing.
     slasher.process_queued(Epoch::new(0)).unwrap();
@@ -1198,11 +1189,7 @@ async fn verify_block_for_gossip_doppelganger_detection() {
     let state = harness.get_current_state();
     let ((block, _), _) = harness.make_block(state.clone(), Slot::new(1)).await;
 
-    let verified_block = harness
-        .chain
-        .verify_block_for_gossip(Arc::new(block))
-        .await
-        .unwrap();
+    let verified_block = harness.chain.verify_block_for_gossip(block).await.unwrap();
     let attestations = verified_block.block.message().body().attestations().clone();
     harness
         .chain
@@ -1564,7 +1551,6 @@ async fn import_duplicate_block_unrealized_justification() {
     let slot = harness.get_current_slot();
     let (block_contents, _) = harness.make_block(state.clone(), slot).await;
     let (block, _) = block_contents;
-    let block = Arc::new(block);
     let block_root = block.canonical_root();
 
     // Create two verified variants of the block, representing the same block being processed in
```

### beacon_node/beacon_chain/tests/payload_invalidation.rs
```diff
@@ -319,7 +319,7 @@ impl InvalidPayloadRig {
                         .get_full_block(&block_root)
                         .unwrap()
                         .unwrap(),
-                    block,
+                    *block,
                     "block from db must match block imported"
                 );
             }
@@ -700,7 +700,7 @@ async fn invalidates_all_descendants() {
         .chain
         .process_block(
             fork_block.canonical_root(),
-            Arc::new(fork_block),
+            fork_block,
             NotifyExecutionLayer::Yes,
             || Ok(()),
         )
@@ -800,7 +800,7 @@ async fn switches_heads() {
         .chain
         .process_block(
             fork_block.canonical_root(),
-            Arc::new(fork_block),
+            fork_block,
             NotifyExecutionLayer::Yes,
             || Ok(()),
         )
@@ -1044,8 +1044,7 @@ async fn invalid_parent() {
     // Produce another block atop the parent, but don't import yet.
     let slot = parent_block.slot() + 1;
     rig.harness.set_current_slot(slot);
-    let (block_tuple, state) = rig.harness.make_block(parent_state, slot).await;
-    let block = Arc::new(block_tuple.0);
+    let ((block, _), state) = rig.harness.make_block(parent_state, slot).await;
     let block_root = block.canonical_root();
     assert_eq!(block.parent_root(), parent_root);
 
@@ -1865,7 +1864,7 @@ impl InvalidHeadSetup {
                     .state_at_slot(slot - 1, StateSkipConfig::WithStateRoots)
                     .unwrap();
                 let (fork_block_tuple, _) = rig.harness.make_block(parent_state, slot).await;
-                opt_fork_block = Some(Arc::new(fork_block_tuple.0));
+                opt_fork_block = Some(fork_block_tuple.0);
             } else {
                 // Skipped slot.
             };
```

### beacon_node/beacon_chain/tests/store_tests.rs
```diff
@@ -2268,17 +2268,17 @@ async fn garbage_collect_temp_states_from_failed_block() {
         let block_slot = Slot::new(2 * slots_per_epoch);
         let ((signed_block, _), state) = harness.make_block(genesis_state, block_slot).await;
 
-        let (mut block, _) = signed_block.deconstruct();
+        let (mut block, _) = (*signed_block).clone().deconstruct();
 
         // Mutate the block to make it invalid, and re-sign it.
         *block.state_root_mut() = Hash256::repeat_byte(0xff);
         let proposer_index = block.proposer_index() as usize;
-        let block = block.sign(
+        let block = Arc::new(block.sign(
             &harness.validator_keypairs[proposer_index].sk,
             &state.fork(),
             state.genesis_validators_root(),
             &harness.spec,
-        );
+        ));
 
         // The block should be rejected, but should store a bunch of temporary states.
         harness.set_current_slot(block_slot);
@@ -2677,7 +2677,7 @@ async fn process_blocks_and_attestations_for_unaligned_checkpoint() {
         .chain
         .process_block(
             invalid_fork_block.canonical_root(),
-            Arc::new(invalid_fork_block.clone()),
+            invalid_fork_block.clone(),
             NotifyExecutionLayer::Yes,
             || Ok(()),
         )
@@ -2690,7 +2690,7 @@ async fn process_blocks_and_attestations_for_unaligned_checkpoint() {
         .chain
         .process_block(
             valid_fork_block.canonical_root(),
-            Arc::new(valid_fork_block.clone()),
+            valid_fork_block.clone(),
             NotifyExecutionLayer::Yes,
             || Ok(()),
         )
```

### beacon_node/http_api/src/lib.rs
```diff
@@ -1410,7 +1410,7 @@ pub fn serve<T: BeaconChainTypes>(
         .and(network_tx_filter.clone())
         .and(log_filter.clone())
         .then(
-            move |block_contents: SignedBlindedBeaconBlock<T::EthSpec>,
+            move |block_contents: Arc<SignedBlindedBeaconBlock<T::EthSpec>>,
                   task_spawner: TaskSpawner<T::EthSpec>,
                   chain: Arc<BeaconChain<T>>,
                   network_tx: UnboundedSender<NetworkMessage<T::EthSpec>>,
@@ -1450,6 +1450,7 @@ pub fn serve<T: BeaconChainTypes>(
                         &block_bytes,
                         &chain.spec,
                     )
+                    .map(Arc::new)
                     .map_err(|e| {
                         warp_utils::reject::custom_bad_request(format!("invalid SSZ: {e:?}"))
                     })?;
@@ -1478,7 +1479,7 @@ pub fn serve<T: BeaconChainTypes>(
         .and(log_filter.clone())
         .then(
             move |validation_level: api_types::BroadcastValidationQuery,
-                  blinded_block: SignedBlindedBeaconBlock<T::EthSpec>,
+                  blinded_block: Arc<SignedBlindedBeaconBlock<T::EthSpec>>,
                   task_spawner: TaskSpawner<T::EthSpec>,
                   chain: Arc<BeaconChain<T>>,
                   network_tx: UnboundedSender<NetworkMessage<T::EthSpec>>,
@@ -1519,6 +1520,7 @@ pub fn serve<T: BeaconChainTypes>(
                         &block_bytes,
                         &chain.spec,
                     )
+                    .map(Arc::new)
                     .map_err(|e| {
                         warp_utils::reject::custom_bad_request(format!("invalid SSZ: {e:?}"))
                     })?;
```

### beacon_node/http_api/src/publish_blocks.rs
```diff
@@ -194,7 +194,7 @@ pub async fn publish_block<T: BeaconChainTypes, B: IntoGossipVerifiedBlockConten
 
     if let Some(gossip_verified_blobs) = gossip_verified_blobs {
         for blob in gossip_verified_blobs {
-            if let Err(e) = chain.process_gossip_blob(blob).await {
+            if let Err(e) = Box::pin(chain.process_gossip_blob(blob)).await {
                 let msg = format!("Invalid blob: {e}");
                 return if let BroadcastValidation::Gossip = validation_level {
                     Err(warp_utils::reject::broadcast_without_import(msg))
@@ -210,14 +210,13 @@ pub async fn publish_block<T: BeaconChainTypes, B: IntoGossipVerifiedBlockConten
         }
     }
 
-    match chain
-        .process_block(
-            block_root,
-            gossip_verified_block,
-            NotifyExecutionLayer::Yes,
-            publish_fn,
-        )
-        .await
+    match Box::pin(chain.process_block(
+        block_root,
+        gossip_verified_block,
+        NotifyExecutionLayer::Yes,
+        publish_fn,
+    ))
+    .await
     {
         Ok(AvailabilityProcessingStatus::Imported(root)) => {
             info!(
@@ -291,7 +290,7 @@ pub async fn publish_block<T: BeaconChainTypes, B: IntoGossipVerifiedBlockConten
 /// Handles a request from the HTTP API for blinded blocks. This converts blinded blocks into full
 /// blocks before publishing.
 pub async fn publish_blinded_block<T: BeaconChainTypes>(
-    blinded_block: SignedBlindedBeaconBlock<T::EthSpec>,
+    blinded_block: Arc<SignedBlindedBeaconBlock<T::EthSpec>>,
     chain: Arc<BeaconChain<T>>,
     network_tx: &UnboundedSender<NetworkMessage<T::EthSpec>>,
     log: Logger,
@@ -319,7 +318,7 @@ pub async fn publish_blinded_block<T: BeaconChainTypes>(
 pub async fn reconstruct_block<T: BeaconChainTypes>(
     chain: Arc<BeaconChain<T>>,
     block_root: Hash256,
-    block: SignedBlindedBeaconBlock<T::EthSpec>,
+    block: Arc<SignedBlindedBeaconBlock<T::EthSpec>>,
     log: Logger,
 ) -> Result<ProvenancedBlock<T, PublishBlockRequest<T::EthSpec>>, Rejection> {
     let full_payload_opt = if let Ok(payload_header) = block.message().body().execution_payload() {
@@ -380,6 +379,10 @@ pub async fn reconstruct_block<T: BeaconChainTypes>(
         None
     };
 
+    // Perf: cloning the block here to unblind it is a little sub-optimal. This is considered an
+    // acceptable tradeoff to avoid passing blocks around on the stack (unarced), which blows up
+    // the size of futures.
+    let block = (*block).clone();
     match full_payload_opt {
         // A block without a payload is pre-merge and we consider it locally
         // built.
```

### beacon_node/http_api/tests/broadcast_validation_tests.rs
```diff
@@ -3,7 +3,7 @@ use beacon_chain::{
     GossipVerifiedBlock, IntoGossipVerifiedBlockContents,
 };
 use eth2::reqwest::StatusCode;
-use eth2::types::{BroadcastValidation, PublishBlockRequest, SignedBeaconBlock};
+use eth2::types::{BroadcastValidation, PublishBlockRequest};
 use http_api::test_utils::InteractiveTester;
 use http_api::{publish_blinded_block, publish_block, reconstruct_block, ProvenancedBlock};
 use std::sync::Arc;
@@ -63,7 +63,7 @@ pub async fn gossip_invalid() {
 
     tester.harness.advance_slot();
 
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(chain_state_before, slot, |b| {
             *b.state_root_mut() = Hash256::zero();
@@ -115,7 +115,7 @@ pub async fn gossip_partial_pass() {
 
     tester.harness.advance_slot();
 
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(chain_state_before, slot, |b| {
             *b.state_root_mut() = Hash256::random()
@@ -161,8 +161,7 @@ pub async fn gossip_full_pass() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) =
-        tester.harness.make_block(state_a, slot_b).await;
+    let ((block, blobs), _) = tester.harness.make_block(state_a, slot_b).await;
 
     let response: Result<(), eth2::Error> = tester
         .client
@@ -252,7 +251,7 @@ pub async fn consensus_invalid() {
 
     tester.harness.advance_slot();
 
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(chain_state_before, slot, |b| {
             *b.state_root_mut() = Hash256::zero();
@@ -304,7 +303,7 @@ pub async fn consensus_gossip() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(state_a, slot_b, |b| *b.state_root_mut() = Hash256::zero())
         .await;
@@ -418,8 +417,7 @@ pub async fn consensus_full_pass() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) =
-        tester.harness.make_block(state_a, slot_b).await;
+    let ((block, blobs), _) = tester.harness.make_block(state_a, slot_b).await;
 
     let response: Result<(), eth2::Error> = tester
         .client
@@ -465,7 +463,7 @@ pub async fn equivocation_invalid() {
 
     tester.harness.advance_slot();
 
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(chain_state_before, slot, |b| {
             *b.state_root_mut() = Hash256::zero();
@@ -518,10 +516,9 @@ pub async fn equivocation_consensus_early_equivocation() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block_a, blobs_a), state_after_a): ((SignedBeaconBlock<E>, _), _) =
+    let ((block_a, blobs_a), state_after_a) =
         tester.harness.make_block(state_a.clone(), slot_b).await;
-    let ((block_b, blobs_b), state_after_b): ((SignedBeaconBlock<E>, _), _) =
-        tester.harness.make_block(state_a, slot_b).await;
+    let ((block_b, blobs_b), state_after_b) = tester.harness.make_block(state_a, slot_b).await;
 
     /* check for `make_block` curios */
     assert_eq!(block_a.state_root(), state_after_a.tree_hash_root());
@@ -590,7 +587,7 @@ pub async fn equivocation_gossip() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) = tester
+    let ((block, blobs), _) = tester
         .harness
         .make_block_with_modifier(state_a, slot_b, |b| *b.state_root_mut() = Hash256::zero())
         .await;
@@ -645,10 +642,9 @@ pub async fn equivocation_consensus_late_equivocation() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block_a, blobs_a), state_after_a): ((SignedBeaconBlock<E>, _), _) =
+    let ((block_a, blobs_a), state_after_a) =
         tester.harness.make_block(state_a.clone(), slot_b).await;
-    let ((block_b, blobs_b), state_after_b): ((SignedBeaconBlock<E>, _), _) =
-        tester.harness.make_block(state_a, slot_b).await;
+    let ((block_b, blobs_b), state_after_b) = tester.harness.make_block(state_a, slot_b).await;
 
     /* check for `make_block` curios */
     assert_eq!(block_a.state_root(), state_after_a.tree_hash_root());
@@ -716,8 +712,7 @@ pub async fn equivocation_full_pass() {
     let slot_b = slot_a + 1;
 
     let state_a = tester.harness.get_current_state();
-    let ((block, blobs), _): ((SignedBeaconBlock<E>, _), _) =
-        tester.harness.make_block(state_a, slot_b).await;
+    let ((block, blobs), _) = tester.harness.make_block(state_a, slot_b).await;
 
     let response: Result<(), eth2::Error> = tester
         .client
@@ -1269,6 +1264,7 @@ pub async fn blinded_equivocation_consensus_late_equivocation() {
         .make_blinded_block(state_a.clone(), slot_b)
         .await;
     let (block_b, state_after_b) = tester.harness.make_blinded_block(state_a, slot_b).await;
+    let block_b = Arc::new(block_b);
 
     /* check for `make_blinded_block` curios */
     assert_eq!(block_a.state_root(), state_after_a.tree_hash_root());
@@ -1278,7 +1274,7 @@ pub async fn blinded_equivocation_consensus_late_equivocation() {
     let unblinded_block_a = reconstruct_block(
         tester.harness.chain.clone(),
         block_a.canonical_root(),
-        block_a,
+        Arc::new(block_a),
         test_logger.clone(),
     )
     .await
@@ -1301,15 +1297,11 @@ pub async fn blinded_equivocation_consensus_late_equivocation() {
         ProvenancedBlock::Builder(b, _) => b,
     };
 
-    let gossip_block_b = GossipVerifiedBlock::new(
-        Arc::new(inner_block_b.clone().deconstruct().0),
-        &tester.harness.chain,
-    );
+    let gossip_block_b =
+        GossipVerifiedBlock::new(inner_block_b.clone().deconstruct().0, &tester.harness.chain);
     assert!(gossip_block_b.is_ok());
-    let gossip_block_a = GossipVerifiedBlock::new(
-        Arc::new(inner_block_a.clone().deconstruct().0),
-        &tester.harness.chain,
-    );
+    let gossip_block_a =
+        GossipVerifiedBlock::new(inner_block_a.clone().deconstruct().0, &tester.harness.chain);
     assert!(gossip_block_a.is_err());
 
     let channel = tokio::sync::mpsc::unbounded_channel();
```

### beacon_node/http_api/tests/interactive_tests.rs
```diff
@@ -632,7 +632,7 @@ pub async fn proposer_boost_re_org_test(
             panic!("Should not be a blinded block");
         }
     };
-    let block_c = harness.sign_beacon_block(unsigned_block_c, &state_b);
+    let block_c = Arc::new(harness.sign_beacon_block(unsigned_block_c, &state_b));
 
     if should_re_org {
         // Block C should build on A.
```

### beacon_node/http_api/tests/tests.rs
```diff
@@ -2597,7 +2597,7 @@ impl ApiTester {
 
             let signed_block = block.sign(&sk, &fork, genesis_validators_root, &self.chain.spec);
             let signed_block_contents =
-                PublishBlockRequest::try_from(signed_block.clone()).unwrap();
+                PublishBlockRequest::try_from(Arc::new(signed_block.clone())).unwrap();
 
             self.client
                 .post_beacon_blocks(&signed_block_contents)
@@ -2670,8 +2670,8 @@ impl ApiTester {
                 .unwrap();
 
             assert_eq!(
-                self.chain.head_beacon_block().as_ref(),
-                signed_block_contents.signed_block()
+                self.chain.head_beacon_block(),
+                *signed_block_contents.signed_block()
             );
 
             self.chain.slot_clock.set_slot(slot.as_u64() + 1);
@@ -2763,8 +2763,8 @@ impl ApiTester {
                         .unwrap();
 
                     assert_eq!(
-                        self.chain.head_beacon_block().as_ref(),
-                        signed_block_contents.signed_block()
+                        self.chain.head_beacon_block(),
+                        *signed_block_contents.signed_block()
                     );
 
                     self.chain.slot_clock.set_slot(slot.as_u64() + 1);
@@ -2994,7 +2994,7 @@ impl ApiTester {
                 .data;
 
             let signed_block = signed_block_contents.signed_block();
-            assert_eq!(&head_block, signed_block);
+            assert_eq!(head_block, **signed_block);
 
             self.chain.slot_clock.set_slot(slot.as_u64() + 1);
         }
```

### beacon_node/network/src/network_beacon_processor/tests.rs
```diff
@@ -250,7 +250,7 @@ impl TestRig {
         };
         Self {
             chain,
-            next_block: Arc::new(block),
+            next_block: block,
             next_blobs: blob_sidecars,
             attestations,
             next_block_attestations,
```
