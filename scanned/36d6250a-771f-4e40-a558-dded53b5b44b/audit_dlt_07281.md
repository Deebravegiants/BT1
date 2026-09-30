# [?] [TestLoop] Properly fix the TestLoop hang-on-panic issue. (#12240)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-10-17
Source: https://github.com/near/nearcore/commit/de6e88b6c8bde63ddf408da5f7c4c4b4aaeb267d
Type: security-commit

## Details
[TestLoop] Properly fix the TestLoop hang-on-panic issue. (#12240)

Previously, https://github.com/near/nearcore/pull/11653 introduced a
mechanism where a maximum timeout was used in `impl Drop for Chain`, but
that only works if the testloop feature is enabled, which most likely is
not the case when someone just runs a test.

This PR switches to an alternative implementation; not only is it
simpler, but it also automatically works. If the TestLoop panics, it
will be dropped first. When it is dropped, it ensures that all pending
events are dropped, thereby dropping the ApplyChunksStillApplying
struct, making the subsequent waiter.wait() call go through when we're
recursively dropping the Chain.

Confirmed that this fixes #11840 as well.

## Patch
### Cargo.lock
```diff
@@ -4034,6 +4034,7 @@ dependencies = [
  "tempfile",
  "thiserror",
  "time",
+ "tokio",
  "tracing",
 ]
 
```

### chain/chain/Cargo.toml
```diff
@@ -30,6 +30,7 @@ strum.workspace = true
 tempfile.workspace = true
 thiserror.workspace = true
 time.workspace = true
+tokio.workspace = true
 tracing.workspace = true
 
 near-async.workspace = true
@@ -112,7 +113,6 @@ nightly_protocol = [
   "node-runtime/nightly_protocol",
 ]
 sandbox = ["near-o11y/sandbox", "near-primitives/sandbox"]
-testloop = []
 protocol_schema = [
   "near-schema-checker-lib/protocol_schema",
   "near-crypto/protocol_schema",
```

### chain/chain/src/block_processing_utils.rs
```diff
@@ -9,8 +9,7 @@ use near_primitives::hash::CryptoHash;
 use near_primitives::sharding::{ReceiptProof, ShardChunkHeader, StateSyncInfo};
 use near_primitives::types::ShardId;
 use std::collections::HashMap;
-use std::sync::{Arc, Condvar, Mutex};
-use std::time::Duration;
+use std::sync::Arc;
 
 /// Max number of blocks that can be in the pool at once.
 /// This number will likely never be hit unless there are many forks in the chain.
@@ -25,7 +24,7 @@ pub(crate) struct BlockPreprocessInfo {
     pub(crate) challenged_blocks: Vec<CryptoHash>,
     pub(crate) provenance: Provenance,
     /// Used to get notified when the applying chunks of a block finishes.
-    pub(crate) apply_chunks_done_tracker: ApplyChunksDoneTracker,
+    pub(crate) apply_chunks_done_waiter: ApplyChunksDoneWaiter,
     /// This is used to calculate block processing time metric
     pub(crate) block_start_processing_time: Instant,
 }
@@ -127,7 +126,7 @@ impl BlocksInProcessing {
     /// Returns true if new blocks are done applying chunks
     pub(crate) fn wait_for_all_blocks(&self) -> bool {
         for (_, (_, block_preprocess_info)) in self.preprocessed_blocks.iter() {
-            let _ = block_preprocess_info.apply_chunks_done_tracker.wait_until_done();
+            let _ = block_preprocess_info.apply_chunks_done_waiter.wait();
         }
         !self.preprocessed_blocks.is_empty()
     }
@@ -142,83 +141,32 @@ impl BlocksInProcessing {
             .get(block_hash)
             .ok_or(BlockNotInPoolError)?
             .1
-            .apply_chunks_done_tracker
-            .wait_until_done();
+            .apply_chunks_done_waiter
+            .wait();
         Ok(())
     }
 }
 
-/// This is used to for the thread that applies chunks to notify other waiter threads.
-/// The thread applying the chunks should call `set_done` to send the notification.
-/// The waiter threads should call `wait_until_done` to wait (blocked) for the notification.
+/// The waiter's wait() will block until the corresponding ApplyChunksStillApplying is dropped.
 #[derive(Clone)]
-pub struct ApplyChunksDoneTracker(Arc<(Mutex<bool>, Condvar)>);
-
-impl ApplyChunksDoneTracker {
-    pub fn new() -> Self {
-        Self(Arc::new((Mutex::new(false), Condvar::new())))
-    }
+pub struct ApplyChunksDoneWaiter(Arc<tokio::sync::Mutex<()>>);
+pub struct ApplyChunksStillApplying {
+    // We're using tokio's mutex guard, because the std one is not Send.
+    _guard: tokio::sync::OwnedMutexGuard<()>,
+}
 
-    /// Notifies all threads waiting on `wait_until_done` that apply chunks is done.
-    /// This should be called only once.
-    /// Returns an error if it is called more than once or the mutex used internally is poisoned.
-    pub fn set_done(&mut self) -> Result<(), &'static str> {
-        let (lock, cvar) = &*self.0;
-        match lock.lock() {
-            Ok(mut guard) => {
-                if *guard {
-                    Err("Apply chunks done marker is already set to true.")
-                } else {
-                    *guard = true;
-                    cvar.notify_all();
-                    Ok(())
-                }
-            }
-            Err(_poisoned) => Err("Mutex is poisoned."),
-        }
+impl ApplyChunksDoneWaiter {
+    pub fn new() -> (Self, ApplyChunksStillApplying) {
+        let lock = Arc::new(tokio::sync::Mutex::new(()));
+        // Use try_lock_owned() rather than blocking_lock_owned(), because otherwise
+        // this causes a panic if we do this on a tokio runtime.
+        let guard = lock.clone().try_lock_owned().expect("should succeed on a fresh mutex");
+        (ApplyChunksDoneWaiter(lock), ApplyChunksStillApplying { _guard: guard })
     }
 
-    /// Blocks the current thread until the `set_done` is called after applying the chunks.
-    /// to indicate that apply chunks is done.
-    pub fn wait_until_done(&self) {
-        #[cfg(feature = "testloop")]
-        let mut testloop_total_wait_time = Duration::from_millis(0);
-
-        let (lock, cvar) = &*self.0;
-        match lock.lock() {
-            Ok(mut guard) => loop {
-                let done = *guard;
-                if done {
-                    break;
-                }
-                const WAIT_TIMEOUT: Duration = Duration::from_millis(100);
-                match cvar.wait_timeout(guard, WAIT_TIMEOUT) {
-                    Ok(result) => {
-                        guard = result.0;
-
-                        // Panics during testing (eg. due to assertion failures) cause the waiter
-                        // threads to miss the notification (see issue #11447). Thus, for testing only,
-                        // we limit the total wait time for waiting for the notification.
-                        #[cfg(feature = "testloop")]
-                        if result.1.timed_out() {
-                            const TESTLOOP_MAX_WAIT_TIME: Duration = Duration::from_millis(5000);
-                            testloop_total_wait_time += WAIT_TIMEOUT;
-                            if testloop_total_wait_time >= TESTLOOP_MAX_WAIT_TIME {
-                                break;
-                            }
-                        }
-                    }
-                    Err(_poisoned) => {
-                        tracing::error!("Mutex is poisoned.");
-                        break;
-                    }
-                }
-            },
-            Err(_poisoned) => {
-                tracing::error!("Mutex is poisoned.");
-                ()
-            }
-        }
+    pub fn wait(&self) {
+        // This would only go through if the guard has been dropped.
+        drop(self.0.blocking_lock());
     }
 }
 
@@ -228,16 +176,16 @@ mod tests {
     use std::sync::Arc;
     use std::time::Duration;
 
-    use super::ApplyChunksDoneTracker;
+    use super::ApplyChunksDoneWaiter;
 
     #[test]
     fn test_apply_chunks_with_multiple_waiters() {
         let shared_value: Arc<AtomicBool> = Arc::new(AtomicBool::new(false));
 
-        let mut tracker = ApplyChunksDoneTracker::new();
-        let waiter1 = tracker.clone();
-        let waiter2 = tracker.clone();
-        let waiter3 = tracker.clone();
+        let (waiter, still_applying) = ApplyChunksDoneWaiter::new();
+        let waiter1 = waiter.clone();
+        let waiter2 = waiter.clone();
+        let waiter3 = waiter;
 
         let (results_sender, results_receiver) = std::sync::mpsc::channel();
 
@@ -246,7 +194,7 @@ mod tests {
             let current_sender = results_sender.clone();
             let current_shared_value = shared_value.clone();
             std::thread::spawn(move || {
-                waiter.wait_until_done();
+                waiter.wait();
                 let read_value = current_shared_value.load(Ordering::Relaxed);
                 current_sender.send(read_value).unwrap();
             });
@@ -255,7 +203,7 @@ mod tests {
         // Wait 300ms then set the shared_value to true, and notify the waiters.
         std::thread::sleep(Duration::from_millis(300));
         shared_value.store(true, Ordering::Relaxed);
-        tracker.set_done().unwrap();
+        drop(still_applying);
 
         // Check values that waiters read
         for _ in 0..3 {
```

### chain/chain/src/chain.rs
```diff
@@ -1,5 +1,6 @@
 use crate::block_processing_utils::{
-    ApplyChunksDoneTracker, BlockPreprocessInfo, BlockProcessingArtifact, BlocksInProcessing,
+    ApplyChunksDoneWaiter, ApplyChunksStillApplying, BlockPreprocessInfo, BlockProcessingArtifact,
+    BlocksInProcessing,
 };
 use crate::blocks_delay_tracker::BlocksDelayTracker;
 use crate::chain_update::ChainUpdate;
@@ -46,7 +47,6 @@ use near_chain_configs::{MutableConfigValue, MutableValidatorSigner};
 use near_chain_primitives::error::{BlockKnownError, Error, LogTransientStorageError};
 use near_epoch_manager::shard_tracker::ShardTracker;
 use near_epoch_manager::EpochManagerAdapter;
-use near_o11y::log_assert;
 use near_primitives::block::{genesis_chunks, Block, BlockValidityError, Tip};
 use near_primitives::block_header::BlockHeader;
 use near_primitives::challenge::{
@@ -294,8 +294,9 @@ type UpdateShardJob =
     (ShardId, Box<dyn FnOnce(&Span) -> Result<ShardUpdateResult, Error> + Send + Sync + 'static>);
 
 /// PreprocessBlockResult is a tuple where the first element is a vector of jobs
-/// to update shards, the second element is BlockPreprocessInfo
-type PreprocessBlockResult = (Vec<UpdateShardJob>, BlockPreprocessInfo);
+/// to update shards, the second element is BlockPreprocessInfo, and the third element shall be
+/// dropped when the chunks finish applying.
+type PreprocessBlockResult = (Vec<UpdateShardJob>, BlockPreprocessInfo, ApplyChunksStillApplying);
 
 // Used only for verify_block_hash_and_signature. See that method.
 #[derive(Clone, Copy, PartialEq, Eq)]
@@ -1820,7 +1821,7 @@ impl Chain {
                 return Err(e);
             }
         };
-        let (apply_chunk_work, block_preprocess_info) = preprocess_res;
+        let (apply_chunk_work, block_preprocess_info, apply_chunks_still_applying) = preprocess_res;
 
         if self.epoch_manager.is_next_block_epoch_start(block.header().prev_hash())? {
             // This is the end of the epoch. Next epoch we will generate new state parts. We can drop the old ones.
@@ -1835,15 +1836,14 @@ impl Chain {
         let block = block.into_inner();
         let block_hash = *block.hash();
         let block_height = block.header().height();
-        let apply_chunks_done_tracker = block_preprocess_info.apply_chunks_done_tracker.clone();
         self.blocks_in_processing.add(block, block_preprocess_info)?;
 
         // 3) schedule apply chunks, which will be executed in the rayon thread pool.
         self.schedule_apply_chunks(
             block_hash,
             block_height,
             apply_chunk_work,
-            apply_chunks_done_tracker,
+            apply_chunks_still_applying,
             apply_chunks_done_sender,
         );
 
@@ -1858,7 +1858,7 @@ impl Chain {
         block_hash: CryptoHash,
         block_height: BlockHeight,
         work: Vec<UpdateShardJob>,
-        mut apply_chunks_done_tracker: ApplyChunksDoneTracker,
+        apply_chunks_still_applying: ApplyChunksStillApplying,
         apply_chunks_done_sender: Option<near_async::messaging::Sender<ApplyChunksDoneMessage>>,
     ) {
         let sc = self.apply_chunks_sender.clone();
@@ -1868,10 +1868,7 @@ impl Chain {
             // If we encounter error here, that means the receiver is deallocated and the client
             // thread is already shut down. The node is already crashed, so we can unwrap here
             sc.send((block_hash, res)).unwrap();
-            if let Err(_) = apply_chunks_done_tracker.set_done() {
-                // This should never happen, if it does, it means there is a bug in our code.
-                log_assert!(false, "apply chunks are called twice for block {block_hash:?}");
-            }
+            drop(apply_chunks_still_applying);
             if let Some(sender) = apply_chunks_done_sender {
                 sender.send(ApplyChunksDoneMessage {});
             }
@@ -2296,6 +2293,8 @@ impl Chain {
             invalid_chunks,
         )?;
 
+        let (apply_chunks_done_waiter, apply_chunks_still_applying) = ApplyChunksDoneWaiter::new();
+
         Ok((
             apply_chunk_work,
             BlockPreprocessInfo {
@@ -2305,9 +2304,10 @@ impl Chain {
                 challenges_result,
                 challenged_blocks,
                 provenance: provenance.clone(),
-                apply_chunks_done_tracker: ApplyChunksDoneTracker::new(),
+                apply_chunks_done_waiter,
                 block_start_processing_time: block_received_time,
             },
+            apply_chunks_still_applying,
         ))
     }
 
```

### core/async/src/test_loop.rs
```diff
@@ -434,6 +434,9 @@ impl Drop for TestLoopV2 {
     fn drop(&mut self) {
         self.queue_received_events();
         if let Some(event) = self.events.pop() {
+            // Drop any references that may be held by the event callbacks. This can help
+            // with destruction of the data.
+            self.events.clear();
             panic!(
                 "Event scheduled at {} is not handled at the end of the test: {}.
                  Consider calling `test.shutdown_and_drain_remaining_events(...)`.",
```

### integration-tests/Cargo.toml
```diff
@@ -167,4 +167,3 @@ sandbox = [
 ]
 no_cache = ["nearcore/no_cache"]
 calimero_zero_storage = []
-testloop = ["near-chain/testloop"]
```

### integration-tests/src/tests/client/state_dump.rs
```diff
@@ -9,7 +9,6 @@ use near_client::sync::external::{external_storage_location, StateFileType};
 use near_client::test_utils::TestEnv;
 use near_client::ProcessTxResponse;
 use near_crypto::{InMemorySigner, KeyType, Signer};
-use near_network::test_utils::wait_or_timeout;
 use near_o11y::testonly::init_test_logger;
 use near_primitives::block::Tip;
 use near_primitives::shard_layout::ShardUId;
@@ -23,7 +22,6 @@ use near_store::adapter::{StoreAdapter, StoreUpdateAdapter};
 use near_store::Store;
 use nearcore::state_sync::StateSyncDumper;
 use nearcore::test_utils::TestEnvNightshadeSetupExt;
-use std::ops::ControlFlow;
 use std::sync::Arc;
 
 #[test]
@@ -35,86 +33,83 @@ fn test_state_dump() {
     let mut genesis = Genesis::test(vec!["test0".parse().unwrap(), "test1".parse().unwrap()], 1);
     genesis.config.epoch_length = 25;
 
-    near_actix_test_utils::run_actix(async {
-        let mut env = TestEnv::builder(&genesis.config)
-            .clients_count(1)
-            .use_state_snapshots()
-            .real_stores()
-            .nightshade_runtimes(&genesis)
-            .build();
-
-        let chain = &env.clients[0].chain;
-        let epoch_manager = env.clients[0].epoch_manager.clone();
-        let runtime = env.clients[0].runtime_adapter.clone();
-        let shard_tracker = chain.shard_tracker.clone();
-        let mut config = env.clients[0].config.clone();
-        let root_dir = tempfile::Builder::new().prefix("state_dump").tempdir().unwrap();
-        config.state_sync.dump = Some(DumpConfig {
-            location: Filesystem { root_dir: root_dir.path().to_path_buf() },
-            restart_dump_for_shards: None,
-            iteration_delay: Some(Duration::ZERO),
-            credentials_file: None,
-        });
-
-        let validator = MutableConfigValue::new(
-            Some(Arc::new(EmptyValidatorSigner::new("test0".parse().unwrap()))),
-            "validator_signer",
-        );
-        let mut state_sync_dumper = StateSyncDumper {
-            clock: Clock::real(),
-            client_config: config.clone(),
-            chain_genesis: ChainGenesis::new(&genesis.config),
-            epoch_manager: epoch_manager.clone(),
-            shard_tracker,
-            runtime,
-            validator,
-            dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
-            handle: None,
-        };
-        state_sync_dumper.start().unwrap();
-
-        const MAX_HEIGHT: BlockHeight = 37;
-        for i in 1..=MAX_HEIGHT {
-            let block = env.clients[0].produce_block(i as u64).unwrap().unwrap();
-            env.process_block(0, block, Provenance::PRODUCED);
-        }
-        let head = &env.clients[0].chain.head().unwrap();
-        let epoch_id = head.clone().epoch_id;
-        let epoch_info = epoch_manager.get_epoch_info(&epoch_id).unwrap();
-        let epoch_height = epoch_info.epoch_height();
-
-        wait_or_timeout(100, 10000, || async {
-            let mut all_parts_present = true;
-
-            let shard_ids = epoch_manager.shard_ids(&epoch_id).unwrap();
-            assert_ne!(shard_ids.len(), 0);
-
-            for shard_id in shard_ids {
-                let num_parts = 1;
-                for part_id in 0..num_parts {
-                    let path = root_dir.path().join(external_storage_location(
-                        "unittest",
-                        &epoch_id,
-                        epoch_height,
-                        shard_id,
-                        &StateFileType::StatePart { part_id, num_parts },
-                    ));
-                    if std::fs::read(&path).is_err() {
-                        tracing::info!("Missing {:?}", path);
-                        all_parts_present = false;
-                    }
+    let mut env = TestEnv::builder(&genesis.config)
+        .clients_count(1)
+        .use_state_snapshots()
+        .real_stores()
+        .nightshade_runtimes(&genesis)
+        .build();
+
+    let chain = &env.clients[0].chain;
+    let epoch_manager = env.clients[0].epoch_manager.clone();
+    let runtime = env.clients[0].runtime_adapter.clone();
+    let shard_tracker = chain.shard_tracker.clone();
+    let mut config = env.clients[0].config.clone();
+    let root_dir = tempfile::Builder::new().prefix("state_dump").tempdir().unwrap();
+    config.state_sync.dump = Some(DumpConfig {
+        location: Filesystem { root_dir: root_dir.path().to_path_buf() },
+        restart_dump_for_shards: None,
+        iteration_delay: Some(Duration::ZERO),
+        credentials_file: None,
+    });
+
+    let validator = MutableConfigValue::new(
+        Some(Arc::new(EmptyValidatorSigner::new("test0".parse().unwrap()))),
+        "validator_signer",
+    );
+    let mut state_sync_dumper = StateSyncDumper {
+        clock: Clock::real(),
+        client_config: config,
+        chain_genesis: ChainGenesis::new(&genesis.config),
+        epoch_manager: epoch_manager.clone(),
+        shard_tracker,
+        runtime,
+        validator,
+        dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
+        handle: None,
+    };
+    state_sync_dumper.start().unwrap();
+
+    const MAX_HEIGHT: BlockHeight = 37;
+    for i in 1..=MAX_HEIGHT {
+        let block = env.clients[0].produce_block(i as u64).unwrap().unwrap();
+        env.process_block(0, block, Provenance::PRODUCED);
+    }
+    let head = &env.clients[0].chain.head().unwrap();
+    let epoch_id = head.clone().epoch_id;
+    let epoch_info = epoch_manager.get_epoch_info(&epoch_id).unwrap();
+    let epoch_height = epoch_info.epoch_height();
+
+    for attempt in 0.. {
+        let mut all_parts_present = true;
+
+        let shard_ids = epoch_manager.shard_ids(&epoch_id).unwrap();
+        assert_ne!(shard_ids.len(), 0);
+
+        for shard_id in shard_ids {
+            let num_parts = 1;
+            for part_id in 0..num_parts {
+                let path = root_dir.path().join(external_storage_location(
+                    "unittest",
+                    &epoch_id,
+                    epoch_height,
+                    shard_id,
+                    &StateFileType::StatePart { part_id, num_parts },
+                ));
+                if std::fs::read(&path).is_err() {
+                    tracing::info!("Missing {:?}", path);
+                    all_parts_present = false;
                 }
             }
-            if all_parts_present {
-                ControlFlow::Break(())
-            } else {
-                ControlFlow::Continue(())
-            }
-        })
-        .await
-        .unwrap();
-        actix_rt::System::current().stop();
-    });
+        }
+        if all_parts_present {
+            break;
+        }
+        if attempt >= 100 {
+            panic!("Failed to dump state parts");
+        }
+        std::thread::sleep(std::time::Duration::from_millis(100));
+    }
 }
 
 /// This function tests that after a node does state sync, it has the data that corresponds to the state of the epoch previous to the dumping node's final block.
@@ -136,251 +131,248 @@ fn run_state_sync_with_dumped_parts(
     } else {
         tracing::info!("Testing for case when head is in new epoch, but final block isn't for the dumping node...");
     }
-    near_actix_test_utils::run_actix(async {
-        let mut genesis = Genesis::test(vec!["test0".parse().unwrap()], 1);
-        genesis.config.epoch_length = epoch_length;
-        let num_clients = 2;
-        let mut env = TestEnv::builder(&genesis.config)
-            .clients_count(num_clients)
-            .use_state_snapshots()
-            .real_stores()
-            .nightshade_runtimes(&genesis)
-            .build();
-
-        let signer = InMemorySigner::from_seed("test0".parse().unwrap(), KeyType::ED25519, "test0");
-        let validator = MutableConfigValue::new(
-            Some(Arc::new(InMemoryValidatorSigner::from_signer(signer.clone()).into())),
-            "validator_signer",
-        );
-        let genesis_block = env.clients[0].chain.get_block_by_height(0).unwrap();
-        let genesis_hash = *genesis_block.hash();
-
-        let mut blocks = vec![];
-        let chain = &env.clients[0].chain;
-        let epoch_manager = env.clients[0].epoch_manager.clone();
-        let runtime = env.clients[0].runtime_adapter.clone();
-        let shard_tracker = chain.shard_tracker.clone();
-        let mut config = env.clients[0].config.clone();
-        let root_dir = tempfile::Builder::new().prefix("state_dump").tempdir().unwrap();
-        config.state_sync.dump = Some(DumpConfig {
-            location: Filesystem { root_dir: root_dir.path().to_path_buf() },
-            restart_dump_for_shards: None,
-            iteration_delay: Some(Duration::ZERO),
-            credentials_file: None,
-        });
-        let mut state_sync_dumper = StateSyncDumper {
-            clock: Clock::real(),
-            client_config: config.clone(),
-            chain_genesis: ChainGenesis::new(&genesis.config),
-            epoch_manager: epoch_manager.clone(),
-            shard_tracker,
-            runtime,
-            validator,
-            dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
-            handle: None,
-        };
-        state_sync_dumper.start().unwrap();
-
-        let account_creation_at_height = (account_creation_at_epoch_height - 1) * epoch_length + 2;
-
-        let dump_node_head_height = if is_final_block_in_new_epoch {
-            (1 + account_creation_at_epoch_height) * epoch_length
-        } else {
-            account_creation_at_epoch_height * epoch_length + 1
-        };
-
-        let signer: Signer = signer.into();
-        for i in 1..=dump_node_head_height {
-            if i == account_creation_at_height {
-                let tx = SignedTransaction::create_account(
-                    1,
-                    "test0".parse().unwrap(),
-                    "test_account".parse().unwrap(),
-                    NEAR_BASE,
-                    signer.public_key(),
-                    &signer,
-                    genesis_hash,
-                );
-                assert_eq!(env.clients[0].process_tx(tx, false, false), ProcessTxResponse::ValidTx);
-            }
-            let block = env.clients[0].produce_block(i).unwrap().unwrap();
-            blocks.push(block.clone());
-            env.process_block(0, block.clone(), Provenance::PRODUCED);
-            env.process_block(1, block.clone(), Provenance::NONE);
+    let mut genesis = Genesis::test(vec!["test0".parse().unwrap()], 1);
+    genesis.config.epoch_length = epoch_length;
+    let num_clients = 2;
+    let mut env = TestEnv::builder(&genesis.config)
+        .clients_count(num_clients)
+        .use_state_snapshots()
+        .real_stores()
+        .nightshade_runtimes(&genesis)
+        .build();
+
+    let signer = InMemorySigner::from_seed("test0".parse().unwrap(), KeyType::ED25519, "test0");
+    let validator = MutableConfigValue::new(
+        Some(Arc::new(InMemoryValidatorSigner::from_signer(signer.clone()).into())),
+        "validator_signer",
+    );
+    let genesis_block = env.clients[0].chain.get_block_by_height(0).unwrap();
+    let genesis_hash = *genesis_block.hash();
+
+    let mut blocks = vec![];
+    let chain = &env.clients[0].chain;
+    let epoch_manager = env.clients[0].epoch_manager.clone();
+    let runtime = env.clients[0].runtime_adapter.clone();
+    let shard_tracker = chain.shard_tracker.clone();
+    let mut config = env.clients[0].config.clone();
+    let root_dir = tempfile::Builder::new().prefix("state_dump").tempdir().unwrap();
+    config.state_sync.dump = Some(DumpConfig {
+        location: Filesystem { root_dir: root_dir.path().to_path_buf() },
+        restart_dump_for_shards: None,
+        iteration_delay: Some(Duration::ZERO),
+        credentials_file: None,
+    });
+    let mut state_sync_dumper = StateSyncDumper {
+        clock: Clock::real(),
+        client_config: config.clone(),
+        chain_genesis: ChainGenesis::new(&genesis.config),
+        epoch_manager: epoch_manager.clone(),
+        shard_tracker,
+        runtime,
+        validator,
+        dump_future_runner: StateSyncDumper::arbiter_dump_future_runner(),
+        handle: None,
+    };
+    state_sync_dumper.start().unwrap();
+
+    let account_creation_at_height = (account_creation_at_epoch_height - 1) * epoch_length + 2;
+
+    let dump_node_head_height = if is_final_block_in_new_epoch {
+        (1 + account_creation_at_epoch_height) * epoch_length
+    } else {
+        account_creation_at_epoch_height * epoch_length + 1
+    };
+
+    let signer: Signer = signer.into();
+    for i in 1..=dump_node_head_height {
+        if i == account_creation_at_height {
+            let tx = SignedTransaction::create_account(
+                1,
+                "test0".parse().unwrap(),
+                "test_account".parse().unwrap(),
+                NEAR_BASE,
+                signer.public_key(),
+                &signer,
+                genesis_hash,
+            );
+            assert_eq!(env.clients[0].process_tx(tx, false, false), ProcessTxResponse::ValidTx);
         }
+        let block = env.clients[0].produce_block(i).unwrap().unwrap();
+        blocks.push(block.clone());
+        env.process_block(0, block.clone(), Provenance::PRODUCED);
+        env.process_block(1, block.clone(), Provenance::NONE);
+    }
 
-        // check that the new account exists
-        let head = env.clients[0].chain.head().unwrap();
-        let head_block = env.clients[0].chain.get_block(&head.last_block_hash).unwrap();
-        let shard_uid = ShardUId::single_shard();
-        let shard_id = shard_uid.shard_id();
-        let response = env.clients[0]
-            .runtime_adapter
-            .query(
-                shard_uid,
-                &head_block.chunks()[0].prev_state_root(),
-                head.height,
-                0,
-                &head.prev_block_hash,
-                &head.last_block_hash,
-                head_block.header().epoch_id(),
-                &QueryRequest::ViewAccount { account_id: "test_account".parse().unwrap() },
-            )
-            .unwrap();
-        assert_matches!(response.kind, QueryResponseKind::ViewAccount(_));
-
-        let header = env.clients[0].chain.get_block_header(&head.last_block_hash).unwrap();
-        let final_block_hash = header.last_final_block();
-        let final_block_header = env.clients[0].chain.get_block_header(final_block_hash).unwrap();
-
-        tracing::info!(
-            dump_node_head_height,
-            final_block_height = final_block_header.height(),
-            "Dumping node state"
-        );
+    // check that the new account exists
+    let head = env.clients[0].chain.head().unwrap();
+    let head_block = env.clients[0].chain.get_block(&head.last_block_hash).unwrap();
+    let shard_uid = ShardUId::single_shard();
+    let shard_id = shard_uid.shard_id();
+    let response = env.clients[0]
+        .runtime_adapter
+        .query(
+            shard_uid,
+            &head_block.chunks()[0].prev_state_root(),
+            head.height,
+            0,
+            &head.prev_block_hash,
+            &head.last_block_hash,
+            head_block.header().epoch_id(),
+            &QueryRequest::ViewAccount { account_id: "test_account".parse().unwrap() },
+        )
+        .unwrap();
+    assert_matches!(response.kind, QueryResponseKind::ViewAccount(_));
 
-        // check if final block is in the same epoch as head for dumping node
-        if is_final_block_in_new_epoch {
-            assert_eq!(header.epoch_id().clone(), final_block_header.epoch_id().clone())
-        } else {
-            assert_ne!(header.epoch_id().clone(), final_block_header.epoch_id().clone())
-        }
+    let header = env.clients[0].chain.get_block_header(&head.last_block_hash).unwrap();
+    let final_block_hash = header.last_final_block();
+    let final_block_header = env.clients[0].chain.get_block_header(final_block_hash).unwrap();
 
-        let epoch_id = *final_block_header.epoch_id();
-        let epoch_info = epoch_manager.get_epoch_info(&epoch_id).unwrap();
-        let epoch_height = epoch_info.epoch_height();
+    tracing::info!(
+        dump_node_head_height,
+        final_block_height = final_block_header.height(),
+        "Dumping node state"
+    );
 
-        let sync_block_height = (epoch_length * epoch_height + 1) as usize;
-        let sync_hash = *blocks[sync_block_height - 1].hash();
+    // check if final block is in the same epoch as head for dumping node
+    if is_final_block_in_new_epoch {
+        assert_eq!(header.epoch_id().clone(), final_block_header.epoch_id().clone())
+    } else {
+        assert_ne!(header.epoch_id().clone(), final_block_header.epoch_id().clone())
+    }
 
-        // the block at sync_block_height should be the start of an epoch
-        assert_ne!(
-            blocks[sync_block_height - 1].header().epoch_id(),
-            blocks[sync_block_height - 2].header().epoch_id()
-        );
-        assert!(env.clients[0].chain.check_sync_hash_validity(&sync_hash).unwrap());
-        let state_sync_header =
-            env.clients[0].chain.get_state_response_header(shard_id, sync_hash).unwrap();
-        let state_root = state_sync_header.chunk_prev_state_root();
-        let num_parts = state_sync_header.num_state_parts();
-
-        wait_or_timeout(100, 10000, || async {
-            let mut all_parts_present = true;
-
-            let shard_ids = epoch_manager.shard_ids(&epoch_id).unwrap();
-            assert_ne!(shard_ids.len(), 0);
-
-            for shard_id in shard_ids {
-                for part_id in 0..num_parts {
-                    let path = root_dir.path().join(external_storage_location(
-                        &config.chain_id,
-                        &epoch_id,
-                        epoch_height,
-                        shard_id,
-                        &StateFileType::StatePart { part_id, num_parts },
-                    ));
-                    if std::fs::read(&path).is_err() {
-                        tracing::info!("dumping node: Missing {:?}", path);
-                        all_parts_present = false;
-                    } else {
-                        tracing::info!("dumping node: Populated {:?}", path);
-                    }
+    let epoch_id = *final_block_header.epoch_id();
+    let epoch_info = epoch_manager.get_epoch_info(&epoch_id).unwrap();
+    let epoch_height = epoch_info.epoch_height();
+
+    let sync_block_height = (epoch_length * epoch_height + 1) as usize;
+    let sync_hash = *blocks[sync_block_height - 1].hash();
+
+    // the block at sync_block_height should be the start of an epoch
+    assert_ne!(
+        blocks[sync_block_height - 1].header().epoch_id(),
+        blocks[sync_block_height - 2].header().epoch_id()
+    );
+    assert!(env.clients[0].chain.check_sync_hash_validity(&sync_hash).unwrap());
+    let state_sync_header =
+        env.clients[0].chain.get_state_response_header(shard_id, sync_hash).unwrap();
+    let state_root = state_sync_header.chunk_prev_state_root();
+    let num_parts = state_sync_header.num_state_parts();
+
+    for attempt in 0.. {
+        let mut all_parts_present = true;
+
+        let shard_ids = epoch_manager.shard_ids(&epoch_id).unwrap();
+        assert_ne!(shard_ids.len(), 0);
+
+        for shard_id in shard_ids {
+            for part_id in 0..num_parts {
+                let path = root_dir.path().join(external_storage_location(
+                    &config.chain_id,
+                    &epoch_id,
+                    epoch_height,
+                    shard_id,
+                    &StateFileType::StatePart { part_id, num_parts },
+                ));
+                if std::fs::read(&path).is_err() {
+                    tracing::info!("dumping node: Missing {:?}", path);
+                    all_parts_present = false;
+                } else {
+                    tracing::info!("dumping node: Populated {:?}", path);
                 }
             }
-            if all_parts_present {
-                ControlFlow::Break(())
-            } else {
-                ControlFlow::Continue(())
-            }
-        })
-        .await
-        .unwrap();
-
-        // Simulate state sync by reading the dumped parts from the external storage and applying them to the other node
-        tracing::info!("syncing node: simulating state sync..");
-        env.clients[1].chain.set_state_header(shard_id, sync_hash, state_sync_header).unwrap();
-        let runtime_client_1 = Arc::clone(&env.clients[1].runtime_adapter);
-        let mut store_update = runtime_client_1.store().store_update();
-        assert!(runtime_client_1
-            .get_flat_storage_manager()
-            .remove_flat_storage_for_shard(
-                ShardUId::single_shard(),
-                &mut store_update.flat_store_update()
-            )
-            .unwrap());
-        store_update.commit().unwrap();
-        let shard_id = new_shard_id_tmp(0);
-        for part_id in 0..num_parts {
-            let path = root_dir.path().join(external_storage_location(
-                &config.chain_id,
-                &epoch_id,
-                epoch_height,
-                shard_id,
-                &StateFileType::StatePart { part_id, num_parts },
-            ));
-            let part = std::fs::read(&path).expect("Part file not found. It should exist");
-            let part_id = PartId::new(part_id, num_parts);
-            runtime_client_1
-                .apply_state_part(shard_id, &state_root, part_id, &part, &epoch_id)
-                .unwrap();
         }
-        env.clients[1].chain.set_state_finalize(shard_id, sync_hash).unwrap();
-        tracing::info!("syncing node: state sync finished.");
+        if all_parts_present {
+            break;
+        }
+        if attempt >= 100 {
+            panic!("dumping node: Failed to dump state parts");
+        }
+        std::thread::sleep(std::time::Duration::from_millis(100));
+    }
 
-        let synced_block = env.clients[1].chain.get_block(&sync_hash).unwrap();
-        let synced_block_header = env.clients[1].chain.get_block_header(&sync_hash).unwrap();
-        let synced_block_tip = Tip::from_header(&synced_block_header);
-        let response = env.clients[1].runtime_adapter.query(
+    // Simulate state sync by reading the dumped parts from the external storage and applying them to the other node
+    tracing::info!("syncing node: simulating state sync..");
+    env.clients[1].chain.set_state_header(shard_id, sync_hash, state_sync_header).unwrap();
+    let runtime_client_1 = Arc::clone(&env.clients[1].runtime_adapter);
+    let mut store_update = runtime_client_1.store().store_update();
+    assert!(runtime_client_1
+        .get_flat_storage_manager()
+        .remove_flat_storage_for_shard(
             ShardUId::single_shard(),
-            &synced_block.chunks()[0].prev_state_root(),
-            synced_block_tip.height,
-            0,
-            &synced_block_tip.prev_block_hash,
-            &synced_block_tip.last_block_hash,
-            synced_block_header.epoch_id(),
-            &QueryRequest::ViewAccount { account_id: "test_account".parse().unwrap() },
-        );
+            &mut store_update.flat_store_update()
+        )
+        .unwrap());
+    store_update.commit().unwrap();
+    let shard_id = new_shard_id_tmp(0);
+    for part_id in 0..num_parts {
+        let path = root_dir.path().join(external_storage_location(
+            &config.chain_id,
+            &epoch_id,
+            epoch_height,
+            shard_id,
+            &StateFileType::StatePart { part_id, num_parts },
+        ));
+        let part = std::fs::read(&path).expect("Part file not found. It should exist");
+        let part_id = PartId::new(part_id, num_parts);
+        runtime_client_1
+            .apply_state_part(shard_id, &state_root, part_id, &part, &epoch_id)
+            .unwrap();
+    }
+    env.clients[1].chain.set_state_finalize(shard_id, sync_hash).unwrap();
+    tracing::info!("syncing node: state sync finished.");
+
+    let synced_block = env.clients[1].chain.get_block(&sync_hash).unwrap();
+    let synced_block_header = env.clients[1].chain.get_block_header(&sync_hash).unwrap();
+    let synced_block_tip = Tip::from_header(&synced_block_header);
+    let response = env.clients[1].runtime_adapter.query(
+        ShardUId::single_shard(),
+        &synced_block.chunks()[0].prev_state_root(),
+        synced_block_tip.height,
+        0,
+        &synced_block_tip.prev_block_hash,
+        &synced_block_tip.last_block_hash,
+        synced_block_header.epoch_id(),
+        &QueryRequest::ViewAccount { account_id: "test_account".parse().unwrap() },
+    );
 
-        if is_final_block_in_new_epoch {
-            tracing::info!(?response, "New Account should exist");
-            assert_matches!(
-                response.unwrap().kind,
-                QueryResponseKind::ViewAccount(_),
-                "the synced node should have information about the created account"
-            );
+    if is_final_block_in_new_epoch {
+        tracing::info!(?response, "New Account should exist");
+        assert_matches!(
+            response.unwrap().kind,
+            QueryResponseKind::ViewAccount(_),
+            "the synced node should have information about the created account"
+        );
 
-            // Check that inlined flat state values remain inlined.
-            {
-                let store0 = env.clients[0].chain.chain_store().store();
-                let store1 = env.clients[1].chain.chain_store().store();
-                let (num_inlined_before, num_ref_before) = count_flat_state_value_kinds(store0);
-                let (num_inlined_after, num_ref_after) = count_flat_state_value_kinds(store1);
-                // Nothing new created, number of flat state values should be identical.
-                assert_eq!(num_inlined_before, num_inlined_after);
-                assert_eq!(num_ref_before, num_ref_after);
-            }
-        } else {
-            tracing::info!(?response, "New Account shouldn't exist");
-            assert!(response.is_err());
-            assert_matches!(
-                response.unwrap_err(),
-                QueryError::UnknownAccount { .. },
-                "the synced node should not have information about the created account"
-            );
+        // Check that inlined flat state values remain inlined.
+        {
+            let store0 = env.clients[0].chain.chain_store().store();
+            let store1 = env.clients[1].chain.chain_store().store();
+            let (num_inlined_before, num_ref_before) = count_flat_state_value_kinds(store0);
+            let (num_inlined_after, num_ref_after) = count_flat_state_value_kinds(store1);
+            // Nothing new created, number of flat state values should be identical.
+            assert_eq!(num_inlined_before, num_inlined_after);
+            assert_eq!(num_ref_before, num_ref_after);
+        }
+    } else {
+        tracing::info!(?response, "New Account shouldn't exist");
+        assert!(response.is_err());
+        assert_matches!(
+            response.unwrap_err(),
+            QueryError::UnknownAccount { .. },
+            "the synced node should not have information about the created account"
+        );
 
-            // Check that inlined flat state values remain inlined.
-            {
-                let store0 = env.clients[0].chain.chain_store().store();
-                let store1 = env.clients[1].chain.chain_store().store();
-                let (num_inlined_before, _num_ref_before) = count_flat_state_value_kinds(store0);
-                let (num_inlined_after, _num_ref_after) = count_flat_state_value_kinds(store1);
-                // Created a new entry, but inlined values should stay inlinedNothing new created, number of flat state values should be identical.
-                assert!(num_inlined_before >= num_inlined_after);
-                assert!(num_inlined_after > 0);
-            }
+        // Check that inlined flat state values remain inlined.
+        {
+            let store0 = env.clients[0].chain.chain_store().store();
+            let store1 = env.clients[1].chain.chain_store().store();
+            let (num_inlined_before, _num_ref_before) = count_flat_state_value_kinds(store0);
+            let (num_inlined_after, _num_ref_after) = count_flat_state_value_kinds(store1);
+            // Created a new entry, but inlined values should stay inlinedNothing new created, number of flat state values should be identical.
+            assert!(num_inlined_before >= num_inlined_after);
+            assert!(num_inlined_after > 0);
         }
-        actix_rt::System::current().stop();
-    });
+    }
 }
 
 /// This test verifies that after state sync, the syncing node has the data that corresponds to the state of the epoch previous to the dumping node's final block.
```
