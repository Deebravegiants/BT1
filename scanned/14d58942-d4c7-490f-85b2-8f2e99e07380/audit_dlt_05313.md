# [?] fix: prevent PoA leader deadlock after reconciliation import (#3261)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-04-16
Source: https://github.com/FuelLabs/fuel-core/commit/0faeb99ce1d01743838394acaacf64907aba5a24
Type: security-commit

## Details
fix: prevent PoA leader deadlock after reconciliation import (#3261)

## Summary

- Fixes a deadlock in the PoA service that caused a 30-minute block
production outage on testnet (April 9, 2026)
- After a FENCING_ERROR, reconciliation imports a block via
`execute_and_commit` which marks it as `Source::Network`. The SyncTask
sees this and transitions from `Synced` → `NotSynced`. On the next
iteration, `ensure_synced()` blocks forever — the leader can't produce
while blocked, and the SyncTask needs a locally-produced block to
recover. Classic deadlock.
- Fix: add a reconciliation watermark (`Arc<AtomicU32>`) shared between
`MainTask` and `SyncTask`. Before importing reconciliation blocks,
`MainTask` sets the watermark to the max height. `SyncTask` treats
blocks at heights ≤ the watermark as locally produced, staying `Synced`.

## Details

**Root cause chain:**
1. `importer.rs:584-585` — `execute_and_commit` always uses
`ImportResult::new_from_network()`
2. `sync.rs:186-203` — SyncTask transitions `Synced → NotSynced` on
non-local block with height > current
3. `service.rs:501-521` — `ensure_synced()` blocks on
`sync_state.changed()` when `NotSynced`
4. Deadlock: leader blocked in `ensure_synced()`, SyncTask waiting for
locally-produced block that can never arrive

**Why a watermark:** A bool flag has a race condition — the SyncTask may
not poll the broadcast channel until after the flag is cleared. The
watermark encodes a permanent fact ("all blocks up to height N were
reconciled") that never needs clearing.

**Files changed (all within `fuel-core-poa`):**
- `sync.rs` — Add `reconciliation_watermark` field, check it in block
handler
- `service.rs` — Create shared watermark, set via `fetch_max` during
reconciliation
- `service_test.rs` — Add deadlock reproduction test

## Test plan

- [x]
`sync_task__network_block_at_reconciliation_height_causes_not_synced_without_watermark`
— confirms bug mechanism (network block → NotSynced)
- [x] `sync_task__network_block_within_watermark_stays_synced` —
verifies watermark prevents NotSynced; blocks above watermark still
trigger it
- [x] `main_task__reconciliation_import_does_not_deadlock_leader` — full
service-level deadlock reproduction (fails without fix, passes with)
- [x] All 51 existing `fuel-core-poa` tests pass

---------

Co-authored-by: Green Baneling <XgreenX9999@gmail.com>
Co-authored-by: Hannes Karppila <2204863+Dentosal@users.noreply.github.com>

### .changes/fixed/3261.md
```diff
@@ -0,0 +1 @@
+Fix PoA leader deadlock after reconciliation import where `ensure_synced()` blocked forever because `execute_and_commit` marked reconciliation blocks as `Source::Network`, causing the SyncTask to transition to `NotSynced`.
```

### crates/services/consensus_module/poa/src/service.rs
```diff
@@ -143,6 +143,9 @@ pub struct MainTask<B, I, S, PB, C, RS, RP> {
     /// externally controlled start of block production
     block_production_ready_signal: BlockProductionReadySignal<RS>,
     reconciliation_port: RP,
+    /// Shared with SyncTask — blocks at heights <= this watermark were
+    /// imported via reconciliation and should not trigger NotSynced.
+    reconciliation_watermark: Arc<std::sync::atomic::AtomicU32>,
 }
 
 impl<B, I, S, PB, C, RS, RP> MainTask<B, I, S, PB, C, RS, RP>
@@ -183,12 +186,15 @@ where
             ..
         } = config;
 
+        let reconciliation_watermark = Arc::new(std::sync::atomic::AtomicU32::new(0));
+
         let sync_task = SyncTask::new(
             peer_connections_stream,
             min_connected_reserved_peers,
             time_until_synced,
             block_stream,
             last_block,
+            Arc::clone(&reconciliation_watermark),
         );
 
         let sync_task_handle = ServiceRunner::new(sync_task);
@@ -213,6 +219,7 @@ where
             production_timeout,
             block_production_ready_signal,
             reconciliation_port,
+            reconciliation_watermark,
         }
     }
 
@@ -628,6 +635,17 @@ where
                         continue;
                     }
 
+                    // Set watermark to this block's height so SyncTask
+                    // doesn't transition to NotSynced when it sees the
+                    // broadcast. execute_and_commit marks blocks as
+                    // Source::Network, which would otherwise cause a
+                    // Synced → NotSynced transition and deadlock
+                    // ensure_synced().
+                    self.reconciliation_watermark.fetch_max(
+                        u32::from(block_height),
+                        std::sync::atomic::Ordering::Release,
+                    );
+
                     match self.block_importer.execute_and_commit(block).await {
                         Ok(()) => {
                             self.last_height = block_height;
```

### crates/services/consensus_module/poa/src/service_test.rs
```diff
@@ -47,9 +47,12 @@ use fuel_core_types::{
     fuel_tx::*,
     fuel_types::BlockHeight,
     secrecy::Secret,
-    services::executor::{
-        ExecutionResult,
-        UncommittedResult,
+    services::{
+        block_importer::BlockImportInfo,
+        executor::{
+            ExecutionResult,
+            UncommittedResult,
+        },
     },
     signer::SignMode,
     tai64::{
@@ -940,3 +943,144 @@ async fn consensus_service__run__will_produce_blocks_with_ready_signal() {
     let produced_block = block_receiver.recv().await.unwrap();
     assert!(matches!(produced_block, FakeProducedBlock::New(_, _)));
 }
+
+/// Reproduces the deadlock from the April 9, 2026 testnet outage.
+///
+/// After a FENCING_ERROR, reconciliation imports a block via
+/// `execute_and_commit` which marks it as `Source::Network`. The SyncTask
+/// sees this non-local block and transitions from Synced → NotSynced.
+/// On the next `run()` iteration, `ensure_synced()` blocks forever
+/// because the leader can't produce locally-sourced blocks while blocked.
+///
+/// This test uses a `FakeReconciliationPort` that returns
+/// `UnreconciledBlocks` on the first call (simulating reconciliation after
+/// fencing error), then switches to `ReconciledLeader`. The
+/// `MockBlockImporter::execute_and_commit` broadcasts a `Source::Network`
+/// block into the block_stream, triggering the SyncTask's NotSynced
+/// transition. Without the watermark fix, the service deadlocks and
+/// never produces a block.
+#[tokio::test]
+async fn main_task__reconciliation_import_does_not_deadlock_leader() {
+    // given: a PoA service with Trigger::Interval
+    let config = Config {
+        trigger: Trigger::Interval {
+            block_time: Duration::from_millis(10),
+        },
+        signer: SignMode::Key(test_signing_key()),
+        metrics: false,
+        min_connected_reserved_peers: 0,
+        time_until_synced: Duration::ZERO,
+        ..Default::default()
+    };
+
+    let (block_producer, mut block_receiver) = FakeBlockProducer::new();
+
+    // Use an mpsc channel to feed both execute_and_commit results and
+    // the SyncTask's block_stream. This simulates what the real importer
+    // does when `execute_and_commit` commits a block and broadcasts it.
+    let (block_import_sender, block_import_receiver) =
+        tokio::sync::mpsc::channel::<BlockImportInfo>(16);
+
+    let mut block_importer = MockBlockImporter::default();
+    block_importer.expect_commit_result().returning(|_| Ok(()));
+
+    // When execute_and_commit is called for the reconciliation block,
+    // send it as Source::Network — this is what the real importer
+    // does (ImportResult::new_from_network at importer.rs:585).
+    let sender_for_import = block_import_sender.clone();
+    block_importer
+        .expect_execute_and_commit()
+        .returning(move |block| {
+            let header = block.entity.header().clone();
+            let _ = sender_for_import.try_send(BlockImportInfo::new_from_network(header));
+            Ok(())
+        });
+
+    // The block_stream feeds the SyncTask — wrap the mpsc receiver.
+    // Use Option+Mutex to allow moving out of the FnMut closure.
+    let receiver_cell = Arc::new(StdMutex::new(Some(block_import_receiver)));
+    block_importer.expect_block_stream().returning(move || {
+        let rx = receiver_cell
+            .lock()
+            .unwrap()
+            .take()
+            .expect("block_stream called more than once");
+        Box::pin(tokio_stream::wrappers::ReceiverStream::new(rx))
+    });
+
+    block_importer
+        .expect_latest_block_height()
+        .returning(|| Ok(Some(BlockHeight::from(0u32))));
+
+    let txpool = MockTransactionPool::no_tx_updates();
+    let p2p_port = generate_p2p_port();
+    let predefined_blocks = InMemoryPredefinedBlocks::new(HashMap::new());
+    let time = TestTime::at_unix_epoch();
+    let watch = time.watch();
+
+    // Create a reconciliation port that returns UnreconciledBlocks once,
+    // then switches to ReconciledLeader for subsequent calls.
+    let block = block_for_height(2);
+    let consensus = FakeBlockSigner { succeeds: true }
+        .seal_block(&block)
+        .await
+        .unwrap();
+    let unreconciled = LeaderState::UnreconciledBlocks(vec![SealedBlock {
+        entity: block,
+        consensus,
+    }]);
+
+    let reconciliation_port = FakeReconciliationPort::with_state(Ok(unreconciled));
+    let reconciliation_state = reconciliation_port.state.clone();
+
+    let task = MainTask::new(
+        &BlockHeader::new_block(BlockHeight::from(1u32), watch.now()),
+        config,
+        txpool,
+        block_producer,
+        block_importer,
+        p2p_port,
+        FakeBlockSigner { succeeds: true }.into(),
+        predefined_blocks,
+        watch,
+        FakeBlockProductionReadySignal,
+        reconciliation_port,
+    );
+
+    // when: start the service
+    let service = ServiceRunner::new(task);
+    service.start_and_await().await.unwrap();
+
+    // Give time for the reconciliation block to be imported.
+    // After import, switch to ReconciledLeader so the service can
+    // attempt normal block production.
+    tokio::task::yield_now().await;
+    time::advance(Duration::from_millis(20)).await;
+    tokio::task::yield_now().await;
+
+    // Switch reconciliation port to ReconciledLeader
+    {
+        let mut state = reconciliation_state.lock().unwrap();
+        *state = Ok(LeaderState::ReconciledLeader);
+    }
+
+    // then: try to receive a produced block within a timeout.
+    // Without the fix, ensure_synced() deadlocks and no block is produced.
+    let receive_timeout = tokio::spawn(async move {
+        time::timeout(Duration::from_millis(500), block_receiver.recv()).await
+    });
+    time::advance(Duration::from_millis(501)).await;
+    tokio::task::yield_now().await;
+    let receive_result = receive_timeout.await.unwrap();
+
+    let _ = service.stop_and_await().await;
+
+    // This assertion fails without the watermark fix — the service
+    // deadlocks in ensure_synced() and never produces a block.
+    assert!(
+        receive_result.is_ok(),
+        "Expected block production after reconciliation, but the service \
+         deadlocked in ensure_synced() — this is the bug from the \
+         April 9, 2026 testnet outage"
+    );
+}
```

### crates/services/consensus_module/poa/src/sync.rs
```diff
@@ -1,5 +1,11 @@
 use std::{
-    sync::Arc,
+    sync::{
+        Arc,
+        atomic::{
+            AtomicU32,
+            Ordering,
+        },
+    },
     time::Duration,
 };
 
@@ -52,6 +58,10 @@ pub struct SyncTask {
     state_receiver: watch::Receiver<SyncState>,
     inner_state: InnerSyncState,
     timer: Option<tokio::time::Interval>,
+    /// Blocks at heights <= this watermark were imported via reconciliation
+    /// by the leader and should not trigger Synced → NotSynced transitions.
+    /// Set by MainTask via `fetch_max`, monotonically increasing, never cleared.
+    reconciliation_watermark: Arc<AtomicU32>,
 }
 
 impl SyncTask {
@@ -61,6 +71,7 @@ impl SyncTask {
         time_until_synced: Duration,
         block_stream: BoxStream<BlockImportInfo>,
         block_header: &BlockHeader,
+        reconciliation_watermark: Arc<AtomicU32>,
     ) -> Self {
         let inner_state = InnerSyncState::from_config(
             min_connected_reserved_peers,
@@ -92,6 +103,7 @@ impl SyncTask {
             state_receiver,
             inner_state,
             timer,
+            reconciliation_watermark,
         }
     }
 
@@ -184,7 +196,11 @@ impl RunnableTask for SyncTask {
                         self.restart_timer();
                     }
                     InnerSyncState::Synced { block_header, has_sufficient_peers } if new_block_height > block_header.height() => {
-                        if block_info.is_locally_produced() {
+                        let watermark = self.reconciliation_watermark.load(Ordering::Acquire);
+                        let is_reconciliation = watermark > 0
+                            && u32::from(*new_block_height) <= watermark;
+
+                        if block_info.is_locally_produced() || is_reconciliation {
                             self.inner_state = InnerSyncState::Synced {
                                 block_header: block_info.block_header.clone(),
                                 has_sufficient_peers: *has_sufficient_peers
@@ -278,6 +294,7 @@ impl InnerSyncState {
 }
 
 #[allow(clippy::arithmetic_side_effects)]
+#[allow(non_snake_case)]
 #[cfg(test)]
 mod tests {
     use super::*;
@@ -359,6 +376,7 @@ mod tests {
             time_until_synced,
             block_stream,
             &Default::default(),
+            Arc::new(AtomicU32::new(0)),
         );
 
         (sync_task, watcher, tx)
@@ -598,4 +616,124 @@ mod tests {
         ));
         matches!(*sync_task.state_receiver.borrow(), SyncState::Synced(_));
     }
+
+    /// Reproduces the deadlock root cause: a network-sourced block (from
+    /// reconciliation via `execute_and_commit`) arrives while the SyncTask
+    /// is in Synced state. Without the watermark fix, this transitions
+    /// the SyncTask to NotSynced, which deadlocks the leader's
+    /// `ensure_synced()` call.
+    #[tokio::test]
+    async fn sync_task__network_block_at_reconciliation_height_causes_not_synced_without_watermark()
+     {
+        // given: a SyncTask that starts in Synced state (min_peers=0, time=ZERO)
+        let connections_stream = MockStream::<usize>::new(vec![]).into_boxed();
+        let block_stream = MockStream::<BlockImportInfo>::new(vec![]).into_boxed();
+
+        let (tx, shutdown) =
+            tokio::sync::watch::channel(fuel_core_services::State::Started);
+        let mut watcher: StateWatcher = shutdown.into();
+
+        // Watermark is 0 (not set) — simulates the pre-fix state
+        let watermark = Arc::new(AtomicU32::new(0));
+
+        let mut sync_task = SyncTask::new(
+            connections_stream,
+            0, // min_connected_reserved_peers
+            Duration::ZERO,
+            block_stream,
+            &BlockHeader::new_block(5u32.into(), Tai64::now()),
+            watermark,
+        );
+
+        // Verify we start in Synced state
+        assert!(
+            matches!(*sync_task.state_receiver.borrow(), SyncState::Synced(_)),
+            "SyncTask should start Synced with min_peers=0 and time_until_synced=ZERO"
+        );
+
+        // when: a Source::Network block arrives at height 6 (> current height 5)
+        // This is what happens when reconciliation imports a block via
+        // execute_and_commit, which always uses ImportResult::new_from_network
+        let network_block_stream =
+            MockStream::new(vec![BlockHeader::new_block(6u32.into(), Tai64::now())])
+                .map(BlockImportInfo::new_from_network)
+                .into_boxed();
+        sync_task.block_stream = network_block_stream;
+
+        let _ = sync_task.run(&mut watcher).await;
+
+        // then: SyncTask transitions to NotSynced — THIS IS THE BUG
+        // The leader's ensure_synced() will now block forever because
+        // it can't produce locally-produced blocks while blocked.
+        assert_eq!(
+            SyncState::NotSynced,
+            *sync_task.state_receiver.borrow(),
+            "Without watermark fix, a network-sourced reconciliation block \
+             causes NotSynced — this deadlocks the leader"
+        );
+
+        drop(tx);
+    }
+
+    /// Verifies the watermark fix: when the reconciliation watermark covers
+    /// the block height, a network-sourced block should NOT trigger NotSynced.
+    #[tokio::test]
+    async fn sync_task__network_block_within_watermark_stays_synced() {
+        // given: a SyncTask in Synced state with watermark set to height 6
+        let connections_stream = MockStream::<usize>::new(vec![]).into_boxed();
+        let block_stream = MockStream::<BlockImportInfo>::new(vec![]).into_boxed();
+
+        let (tx, shutdown) =
+            tokio::sync::watch::channel(fuel_core_services::State::Started);
+        let mut watcher: StateWatcher = shutdown.into();
+
+        let watermark = Arc::new(AtomicU32::new(6));
+
+        let mut sync_task = SyncTask::new(
+            connections_stream,
+            0,
+            Duration::ZERO,
+            block_stream,
+            &BlockHeader::new_block(5u32.into(), Tai64::now()),
+            watermark,
+        );
+
+        assert!(matches!(
+            *sync_task.state_receiver.borrow(),
+            SyncState::Synced(_)
+        ));
+
+        // when: a Source::Network block at height 6 (within watermark)
+        let network_block_stream =
+            MockStream::new(vec![BlockHeader::new_block(6u32.into(), Tai64::now())])
+                .map(BlockImportInfo::new_from_network)
+                .into_boxed();
+        sync_task.block_stream = network_block_stream;
+
+        let _ = sync_task.run(&mut watcher).await;
+
+        // then: should stay Synced because watermark covers height 6
+        assert!(
+            matches!(*sync_task.state_receiver.borrow(), SyncState::Synced(_)),
+            "With watermark=6, a network block at height 6 should NOT trigger NotSynced"
+        );
+
+        // when: a Source::Network block at height 7 (ABOVE watermark)
+        let network_block_stream =
+            MockStream::new(vec![BlockHeader::new_block(7u32.into(), Tai64::now())])
+                .map(BlockImportInfo::new_from_network)
+                .into_boxed();
+        sync_task.block_stream = network_block_stream;
+
+        let _ = sync_task.run(&mut watcher).await;
+
+        // then: should transition to NotSynced (watermark doesn't protect above its value)
+        assert_eq!(
+            SyncState::NotSynced,
+            *sync_task.state_receiver.borrow(),
+            "A network block above the watermark should still trigger NotSynced"
+        );
+
+        drop(tx);
+    }
 }
```
