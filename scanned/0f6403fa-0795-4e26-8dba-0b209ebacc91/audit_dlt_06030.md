# [?] fix(starfish): harden consensus against panic-inducing peer messages (#11202)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-09
Source: https://github.com/iotaledger/iota/commit/702e8f7c2ccb592bcbf7f2e3c386641372e6c026
Type: security-commit

## Details
fix(starfish): harden consensus against panic-inducing peer messages (#11202)

# Description of change

Replace panic paths with proper error propagation across peer-facing
Starfish code paths, hardening the node against malformed or malicious
messages from peers.

**Changes:**
- Replace `.expect()` with `?` on peer-triggered merkle/encoding
computations in authority service and commit syncer
- Validate authority indices from untrusted peer messages (block
bundles, block verifier, cordial knowledge)
- Replace `unimplemented!()` macro with gRPC `Status::unimplemented` in
deprecated RPC

## Links to any relevant issues

Fixes #11201

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### crates/starfish/core/src/authority_service.rs
```diff
@@ -196,12 +196,12 @@ impl<C: CoreThreadDispatcher> AuthorityService<C> {
             return Err(e);
         }
 
-        let (transaction_commitment, our_shard, proof_for_shard) = TransactionsCommitment::compute_merkle_root_shard_and_proof(
-            &serialized_transactions,
-            &self.context,
-            encoder,
-        )
-            .expect("we should expect correct computation of the transactions commitment, our shard and its proof");
+        let (transaction_commitment, our_shard, proof_for_shard) =
+            TransactionsCommitment::compute_merkle_root_shard_and_proof(
+                &serialized_transactions,
+                &self.context,
+                encoder,
+            )?;
         if signed_block_header.transactions_commitment() != transaction_commitment {
             return Err(ConsensusError::TransactionCommitmentFailure {
                 round: signed_block_header.round(),
@@ -608,6 +608,18 @@ impl<C: CoreThreadDispatcher> NetworkService for AuthorityService<C> {
         let peer_hostname = &self.context.committee.authority(peer).hostname;
         let mut serialized_block_bundle_parts =
             SerializedBlockBundleParts::try_from(serialized_block_bundle)?;
+        if let Err(e) =
+            serialized_block_bundle_parts.validate_useful_authorities(&self.context.committee)
+        {
+            self.context
+                .metrics
+                .node_metrics
+                .bundles_with_invalid_parts
+                .with_label_values(&[peer_hostname.as_str(), "metadata", e.name()])
+                .inc();
+            warn!("Invalid bundle metadata from {}: {}", peer, e);
+            return Err(e);
+        }
 
         // 1. Create a verified block and make some preliminary checks
         let (verified_block, shard_for_core) = self.create_verified_block_and_shard(
@@ -1452,12 +1464,12 @@ impl SubscriptionCounter {
 
     fn decrement(&self, peer: AuthorityIndex) -> Result<(), ConsensusError> {
         let mut counter = self.counter.lock();
-        counter.count -= 1;
-        let original_subscription_by_peer = counter.subscriptions_by_authority[peer];
-
         if counter.subscriptions_by_authority[peer] == 0 {
-            panic!("Subscription count for peer {peer} is already zero, cannot decrement");
+            warn!("Subscription count for peer {peer} is already zero, skipping decrement");
+            return Ok(());
         }
+        counter.count -= 1;
+        let original_subscription_by_peer = counter.subscriptions_by_authority[peer];
         counter.subscriptions_by_authority[peer] -= 1;
         let mut total_stake = 0;
         for (authority_index, _) in self.context.committee.authorities() {
@@ -2117,6 +2129,88 @@ mod tests {
         assert_eq!(block_headers, headers);
     }
 
+    #[tokio::test(flavor = "current_thread")]
+    async fn test_handle_subscribed_block_bundle_with_invalid_useful_authority_hints() {
+        let committee_size = 4;
+        let (context, _keys) = Context::new_for_test(committee_size);
+        let context = Arc::new(context);
+        let block_verifier = Arc::new(crate::block_verifier::NoopBlockVerifier {});
+        let commit_vote_monitor = Arc::new(CommitVoteMonitor::new(context.clone()));
+        let core_dispatcher = Arc::new(MockCoreThreadDispatcher::default());
+        let (_tx_block_broadcast, rx_block_broadcast) = broadcast::channel(100);
+        let (tx_message_sender, _tx_message_receiver) = mpsc::channel(100);
+
+        let network_client = Arc::new(FakeNetworkClient::default());
+        let store = Arc::new(MemStore::new(context.clone()));
+        let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
+        let cordial_knowledge = CordialKnowledge::start(context.clone(), dag_state.clone());
+        let transactions_synchronizer = TransactionsSynchronizer::start(
+            network_client.clone(),
+            context.clone(),
+            core_dispatcher.clone(),
+            dag_state.clone(),
+        );
+
+        let header_synchronizer = HeaderSynchronizer::start(
+            network_client.clone(),
+            context.clone(),
+            core_dispatcher.clone(),
+            commit_vote_monitor.clone(),
+            transactions_synchronizer.clone(),
+            block_verifier.clone(),
+            dag_state.clone(),
+            false,
+        );
+
+        let authority_service = Arc::new(AuthorityService::new(
+            context.clone(),
+            block_verifier,
+            commit_vote_monitor,
+            header_synchronizer,
+            transactions_synchronizer,
+            core_dispatcher.clone(),
+            rx_block_broadcast,
+            dag_state,
+            store,
+            tx_message_sender,
+            cordial_knowledge,
+        ));
+        let mut encoder = create_encoder(&context);
+
+        let input_block = VerifiedBlock::new_for_test(
+            TestBlockHeader::new_with_commitment(1, 0, &context, &mut encoder).build(),
+        );
+        let invalid_authority = AuthorityIndex::new_for_test(250);
+        let block_bundle = BlockBundle {
+            verified_block: input_block,
+            verified_headers: vec![],
+            serialized_shards: vec![],
+            useful_headers_authors: BTreeSet::from([invalid_authority]),
+            useful_shards_authors: BTreeSet::new(),
+        };
+        let serialized_block_bundle = SerializedBlockBundle::try_from(
+            SerializedBlockBundleParts::try_from(block_bundle).unwrap(),
+        )
+        .unwrap();
+
+        let result = authority_service
+            .handle_subscribed_block_bundle(
+                context.committee.to_authority_index(0).unwrap(),
+                serialized_block_bundle,
+                &mut encoder,
+            )
+            .await;
+
+        assert!(matches!(
+            result,
+            Err(ConsensusError::InvalidAuthorityIndex { index, max })
+                if index == invalid_authority && max == committee_size
+        ));
+        assert!(core_dispatcher.get_blocks().is_empty());
+        assert!(core_dispatcher.get_block_headers().is_empty());
+        assert_eq!(authority_service.received_block_headers.size(), 0);
+    }
+
     #[tokio::test(flavor = "current_thread", start_paused = true)]
     async fn test_handle_fetch_latest_block_headers() {
         // GIVEN
```

### crates/starfish/core/src/block_header.rs
```diff
@@ -595,15 +595,13 @@ impl TransactionsCommitment {
     ) -> ConsensusResult<TransactionsCommitment> {
         let info_length = context.committee.info_length();
         let parity_length = context.committee.size() - info_length;
-        let encoded_shards = encoder
-            .encode_serialized_data(serialized_transactions, info_length, parity_length)
-            .expect("We should expect correct encoding of the shards");
+        let encoded_shards =
+            encoder.encode_serialized_data(serialized_transactions, info_length, parity_length)?;
 
         let (transactions_commitment, _) = TransactionsCommitment::compute_merkle_root_and_proof(
             &encoded_shards,
             context.own_index,
-        )
-        .expect("We should expect correct computation of the Merkle root for encoded transactions");
+        )?;
         Ok(transactions_commitment)
     }
 
@@ -619,10 +617,7 @@ impl TransactionsCommitment {
             leaves.push(leaf);
         }
         let merkle_tree = MerkleTree::<DefaultHashFunctionWrapper>::from_leaves(&leaves);
-        let merkle_root = merkle_tree
-            .root()
-            .ok_or("couldn't get the merkle root")
-            .unwrap();
+        let merkle_root = merkle_tree.root().ok_or(ConsensusError::EmptyMerkleTree)?;
 
         let indices_to_prove = vec![own_index.value()];
         let merkle_proof = merkle_tree.proof(&indices_to_prove);
```

### crates/starfish/core/src/block_verifier.rs
```diff
@@ -122,6 +122,13 @@ impl BlockVerifier for SignedBlockVerifier {
                 quorum: committee.quorum_threshold(),
             });
         }
+        for acknowledgment in block.acknowledgments() {
+            ConsensusError::quick_validation_authority_indices(
+                &[acknowledgment.author],
+                committee,
+            )?;
+        }
+
         let mut seen_ancestors = vec![false; committee.size()];
         let mut parent_stakes = 0;
         for (i, ancestor) in block.ancestors().iter().enumerate() {
@@ -161,9 +168,6 @@ impl BlockVerifier for SignedBlockVerifier {
                 quorum: committee.quorum_threshold(),
             });
         }
-
-        // TODO: transaction verification is removed from here. It should be done when
-        // the transaction data gets available by Data/Transaction Manager
         Ok(())
     }
 
```

### crates/starfish/core/src/commit_syncer/mod.rs
```diff
@@ -295,15 +295,14 @@ pub(crate) fn verify_transactions_with_headers(
         // the ones that were included in the block when it was created.
         let block_header = block_headers
             .get(&block_ref)
-            .expect("header for fetched transactions must exist");
+            .ok_or(ConsensusError::MissingBlockHeader { block_ref })?;
 
         if block_header.transactions_commitment()
             != TransactionsCommitment::compute_transactions_commitment(
                 &inner_serialized_transactions,
                 &context,
                 &mut encoder,
-            )
-            .expect("correct computation of the transactions commitment should be successful")
+            )?
         {
             return Err(ConsensusError::TransactionCommitmentFailure {
                 round: block_ref.round,
@@ -359,8 +358,7 @@ pub(crate) fn verify_transactions_with_transactions_refs(
                 &inner_serialized_transactions,
                 context,
                 &mut encoder,
-            )
-            .expect("correct computation of the transactions commitment should be successful")
+            )?
         {
             return Err(ConsensusError::TransactionCommitmentFailure {
                 round: transaction_ref.round,
```

### crates/starfish/core/src/error.rs
```diff
@@ -142,6 +142,12 @@ pub(crate) enum ConsensusError {
     #[error("Too many ancestors in the block: {0} > {1}")]
     TooManyAncestors(usize, usize),
 
+    #[error("Merkle tree has no root (empty shard list)")]
+    EmptyMerkleTree,
+
+    #[error("Missing block header for {block_ref}")]
+    MissingBlockHeader { block_ref: BlockRef },
+
     #[error(
         "Commit range exceeded limit after scanning during {sync_type} sync: {count} > {limit}"
     )]
```

### crates/starfish/core/src/network/mod.rs
```diff
@@ -28,7 +28,7 @@ use async_trait::async_trait;
 use bytes::Bytes;
 use futures::Stream;
 use serde::{Deserialize, Serialize};
-use starfish_config::AuthorityIndex;
+use starfish_config::{AuthorityIndex, Committee};
 
 use crate::{
     Round, VerifiedBlockHeader,
@@ -322,7 +322,32 @@ fn bitmask_to_authority_set(bitmask: [u64; 4]) -> BTreeSet<AuthorityIndex> {
     set
 }
 
+fn validate_authority_bitmask(bitmask: [u64; 4], committee: &Committee) -> ConsensusResult<()> {
+    for (array_index, &bits) in bitmask.iter().enumerate() {
+        let mut bits = bits;
+        let base = array_index * 64;
+        while bits != 0 {
+            let bit = bits.trailing_zeros() as usize;
+            let index = base + bit;
+            if index >= committee.size() {
+                return Err(ConsensusError::InvalidAuthorityIndex {
+                    index: AuthorityIndex::from(index as u8),
+                    max: committee.size(),
+                });
+            }
+            bits &= bits - 1;
+        }
+    }
+    Ok(())
+}
+
 impl SerializedBlockBundleParts {
+    pub(crate) fn validate_useful_authorities(&self, committee: &Committee) -> ConsensusResult<()> {
+        validate_authority_bitmask(self.useful_headers_authors_bitmask, committee)?;
+        validate_authority_bitmask(self.useful_shards_authors_bitmask, committee)?;
+        Ok(())
+    }
+
     pub(crate) fn useful_headers_authors(&self) -> BTreeSet<AuthorityIndex> {
         bitmask_to_authority_set(self.useful_headers_authors_bitmask)
     }
```

### crates/starfish/core/src/network/tonic_network.rs
```diff
@@ -830,8 +830,12 @@ impl<S: NetworkService> ConsensusService for TonicServiceProxy<S> {
         &self,
         _request: Request<GetLatestRoundsRequest>,
     ) -> Result<Response<GetLatestRoundsResponse>, tonic::Status> {
+        // This RPC is kept in the service definition for backward compatibility,
+        // but is not supported by Starfish.
         error!("get_latest_rounds() is deprecated in starfish and should not be called");
-        unimplemented!();
+        Err(tonic::Status::unimplemented(
+            "get_latest_rounds is deprecated and not supported",
+        ))
     }
 
     type FetchTransactionsStream =
```
