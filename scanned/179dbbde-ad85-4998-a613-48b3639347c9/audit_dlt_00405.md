# [?] fix: avoid panic on partial chunk request for genesis chunk (#16141)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-07-30
Source: https://github.com/near/nearcore/commit/556282637959c23a0bb50c33299fc55d542c6833
Type: security-commit

## Details
fix: avoid panic on partial chunk request for genesis chunk (#16141)

Any peer can ask for the genesis chunk by hash, and that used to panic
the node: the code asserts the receipts root it recomputes matches the
one in the chunk header, but genesis headers store an empty root.
Now return an error instead of asserting.

## Patch
### chain/chunks/src/logic.rs
```diff
@@ -1,4 +1,5 @@
 use near_chain::ChainStoreAccess;
+use near_chain::near_chain_primitives::Error as ChainError;
 use near_chain::{BlockHeader, Chain, ChainStore, types::EpochManagerAdapter};
 use near_chunks_primitives::Error;
 use near_epoch_manager::shard_tracker::ShardTracker;
@@ -77,7 +78,7 @@ pub fn make_outgoing_receipts_proofs(
     chunk_header: &ShardChunkHeader,
     outgoing_receipts: Vec<Receipt>,
     epoch_manager: &dyn EpochManagerAdapter,
-) -> Result<Vec<ReceiptProof>, EpochError> {
+) -> Result<Vec<ReceiptProof>, ChainError> {
     let shard_id = chunk_header.shard_id();
     let shard_layout =
         epoch_manager.get_shard_layout_from_prev_block(chunk_header.prev_block_hash())?;
@@ -86,7 +87,12 @@ pub fn make_outgoing_receipts_proofs(
         shard_id,
         outgoing_receipts,
     )?;
-    assert_eq!(chunk_header.prev_outgoing_receipts_root(), &root);
+    if chunk_header.prev_outgoing_receipts_root() != &root {
+        // Genesis chunks store CryptoHash::default() here while a recomputed root is
+        // always non-default, so this fires for any peer asking for a genesis chunk
+        // by hash. Must return Err rather than panic since this path is unauthenticated.
+        return Err(ChainError::InvalidChunkReceiptsRoot);
+    }
     Ok(receipt_proofs)
 }
 
@@ -202,3 +208,29 @@ pub fn persist_chunk(
     }
     update.commit().map_err(Error::from)
 }
+
+#[cfg(test)]
+mod test {
+    use super::*;
+    use crate::test_utils::ChunkTestFixture;
+    use assert_matches::assert_matches;
+    use near_primitives::sharding::ShardChunkHeader;
+    use near_primitives::types::EpochId;
+
+    #[test]
+    fn make_outgoing_receipts_proofs_returns_err_on_root_mismatch() {
+        let fixture = ChunkTestFixture::default();
+        let shard_id = fixture
+            .epoch_manager
+            .get_shard_layout(&EpochId::default())
+            .unwrap()
+            .shard_ids()
+            .next()
+            .unwrap();
+        let header = ShardChunkHeader::new_dummy(0, shard_id, CryptoHash::default());
+
+        let result = make_outgoing_receipts_proofs(&header, vec![], &fixture.epoch_manager);
+
+        assert_matches!(result, Err(ChainError::InvalidChunkReceiptsRoot));
+    }
+}
```

### test-loop-tests/src/tests/genesis_chunk_request.rs
```diff
@@ -0,0 +1,65 @@
+use crate::setup::builder::TestLoopBuilder;
+use crate::setup::peer_manager_actor::HandlerResult;
+use near_async::messaging::CanSend;
+use near_async::time::Duration;
+use near_network::shards_manager::ShardsManagerRequestFromNetwork;
+use near_network::types::{NetworkRequests, NetworkResponses, PartialEncodedChunkRequestMsg};
+use near_o11y::testonly::init_test_logger;
+use near_primitives::hash::CryptoHash;
+use parking_lot::Mutex;
+use std::collections::HashSet;
+use std::sync::Arc;
+
+/// A peer-supplied PartialEncodedChunkRequest for the genesis
+/// chunk used to panic on a receipts-root assert (genesis stores
+/// CryptoHash::default(); the recomputed root is non-default).
+#[test]
+fn test_genesis_chunk_request_does_not_panic() {
+    init_test_logger();
+
+    let mut env = TestLoopBuilder::new().build();
+
+    let response_seen = Arc::new(Mutex::new(None));
+    let response_seen_handler = response_seen.clone();
+    let peer_handle = env.node_datas[0].peer_manager_sender.actor_handle();
+    let peer_actor = env.test_loop.data.get_mut(&peer_handle);
+    peer_actor.register_override_handler(Box::new(move |request| match request {
+        NetworkRequests::PartialEncodedChunkResponse { response, .. } => {
+            *response_seen_handler.lock() = Some(response);
+            HandlerResult::Handled(NetworkResponses::NoResponse)
+        }
+        _ => HandlerResult::Unhandled(request),
+    }));
+
+    let genesis_chunk_hash = env
+        .validator()
+        .client()
+        .chain
+        .genesis_block()
+        .chunks()
+        .iter_raw()
+        .next()
+        .unwrap()
+        .chunk_hash()
+        .clone();
+
+    let request = PartialEncodedChunkRequestMsg {
+        chunk_hash: genesis_chunk_hash.clone(),
+        part_ords: vec![0],
+        tracking_shards: HashSet::new(),
+    };
+    env.node_datas[0].shards_manager_sender.send(
+        ShardsManagerRequestFromNetwork::ProcessPartialEncodedChunkRequest {
+            partial_encoded_chunk_request: request,
+            route_back: CryptoHash::default(),
+        },
+    );
+
+    env.test_loop.run_for(Duration::seconds(1));
+
+    let response =
+        response_seen.lock().take().expect("expected response for genesis chunk request");
+    assert_eq!(response.chunk_hash, genesis_chunk_hash);
+    assert!(response.parts.is_empty(), "expected no parts for genesis chunk response");
+    assert!(response.receipts.is_empty(), "expected no receipts for genesis chunk response");
+}
```

### test-loop-tests/src/tests/mod.rs
```diff
@@ -33,6 +33,7 @@ mod fix_chunk_producer_stake_threshold;
 mod fix_stake_threshold;
 mod garbage_collection;
 mod gas_keys;
+mod genesis_chunk_request;
 mod global_contracts;
 mod global_contracts_distribution;
 mod in_memory_tries;
```
