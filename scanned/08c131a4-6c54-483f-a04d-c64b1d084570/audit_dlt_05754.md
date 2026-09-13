# [?] Harden secret sharing: fix panics, resolve TODOs, clean dead code (#18833)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-04
Source: https://github.com/aptos-labs/aptos-core/commit/1cf4d5a0bfa3702d2ded1811cee2570188d6b6f0
Type: security-commit

## Details
Harden secret sharing: fix panics, resolve TODOs, clean dead code (#18833)

* [consensus] Replace panics with proper error handling in secret sharing

Convert assert!, expect(), and unreachable!() calls to graceful error
returns in the secret sharing module. Panics in consensus code crash
validator nodes, so these should return errors instead.

- assert! → ensure! in add_self_share for author validation
- expect("Broadcast cannot fail") → warn + return in spawned task
- expect("pipeline must exist") → anyhow error propagation
- expect("Must not be None") → anyhow error propagation
- expect("Add self dec share should succeed") → ? operator
- expect("Author must exist for weight") → filter_map in retain
- expect("Author must exist in weights") → ok_or_else with anyhow
- unreachable!() in get_all_shares_authors → return None
- expect("Aggregated item should have self share") → warn + retry
- SecretShareConfig::get_id returns Result instead of panicking
- SecretShare::verify uses bounds-checked verification_keys access

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Resolve TODOs in secret sharing module

- Add ss_rb_config (ReliableBroadcastConfig) to ConsensusConfig for
  secret sharing, separate from rand_rb_config
- Add secret_share_request_delay_ms to ReliableBroadcastConfig with
  default of 300ms, replacing hardcoded sleep duration
- Thread config through SecretShareManager construction
- Resolve HashSet TODO in block_queue with explanatory comment

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Remove dead code from secret sharing types

Remove unused SecretSharingConfig struct, duplicate
FUTURE_ROUNDS_TO_ACCEPT constant, and ThresholdConfig type alias.
The actual config used is SecretShareConfig from aptos-types which
already implements weighted config correctly.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Add observability logging in secret sharing module

- Log when outgoing block sends fail instead of silently ignoring
- Log count of dropped incoming block batches during reset

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Move secret_share_request_delay_ms to ConsensusConfig

The delay field doesn't belong in ReliableBroadcastConfig since that
struct is shared with the randomness module. Move it to ConsensusConfig
directly and pass it as a separate parameter to SecretShareManager.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* [consensus] Fix missing reset signal and clean up secret sharing types

- Send reset signal to secret_share_manager in ExecutionProxyClient::reset()
- Remove unnecessary Option wrapper from QueueItem::share_requester_handles
- Change SecretShareStore::secret_share_map from HashMap to BTreeMap
- Make SecretShareConfig::get_peer_weight return Result instead of silently
  defaulting to 0
- Improve error messages with round context

Made-with: Cursor

* [consensus] Defer self-share derivation in SecretShareManager

Drive derive futures via FuturesUnordered in the select loop instead of
awaiting inline, so block ingestion is no longer blocked on derivation.

Made-with: Cursor

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### config/src/config/consensus_config.rs
```diff
@@ -94,6 +94,9 @@ pub struct ConsensusConfig {
     pub broadcast_vote: bool,
     pub proof_cache_capacity: u64,
     pub rand_rb_config: ReliableBroadcastConfig,
+    pub secret_share_rb_config: ReliableBroadcastConfig,
+    /// Delay in ms before broadcasting secret share requests.
+    pub secret_share_request_delay_ms: u64,
     pub num_bounded_executor_tasks: u64,
     pub enable_pre_commit: bool,
     pub max_pending_rounds_in_commit_vote_cache: u64,
@@ -380,6 +383,13 @@ impl Default for ConsensusConfig {
                 backoff_policy_max_delay_ms: 10000,
                 rpc_timeout_ms: 10000,
             },
+            secret_share_rb_config: ReliableBroadcastConfig {
+                backoff_policy_base_ms: 2,
+                backoff_policy_factor: 100,
+                backoff_policy_max_delay_ms: 10000,
+                rpc_timeout_ms: 10000,
+            },
+            secret_share_request_delay_ms: 300,
             num_bounded_executor_tasks: 16,
             enable_pre_commit: true,
             max_pending_rounds_in_commit_vote_cache: 100,
```

### consensus/src/pipeline/decryption_pipeline_builder.rs
```diff
@@ -59,6 +59,7 @@ impl PipelineBuilder {
         // Assumption: `input_txns` is free of Encrypted Transactions
         // due to VM validation checks
         let Some(secret_share_config) = maybe_secret_share_config else {
+            // TODO(ibalajiarun): Is sending None necessary?
             let _ = derived_self_key_share_tx.send(None);
             let maybe_key = secret_shared_key_rx
                 .await
```

### consensus/src/pipeline/execution_client.rs
```diff
@@ -296,7 +296,8 @@ impl ExecutionProxyClient {
             secret_ready_block_tx,
             network_sender.clone(),
             self.bounded_executor.clone(),
-            &self.consensus_config.rand_rb_config,
+            &self.consensus_config.secret_share_rb_config,
+            self.consensus_config.secret_share_request_delay_ms,
         );
 
         tokio::spawn(secret_share_manager.start(
@@ -691,10 +692,15 @@ impl TExecutionClient for ExecutionProxyClient {
     }
 
     async fn reset(&self, target: &LedgerInfoWithSignatures) -> Result<()> {
-        let (reset_tx_to_rand_manager, reset_tx_to_buffer_manager) = {
+        let (
+            reset_tx_to_rand_manager,
+            reset_tx_to_secret_share_manager,
+            reset_tx_to_buffer_manager,
+        ) = {
             let handle = self.handle.read();
             (
                 handle.reset_tx_to_rand_manager.clone(),
+                handle.reset_tx_to_secret_share_manager.clone(),
                 handle.reset_tx_to_buffer_manager.clone(),
             )
         };
@@ -711,6 +717,18 @@ impl TExecutionClient for ExecutionProxyClient {
             ack_rx.await.map_err(|_| Error::RandResetDropped)?;
         }
 
+        if let Some(mut reset_tx) = reset_tx_to_secret_share_manager {
+            let (ack_tx, ack_rx) = oneshot::channel::<ResetAck>();
+            reset_tx
+                .send(ResetRequest {
+                    tx: ack_tx,
+                    signal: ResetSignal::TargetRound(target.commit_info().round()),
+                })
+                .await
+                .map_err(|_| Error::RandResetDropped)?;
+            ack_rx.await.map_err(|_| Error::RandResetDropped)?;
+        }
+
         if let Some(mut reset_tx) = reset_tx_to_buffer_manager {
             // reset execution phase and commit phase
             let (tx, rx) = oneshot::channel::<ResetAck>();
```

### consensus/src/rand/secret_sharing/block_queue.rs
```diff
@@ -18,15 +18,11 @@ pub struct QueueItem {
     ordered_blocks: OrderedBlocks,
     offsets_by_round: HashMap<Round, usize>,
     pending_secret_key_rounds: HashSet<Round>,
-    share_requester_handles: Option<Vec<DropGuard>>,
+    share_requester_handles: Vec<DropGuard>,
 }
 
 impl QueueItem {
-    pub fn new(
-        ordered_blocks: OrderedBlocks,
-        share_requester_handles: Option<Vec<DropGuard>>,
-        pending_secret_key_rounds: HashSet<Round>,
-    ) -> Self {
+    pub fn new(ordered_blocks: OrderedBlocks, pending_secret_key_rounds: HashSet<Round>) -> Self {
         assert!(!ordered_blocks.ordered_blocks.is_empty());
         let offsets_by_round: HashMap<Round, usize> = ordered_blocks
             .ordered_blocks
@@ -37,7 +33,7 @@ impl QueueItem {
         Self {
             ordered_blocks,
             offsets_by_round,
-            share_requester_handles,
+            share_requester_handles: Vec::new(),
             pending_secret_key_rounds,
         }
     }
@@ -61,9 +57,13 @@ impl QueueItem {
         self.pending_secret_key_rounds.is_empty()
     }
 
+    pub fn push_share_requester_handle(&mut self, handle: DropGuard) {
+        self.share_requester_handles.push(handle);
+    }
+
     pub fn set_secret_shared_key(&mut self, round: Round, key: SecretSharedKey) {
         let offset = self.offset(round);
-        // TODO(ibalajiarun): revisit the importance of this hashset
+        // Guard against setting a key for an already-resolved round.
         if self.pending_secret_key_rounds.contains(&round) {
             observe_block(
                 self.blocks()[offset].timestamp_usecs(),
```

### consensus/src/rand/secret_sharing/secret_share_manager.rs
```diff
@@ -19,7 +19,7 @@ use aptos_channels::aptos_channel;
 use aptos_config::config::ReliableBroadcastConfig;
 use aptos_consensus_types::{
     common::{Author, Round},
-    pipelined_block::PipelinedBlock,
+    pipelined_block::{PipelinedBlock, SecretShareResult, TaskResult},
 };
 use aptos_infallible::Mutex;
 use aptos_logger::{error, info, spawn_named, warn};
@@ -33,25 +33,30 @@ use aptos_types::{
 use bytes::Bytes;
 use futures::{
     future::{AbortHandle, Abortable},
+    stream::FuturesUnordered,
     FutureExt, StreamExt,
 };
 use futures_channel::{
     mpsc::{unbounded, UnboundedReceiver, UnboundedSender},
     oneshot,
 };
-use std::{collections::HashSet, sync::Arc, time::Duration};
+use std::{collections::HashSet, future::Future, pin::Pin, sync::Arc, time::Duration};
 use tokio_retry::strategy::ExponentialBackoff;
 
 pub type Sender<T> = UnboundedSender<T>;
 pub type Receiver<T> = UnboundedReceiver<T>;
 
+type PendingDeriveFut =
+    Pin<Box<dyn Future<Output = (Round, TaskResult<SecretShareResult>)> + Send>>;
+
 pub struct SecretShareManager {
     author: Author,
     epoch_state: Arc<EpochState>,
     stop: bool,
     config: SecretShareConfig,
     reliable_broadcast: Arc<ReliableBroadcast<SecretShareMessage, ExponentialBackoff>>,
     network_sender: Arc<NetworkSender>,
+    secret_share_request_delay_ms: u64,
 
     // local channel received from dec_store
     decision_rx: Receiver<SecretSharedKey>,
@@ -60,6 +65,7 @@ pub struct SecretShareManager {
     // local state
     secret_share_store: Arc<Mutex<SecretShareStore>>,
     block_queue: BlockQueue,
+    pending_derives: FuturesUnordered<PendingDeriveFut>,
 }
 
 impl SecretShareManager {
@@ -71,6 +77,7 @@ impl SecretShareManager {
         network_sender: Arc<NetworkSender>,
         bounded_executor: BoundedExecutor,
         rb_config: &ReliableBroadcastConfig,
+        secret_share_request_delay_ms: u64,
     ) -> Self {
         let rb_backoff_policy = ExponentialBackoff::from_millis(rb_config.backoff_policy_base_ms)
             .factor(rb_config.backoff_policy_factor)
@@ -100,62 +107,95 @@ impl SecretShareManager {
             config,
             reliable_broadcast,
             network_sender,
+            secret_share_request_delay_ms,
 
             decision_rx,
             outgoing_blocks,
 
             secret_share_store: dec_store,
             block_queue: BlockQueue::new(),
+            pending_derives: FuturesUnordered::new(),
         }
     }
 
-    async fn process_incoming_blocks(&mut self, blocks: OrderedBlocks) -> anyhow::Result<()> {
+    /// Processes a batch of incoming ordered blocks by registering their rounds
+    /// in the store and deferring self-share derivation to `pending_derives`.
+    fn process_incoming_blocks(&mut self, blocks: OrderedBlocks) -> anyhow::Result<()> {
         let rounds: Vec<u64> = blocks.ordered_blocks.iter().map(|b| b.round()).collect();
-        info!(rounds = rounds, "Processing incoming blocks.");
+        info!(
+            rounds = rounds,
+            num_blocks = rounds.len(),
+            "Processing incoming blocks."
+        );
 
-        let mut share_requester_handles = Vec::new();
-        let mut pending_secret_key_rounds = HashSet::new();
+        let pending_secret_key_rounds = HashSet::from_iter(rounds);
         for block in blocks.ordered_blocks.iter() {
-            let handle = self.process_incoming_block(block).await?;
-            share_requester_handles.push(handle);
-            pending_secret_key_rounds.insert(block.round());
+            self.enqueue_self_derive(block)?;
         }
 
-        let queue_item = QueueItem::new(
-            blocks,
-            Some(share_requester_handles),
-            pending_secret_key_rounds,
-        );
-        self.block_queue.push_back(queue_item);
+        self.block_queue
+            .push_back(QueueItem::new(blocks, pending_secret_key_rounds));
         Ok(())
     }
 
-    async fn process_incoming_block(&self, block: &PipelinedBlock) -> anyhow::Result<DropGuard> {
-        let futures = block.pipeline_futs().expect("pipeline must exist");
-        let self_secret_share = futures
-            .secret_sharing_derive_self_fut
-            .await
-            .map_err(|_| anyhow::anyhow!("derive self failed"))?
-            .expect("Must not be None");
-        let metadata = self_secret_share.metadata().clone();
+    /// Registers the round in the store so remote shares can accumulate, and
+    /// pushes the self-derive future into `pending_derives` for later resolution.
+    fn enqueue_self_derive(&mut self, block: &PipelinedBlock) -> anyhow::Result<()> {
+        let futures = block.pipeline_futs().ok_or_else(|| {
+            anyhow::anyhow!("pipeline futures not set for round {}", block.round())
+        })?;
+
+        self.secret_share_store
+            .lock()
+            .update_highest_known_round(block.round());
+
+        let round = block.round();
+        let derive_fut = futures.secret_sharing_derive_self_fut.clone();
+        self.pending_derives
+            .push(Box::pin(async move { (round, derive_fut.await) }));
+        Ok(())
+    }
+
+    /// Handles a completed self-share derivation: updates the store, broadcasts
+    /// the share, and spawns the share requester task.
+    fn process_completed_derive(&mut self, round: Round, result: TaskResult<SecretShareResult>) {
+        let share = match result {
+            Ok(Some(share)) => share,
+            Ok(None) => {
+                error!(round = round, "Self-share derive returned None, skipping");
+                return;
+            },
+            Err(e) => {
+                error!(round = round, "Self-share derive failed: {:?}", e);
+                return;
+            },
+        };
 
-        // Now acquire lock and update store
+        let metadata = share.metadata().clone();
         {
-            let mut secret_share_store = self.secret_share_store.lock();
-            secret_share_store.update_highest_known_round(block.round());
-            secret_share_store
-                .add_self_share(self_secret_share.clone())
-                .expect("Add self dec share should succeed");
+            let mut store = self.secret_share_store.lock();
+            if let Err(e) = store.add_self_share(share.clone()) {
+                error!(round = round, "Failed to add self share to store: {:?}", e);
+                return;
+            }
         }
 
         info!(LogSchema::new(LogEvent::BroadcastSecretShare)
             .epoch(self.epoch_state.epoch)
             .author(self.author)
-            .round(block.round()));
-        self.network_sender.broadcast_without_self(
-            SecretShareMessage::Share(self_secret_share).into_network_message(),
-        );
-        Ok(self.spawn_share_requester_task(metadata))
+            .round(round));
+        self.network_sender
+            .broadcast_without_self(SecretShareMessage::Share(share).into_network_message());
+
+        let guard = self.spawn_share_requester_task(metadata);
+        if let Some(item) = self.block_queue.item_mut(round) {
+            item.push_share_requester_handle(guard);
+        } else {
+            warn!(
+                round = round,
+                "Secret share item not found for round {}", round
+            );
+        }
     }
 
     fn process_ready_blocks(&mut self, ready_blocks: Vec<OrderedBlocks>) {
@@ -166,7 +206,12 @@ impl SecretShareManager {
         info!(rounds = rounds, "Processing secret share ready blocks.");
 
         for blocks in ready_blocks {
-            let _ = self.outgoing_blocks.unbounded_send(blocks);
+            if let Err(e) = self.outgoing_blocks.unbounded_send(blocks) {
+                error!(
+                    "[SecretShareManager] Failed to send ready blocks downstream: {}",
+                    e
+                );
+            }
         }
     }
 
@@ -177,9 +222,8 @@ impl SecretShareManager {
             ResetSignal::TargetRound(round) => round,
         };
         self.block_queue = BlockQueue::new();
-        self.secret_share_store
-            .lock()
-            .update_highest_known_round(target_round);
+        self.pending_derives = FuturesUnordered::new();
+        self.secret_share_store.lock().reset(target_round);
         self.stop = matches!(signal, ResetSignal::Stop);
         let _ = tx.send(ResetAck::default());
     }
@@ -244,9 +288,9 @@ impl SecretShareManager {
         ));
         let epoch_state = self.epoch_state.clone();
         let secret_share_store = self.secret_share_store.clone();
+        let request_delay_ms = self.secret_share_request_delay_ms;
         let task = async move {
-            // TODO(ibalajiarun): Make this configurable
-            tokio::time::sleep(Duration::from_millis(300)).await;
+            tokio::time::sleep(Duration::from_millis(request_delay_ms)).await;
             let maybe_existing_shares = secret_share_store.lock().get_all_shares_authors(&metadata);
             if let Some(existing_shares) = maybe_existing_shares {
                 let epoch = epoch_state.epoch;
@@ -262,9 +306,15 @@ impl SecretShareManager {
                     "[SecretShareManager] Start broadcasting share request for {}",
                     targets.len(),
                 );
-                rb.multicast(request, aggregate_state, targets)
-                    .await
-                    .expect("Broadcast cannot fail");
+                if let Err(e) = rb.multicast(request, aggregate_state, targets).await {
+                    warn!(
+                        epoch = epoch,
+                        round = metadata.round,
+                        "[SecretShareManager] Share request broadcast failed: {}",
+                        e,
+                    );
+                    return;
+                }
                 info!(
                     epoch = epoch,
                     round = metadata.round,
@@ -354,12 +404,21 @@ impl SecretShareManager {
         while !self.stop {
             tokio::select! {
                 Some(blocks) = incoming_blocks.next() => {
-                    if let Err(e) = self.process_incoming_blocks(blocks).await {
+                    if let Err(e) = self.process_incoming_blocks(blocks) {
                         error!("error processing incoming blocks: {:?}", e);
                     }
                 }
+                Some((round, result)) = self.pending_derives.next() => {
+                    self.process_completed_derive(round, result);
+                }
                 Some(reset) = reset_rx.next() => {
-                    while matches!(incoming_blocks.try_next(), Ok(Some(_))) {}
+                    let mut dropped = 0;
+                    while matches!(incoming_blocks.try_next(), Ok(Some(_))) {
+                        dropped += 1;
+                    }
+                    if dropped > 0 {
+                        info!("[SecretShareManager] Dropped {} incoming block batches during reset", dropped);
+                    }
                     self.process_reset(reset);
                 }
                 Some(secret_shared_key) = self.decision_rx.next() => {
```

### consensus/src/rand/secret_sharing/secret_share_store.rs
```diff
@@ -12,7 +12,7 @@ use aptos_types::secret_sharing::{
     SecretShare, SecretShareConfig, SecretShareMetadata, SecretSharedKey,
 };
 use itertools::Either;
-use std::collections::{HashMap, HashSet};
+use std::collections::{BTreeMap, HashMap, HashSet};
 
 pub struct SecretShareAggregator {
     self_author: Author,
@@ -49,9 +49,13 @@ impl SecretShareAggregator {
             BlockStage::SECRET_SHARING_ADD_ENOUGH_SHARE,
         );
         let dec_config = secret_share_config.clone();
-        let self_share = self
-            .get_self_share()
-            .expect("Aggregated item should have self share");
+        let self_share = match self.get_self_share() {
+            Some(share) => share,
+            None => {
+                warn!("Aggregation threshold met but self share missing");
+                return Either::Left(self);
+            },
+        };
         tokio::task::spawn_blocking(move || {
             let maybe_key = SecretShare::aggregate(self.shares.values(), &dec_config);
             match maybe_key {
@@ -76,7 +80,7 @@ impl SecretShareAggregator {
         self.total_weight = self
             .shares
             .keys()
-            .map(|author| weights.get(author).expect("Author must exist for weight"))
+            .filter_map(|author| weights.get(author))
             .sum();
     }
 
@@ -161,7 +165,7 @@ impl SecretShareItem {
         let item = std::mem::replace(self, Self::new(Author::ONE));
         let share_weight = *share_weights
             .get(share.author())
-            .expect("Author must exist in weights");
+            .ok_or_else(|| anyhow::anyhow!("Author {} not found in weights", share.author()))?;
         let new_item = match item {
             SecretShareItem::PendingMetadata(mut share_aggregator) => {
                 let metadata = share.metadata.clone();
@@ -187,9 +191,7 @@ impl SecretShareItem {
                 share_aggregator, ..
             } => Some(share_aggregator.shares.keys().cloned().collect()),
             SecretShareItem::Decided { .. } => None,
-            SecretShareItem::PendingMetadata(_) => {
-                unreachable!("Should only be called after block is added")
-            },
+            SecretShareItem::PendingMetadata(_) => None,
         }
     }
 
@@ -204,11 +206,18 @@ impl SecretShareItem {
     }
 }
 
+/// Per-epoch store that tracks secret share aggregation state for each round.
+/// Remote shares can accumulate here while the self-share derivation is still
+/// in flight. Once enough shares arrive and the self share is added,
+/// aggregation produces a `SecretSharedKey` sent via `decision_tx`.
+///
+/// Note: there is no garbage collection of items after they're decided. They
+/// are kept around until the epoch ends.
 pub struct SecretShareStore {
     epoch: u64,
     self_author: Author,
     secret_share_config: SecretShareConfig,
-    secret_share_map: HashMap<Round, SecretShareItem>,
+    secret_share_map: BTreeMap<Round, SecretShareItem>,
     highest_known_round: u64,
     decision_tx: Sender<SecretSharedKey>,
 }
@@ -224,7 +233,7 @@ impl SecretShareStore {
             epoch,
             self_author: author,
             secret_share_config: dec_config,
-            secret_share_map: HashMap::new(),
+            secret_share_map: BTreeMap::new(),
             highest_known_round: 0,
             decision_tx,
         }
@@ -234,8 +243,15 @@ impl SecretShareStore {
         self.highest_known_round = std::cmp::max(self.highest_known_round, round);
     }
 
+    pub fn reset(&mut self, round: u64) {
+        self.update_highest_known_round(round);
+        // remove future rounds items in case they're already decided
+        // otherwise if the block re-enters the queue, it'll be stuck
+        let _ = self.secret_share_map.split_off(&round);
+    }
+
     pub fn add_self_share(&mut self, share: SecretShare) -> anyhow::Result<()> {
-        assert!(
+        ensure!(
             self.self_author == share.author,
             "Only self shares can be added with metadata"
         );
@@ -257,14 +273,15 @@ impl SecretShareStore {
     }
 
     pub fn add_share(&mut self, share: SecretShare) -> anyhow::Result<bool> {
-        let weight = self.secret_share_config.get_peer_weight(share.author());
+        let weight = self.secret_share_config.get_peer_weight(share.author())?;
         let metadata = share.metadata();
         ensure!(metadata.epoch == self.epoch, "Share from different epoch");
         ensure!(
             metadata.round <= self.highest_known_round + FUTURE_ROUNDS_TO_ACCEPT,
             "Share from future round"
         );
 
+        // TODO(ibalajiarun): Make sure to garbage collect the items after they're decided.
         let item = self
             .secret_share_map
             .entry(metadata.round)
```

### consensus/src/rand/secret_sharing/types.rs
```diff
@@ -1,21 +1,8 @@
 // Copyright (c) Aptos Foundation
 // Licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE
 
-use aptos_batch_encryption::group::Fr;
-use aptos_consensus_types::common::Author;
-use aptos_crypto::arkworks::shamir::ShamirThresholdConfig;
-use aptos_types::{
-    secret_sharing::{
-        DigestKey, EncryptionKey, MasterSecretKeyShare, SecretShareMetadata, VerificationKey,
-    },
-    validator_verifier::ValidatorVerifier,
-};
+use aptos_types::secret_sharing::SecretShareMetadata;
 use serde::{Deserialize, Serialize};
-use std::sync::Arc;
-
-pub const FUTURE_ROUNDS_TO_ACCEPT: u64 = 200;
-
-pub type ThresholdConfig = ShamirThresholdConfig<Fr>;
 
 #[derive(Clone, Serialize, Deserialize)]
 pub struct RequestSecretShare {
@@ -35,73 +22,3 @@ impl RequestSecretShare {
         &self.metadata
     }
 }
-
-#[derive(Clone)]
-pub struct SecretSharingConfig {
-    author: Author,
-    epoch: u64,
-    validator: Arc<ValidatorVerifier>,
-    // wconfig: WeightedConfig,
-    digest_key: DigestKey,
-    msk_share: MasterSecretKeyShare,
-    verification_keys: Vec<VerificationKey>,
-    config: ThresholdConfig,
-    encryption_key: EncryptionKey,
-}
-
-impl SecretSharingConfig {
-    pub fn new(
-        author: Author,
-        epoch: u64,
-        validator: Arc<ValidatorVerifier>,
-        digest_key: DigestKey,
-        msk_share: MasterSecretKeyShare,
-        verification_keys: Vec<VerificationKey>,
-        config: ThresholdConfig,
-        encryption_key: EncryptionKey,
-    ) -> Self {
-        Self {
-            author,
-            epoch,
-            validator,
-            digest_key,
-            msk_share,
-            verification_keys,
-            config,
-            encryption_key,
-        }
-    }
-
-    pub fn get_id(&self, peer: &Author) -> usize {
-        *self
-            .validator
-            .address_to_validator_index()
-            .get(peer)
-            .expect("Peer should be in the index!")
-    }
-
-    pub fn digest_key(&self) -> &DigestKey {
-        &self.digest_key
-    }
-
-    pub fn msk_share(&self) -> &MasterSecretKeyShare {
-        &self.msk_share
-    }
-
-    pub fn threshold(&self) -> u64 {
-        self.config.t as u64
-    }
-
-    pub fn number_of_validators(&self) -> u64 {
-        self.config.n as u64
-    }
-
-    pub fn get_peer_weight(&self, _peer: &Author) -> u64 {
-        // daniel todo: use weighted config
-        1
-    }
-
-    pub fn encryption_key(&self) -> &EncryptionKey {
-        &self.encryption_key
-    }
-}
```

### types/src/secret_sharing.rs
```diff
@@ -73,10 +73,18 @@ impl SecretShare {
     }
 
     pub fn verify(&self, config: &SecretShareConfig) -> anyhow::Result<()> {
-        let index = config.get_id(self.author());
+        let index = config.get_id(self.author())?;
         let decryption_key_share = self.share().clone();
-        // TODO(ibalajiarun): Check index out of bounds
-        config.verification_keys[index]
+        config
+            .verification_keys
+            .get(index)
+            .ok_or_else(|| {
+                anyhow::anyhow!(
+                    "Verification key index {} out of bounds (len {})",
+                    index,
+                    config.verification_keys.len()
+                )
+            })?
             .verify_decryption_key_share(&self.metadata.digest, &decryption_key_share)?;
         Ok(())
     }
@@ -171,13 +179,12 @@ impl SecretShareConfig {
         }
     }
 
-    pub fn get_id(&self, peer: &Author) -> usize {
-        // TODO(ibalajiarun): Index out of bounds
-        *self
-            .validator
+    pub fn get_id(&self, peer: &Author) -> anyhow::Result<usize> {
+        self.validator
             .address_to_validator_index()
             .get(peer)
-            .expect("Peer should be in the index!")
+            .copied()
+            .ok_or_else(|| anyhow::anyhow!("Peer {} not found in validator index", peer))
     }
 
     pub fn digest_key(&self) -> &DigestKey {
@@ -196,8 +203,11 @@ impl SecretShareConfig {
         self.config.get_threshold_config().n as u64
     }
 
-    pub fn get_peer_weight(&self, peer: &Author) -> u64 {
-        self.weights.get(peer).copied().unwrap_or(0)
+    pub fn get_peer_weight(&self, peer: &Author) -> anyhow::Result<u64> {
+        self.weights
+            .get(peer)
+            .copied()
+            .ok_or_else(|| anyhow::anyhow!("Peer {} not found in validator index", peer))
     }
 
     pub fn get_peer_weights(&self) -> &HashMap<Author, u64> {
```
