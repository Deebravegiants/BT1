# [?] Fix race condition the `cache_warm_up_executor` (#2059)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2025-11-12
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/9cfe8c00bcd9dfcc1f3f4a06e360d6744e56b930
Type: security-commit

## Details
Fix race condition the `cache_warm_up_executor` (#2059)

## Patch
### crates/full-node/sov-sequencer/src/preferred/cache_warm_up_executor.rs
```diff
@@ -3,6 +3,7 @@ use crate::preferred::block_executor::StartBlockData;
 use crate::preferred::PreferredSequencerConfig;
 use crate::preferred::RollupBlockExecutor;
 use crate::preferred::RollupBlockExecutorConfig;
+use crate::preferred::SequenceNumber;
 use crate::RollupHeight;
 use crate::SequencerConfig;
 use sov_metrics::Metric;
@@ -24,6 +25,9 @@ use tokio::task::JoinHandle;
 // Even if it does, the sender uses a non-blocking method, meaning a few updates may simply be skipped.
 const TX_CHANNEL_SIZE: usize = 16;
 
+// Maximum number of transactions ignored by an executor because they are too new or too old.
+const MAX_NB_OF_IGNORED_TXS: u64 = 16;
+
 /// A transaction with a way to retrieve the corresponding state changes it may produce.
 pub struct FullyBakedTxWithMaybeChangeSet {
     /// The original transaction.
@@ -46,6 +50,7 @@ pub(crate) struct StartBlockNotification<S: Spec> {
     pub(crate) data: StartBlockData<S>,
     pub(crate) checkpoint: StateCheckpoint<S>,
     pub(crate) state_roots: BTreeMap<RollupHeight, <S::Storage as Storage>::Root>,
+    pub(crate) sequence_number: SequenceNumber,
 }
 
 impl<S: Spec> Clone for StartBlockNotification<S> {
@@ -56,13 +61,15 @@ impl<S: Spec> Clone for StartBlockNotification<S> {
             checkpoint: self
                 .checkpoint
                 .clone_with_empty_witness_dropping_temp_cache(),
+            sequence_number: self.sequence_number,
         }
     }
 }
 
 struct FullyBakedTxWithTxChangeSetSender {
     tx: FullyBakedTx,
     sender: oneshot::Sender<TxChangeSet>,
+    sequence_number: SequenceNumber,
 }
 
 #[derive(Clone)]
@@ -92,7 +99,11 @@ impl<S: Spec> CacheWarmUpExecutor<S> {
         let _ = inner.start_block_notification_sender.send(Some(data));
     }
 
-    pub(crate) fn send_tx(&self, tx: FullyBakedTx) -> FullyBakedTxWithMaybeChangeSet {
+    pub(crate) fn send_tx(
+        &self,
+        tx: FullyBakedTx,
+        sequence_number: u64,
+    ) -> FullyBakedTxWithMaybeChangeSet {
         let Some(inner) = &self.inner else {
             return FullyBakedTxWithMaybeChangeSet { tx, receiver: None };
         };
@@ -105,6 +116,7 @@ impl<S: Spec> CacheWarmUpExecutor<S> {
         let res = inner.tx_sender.try_send(FullyBakedTxWithTxChangeSetSender {
             tx: tx.clone(),
             sender,
+            sequence_number,
         });
 
         let maybe_receiver = match res {
@@ -199,16 +211,14 @@ impl<S: Spec> CacheWarmUpExecutor<S> {
                 Default::default(),
             );
 
-            let mut is_started = false;
+            let mut maybe_executor_sequence_number = None;
+            let mut nb_of_ignored_txs = 0;
             loop {
                 tokio::select! {
                     _ = start_block_notification_receiver.changed() => {
-
                         let notify = start_block_notification_receiver.borrow().clone();
                         if let Some(notify) = notify {
-                              let _ = executor.shutdown().await;
-                              Self::start_block(notify, &mut executor).await;
-                              is_started = true;
+                              maybe_executor_sequence_number = Some(Self::start_block(notify, &mut executor).await);
                         }
                     }
 
@@ -225,7 +235,23 @@ impl<S: Spec> CacheWarmUpExecutor<S> {
                             },
                         };
 
-                        if is_started {
+                        if let Some(executor_sequence_number) = maybe_executor_sequence_number {
+                            if tx_with_sender.sequence_number != executor_sequence_number {
+                                // Due to timing issues, the received transaction may have either older or newer sequence number than the executor.
+                                // In this case, we simply continue the loop until the executor and the transactions received from the `accept_tx` task are synchronized.
+                                // If this occurs too frequently, we escalate the log level from warning to error.
+                                if nb_of_ignored_txs > MAX_NB_OF_IGNORED_TXS {
+                                    tracing::error!(%tx_with_sender.sequence_number, %executor_sequence_number, %nb_of_ignored_txs, "Cache warm up task: Transaction could not be applied on the executor.");
+                                }else{
+                                    tracing::warn!(%tx_with_sender.sequence_number, %executor_sequence_number, %nb_of_ignored_txs, "Cache warm up task: Transaction could not be applied on the executor.");
+                                }
+
+                                nb_of_ignored_txs += 1;
+                                continue;
+                            }
+
+                            nb_of_ignored_txs = 0;
+
                             let baked_tx = FullyBakedTxWithMaybeChangeSet::new(tx_with_sender.tx);
                             let res = executor.apply_tx_to_in_progress_batch(baked_tx).await;
 
@@ -255,14 +281,19 @@ impl<S: Spec> CacheWarmUpExecutor<S> {
     async fn start_block<Rt: Runtime<S>>(
         notify: StartBlockNotification<S>,
         executor: &mut RollupBlockExecutor<S, Rt>,
-    ) {
+    ) -> SequenceNumber {
+        let _ = executor.shutdown().await;
+        let seq_nr_from_start_block = notify.sequence_number;
+
         executor
             .start_rollup_block_with_provided_state_roots(
                 notify.data,
                 notify.checkpoint,
                 notify.state_roots,
             )
             .await;
+
+        seq_nr_from_start_block
     }
 }
 
```

### crates/full-node/sov-sequencer/src/preferred/sync_sequencer_state/inner.rs
```diff
@@ -520,8 +520,20 @@ where
             .current_visible_slot_number()
             .advance(visible_increase.get().into());
 
-        self.do_batch_start(visible_slot_number_after_increase, visible_increase)
-            .await
+        let maybe_seq_nr = self
+            .do_batch_start(visible_slot_number_after_increase, visible_increase)
+            .await?;
+
+        if let Some(sequence_number) = maybe_seq_nr {
+            tracing::debug!(
+                %visible_increase,
+                %visible_slot_number_after_increase,
+                %sequence_number,
+                "Sequencer created a new batch"
+            );
+        }
+
+        Ok(())
     }
 
     pub(crate) fn new_executor_with_empty_uncommitted_changes(
@@ -569,9 +581,9 @@ where
         &mut self,
         visible_slot_number_after_increase: VisibleSlotNumber,
         visible_increase: NonZero<u8>,
-    ) -> Result<(), BatchCreationError> {
+    ) -> Result<Option<SequenceNumber>, BatchCreationError> {
         if self.executor.has_in_progress_batch() {
-            return Ok(());
+            return Ok(None);
         }
 
         if let Some(height_to_stop_at) = self.stop_at_rollup_height {
@@ -624,6 +636,7 @@ where
             state_roots,
             data: start_block_data,
             checkpoint: old_checkpoint,
+            sequence_number,
         };
 
         self.cache_warm_up_executor
@@ -640,7 +653,7 @@ where
             )
             .await;
 
-        Ok(())
+        Ok(Some(sequence_number))
     }
 
     pub(crate) async fn do_new_tx(
@@ -683,7 +696,7 @@ where
             });
         }
 
-        let baked_tx = cache_warm_up_executor.send_tx(baked_tx.clone());
+        let baked_tx = cache_warm_up_executor.send_tx(baked_tx.clone(), sequence_number);
         let apply_tx_res = executor.apply_tx_to_in_progress_batch(baked_tx).await;
 
         let (
```
