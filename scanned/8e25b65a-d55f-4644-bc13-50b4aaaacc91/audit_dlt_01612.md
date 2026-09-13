# [?] Fix potential underflow on `PrunerWatermark.wait_for` (#22171)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-22
Source: https://github.com/MystenLabs/sui/commit/3406f7c92cc0316a61b0502bf84c99fa8cf23285
Type: security-commit

## Details
Fix potential underflow on `PrunerWatermark.wait_for` (#22171)

## Description 

Previously:
wait_for was an i64 field on PrunerWatermark (since PrunerWatermark
represented the "stored" datatype)
The fn wait_for on PrunerWatermark checked self.wait_for > 0 then
Duration::from_millis, which works since self.wait_for is still an i64,
and thus can represent negative values

https://github.com/MystenLabs/sui/pull/21537/files#diff-e91aff7d4e8968395eb4a363dc2f6b5affae2cd76042e5ec1029661c80c1522b

Currently:
fn pruner_watermark of the Connection trait has the same query
"CAST({BigInt} + 1000 * EXTRACT(EPOCH FROM pruner_timestamp - NOW()) AS
BIGINT)", but now we immediately set it as a field on PrunerWatermark -
as u64, so that causes the underflow, turning potentially negative
numbers into a massive positive one
Later, the check self.wait_for_ms > 0 will return true, and pruner waits
an impossible amount of time

`2025-05-19T21:07:58.187014Z DEBUG
sui_indexer_alt_framework::pipeline::concurrent::pruner: Waiting to
prune pipeline="obj_info" wait_for=18446744073452109.806s`

```
postgres=> select pipeline, pruner_hi, pruner_timestamp, reader_lo, cast(120000 + 1000 * extract(epoch from pruner_timestamp - now()) as bigint)  from watermarks where pipeline = 'obj_info';
 pipeline | pruner_hi |      pruner_timestamp      | reader_lo |    int8     
----------+-----------+----------------------------+-----------+-------------
 obj_info |  70000000 | 2025-04-21 17:58:41.447523 | 132449987 | -2430754117
```

The pruner_timestamp is in the past, so we end up in this scenario.

The fix is to switch wait_for on PrunerWatermark to be i64 instead. Also
add tests for this case.

## Test plan 

New test coverage

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

### crates/sui-indexer-alt-framework-store-traits/src/lib.rs
```diff
@@ -24,6 +24,18 @@ pub trait Connection: Send + Sync {
         pipeline: &'static str,
     ) -> anyhow::Result<Option<ReaderWatermark>>;
 
+    /// Get the bounds for the region that the pruner is allowed to prune, and the time in
+    /// milliseconds the pruner must wait before it can begin pruning data for the given `pipeline`.
+    /// The pruner is allowed to prune the region between the returned `pruner_hi` (inclusive) and
+    /// `reader_lo` (exclusive) after waiting until `pruner_timestamp + delay` has passed. This
+    /// minimizes the possibility for the pruner to delete data still expected by inflight read
+    /// requests.
+    async fn pruner_watermark(
+        &mut self,
+        pipeline: &'static str,
+        delay: Duration,
+    ) -> anyhow::Result<Option<PrunerWatermark>>;
+
     /// Upsert the high watermark as long as it raises the watermark stored in the database. Returns
     /// a boolean indicating whether the watermark was actually updated or not.
     async fn set_committer_watermark(
@@ -51,18 +63,6 @@ pub trait Connection: Send + Sync {
         reader_lo: u64,
     ) -> anyhow::Result<bool>;
 
-    /// Get the bounds for the region that the pruner is allowed to prune, and the time in
-    /// milliseconds the pruner must wait before it can begin pruning data for the given `pipeline`.
-    /// The pruner is allowed to prune the region between the returned `pruner_hi` (inclusive) and
-    /// `reader_lo` (exclusive) after waiting until `pruner_timestamp + delay` has passed. This
-    /// minimizes the possibility for the pruner to delete data still expected by inflight read
-    /// requests.
-    async fn pruner_watermark(
-        &mut self,
-        pipeline: &'static str,
-        delay: Duration,
-    ) -> anyhow::Result<Option<PrunerWatermark>>;
-
     /// Update the pruner watermark, returns true if the watermark was actually updated
     async fn set_pruner_watermark(
         &mut self,
@@ -123,8 +123,14 @@ pub struct ReaderWatermark {
 #[derive(Default, Debug, Clone, Copy)]
 pub struct PrunerWatermark {
     /// The remaining time in milliseconds that the pruner must wait before it can begin pruning.
-    /// This is calculated as the time remaining until `pruner_timestamp + delay` has passed.
-    pub wait_for_ms: u64,
+    ///
+    /// This is calculated by finding the difference between the time when it becomes safe to prune
+    /// and the current time: `(pruner_timestamp + delay) - current_time`.
+    ///
+    /// The pruner will wait for this duration before beginning to delete data if it is positive.
+    /// When this value is zero or negative, it means the waiting period has already passed and
+    /// pruning can begin immediately.
+    pub wait_for_ms: i64,
 
     /// The pruner can delete up to this checkpoint (exclusive).
     pub reader_lo: u64,
@@ -152,8 +158,9 @@ impl CommitterWatermark {
 }
 
 impl PrunerWatermark {
-    pub fn wait_for_ms(&self) -> Option<Duration> {
-        (self.wait_for_ms > 0).then(|| Duration::from_millis(self.wait_for_ms))
+    /// Returns the duration that the pruner must wait before it can begin pruning data.
+    pub fn wait_for(&self) -> Option<Duration> {
+        (self.wait_for_ms > 0).then(|| Duration::from_millis(self.wait_for_ms as u64))
     }
 
     /// The next chunk of checkpoints that the pruner should work on, to advance the watermark. If
@@ -171,3 +178,78 @@ impl PrunerWatermark {
         Some((from, to_exclusive))
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use std::time::Duration;
+
+    #[test]
+    fn test_pruner_watermark_wait_for_positive() {
+        let watermark = PrunerWatermark {
+            wait_for_ms: 5000, // 5 seconds
+            reader_lo: 1000,
+            pruner_hi: 500,
+        };
+
+        assert_eq!(watermark.wait_for(), Some(Duration::from_millis(5000)));
+    }
+
+    #[test]
+    fn test_pruner_watermark_wait_for_zero() {
+        let watermark = PrunerWatermark {
+            wait_for_ms: 0,
+            reader_lo: 1000,
+            pruner_hi: 500,
+        };
+
+        assert_eq!(watermark.wait_for(), None);
+    }
+
+    #[test]
+    fn test_pruner_watermark_wait_for_negative() {
+        let watermark = PrunerWatermark {
+            wait_for_ms: -5000,
+            reader_lo: 1000,
+            pruner_hi: 500,
+        };
+
+        assert_eq!(watermark.wait_for(), None);
+    }
+
+    #[test]
+    fn test_pruner_watermark_no_more_chunks() {
+        let mut watermark = PrunerWatermark {
+            wait_for_ms: 0,
+            reader_lo: 1000,
+            pruner_hi: 1000,
+        };
+
+        assert_eq!(watermark.next_chunk(100), None);
+    }
+
+    #[test]
+    fn test_pruner_watermark_chunk_boundaries() {
+        let mut watermark = PrunerWatermark {
+            wait_for_ms: 0,
+            reader_lo: 1000,
+            pruner_hi: 100,
+        };
+
+        assert_eq!(watermark.next_chunk(100), Some((100, 200)));
+        assert_eq!(watermark.pruner_hi, 200);
+        assert_eq!(watermark.next_chunk(100), Some((200, 300)));
+
+        // Reset and test oversized chunk
+        let mut watermark = PrunerWatermark {
+            wait_for_ms: 0,
+            reader_lo: 1000,
+            pruner_hi: 500,
+        };
+
+        // Chunk larger than remaining range
+        assert_eq!(watermark.next_chunk(2000), Some((500, 1000)));
+        assert_eq!(watermark.pruner_hi, 1000);
+        assert_eq!(watermark.next_chunk(2000), None);
+    }
+}
```

### crates/sui-indexer-alt-framework/src/pipeline/concurrent/pruner.rs
```diff
@@ -168,7 +168,7 @@ pub(super) fn pruner<H: Handler + Send + Sync + 'static>(
             };
 
             // (2) Wait until this information can be acted upon.
-            if let Some(wait_for) = watermark.wait_for_ms() {
+            if let Some(wait_for) = watermark.wait_for() {
                 debug!(pipeline = H::NAME, ?wait_for, "Waiting to prune");
                 tokio::select! {
                     _ = tokio::time::sleep(wait_for) => {}
@@ -341,3 +341,366 @@ async fn prune_task_impl<H: Handler + Send + Sync + 'static>(
 
     Ok(())
 }
+
+#[cfg(test)]
+mod tests {
+    use std::collections::HashMap;
+    use std::sync::{Arc, Mutex};
+    use std::time::{Duration, SystemTime, UNIX_EPOCH};
+
+    use async_trait::async_trait;
+    use prometheus::Registry;
+    use sui_indexer_alt_framework_store_traits::{
+        CommitterWatermark, PrunerWatermark, ReaderWatermark, Store,
+    };
+    use sui_types::full_checkpoint_content::CheckpointData;
+
+    use crate::{pipeline::Processor, store::Connection, FieldCount};
+
+    use super::*;
+
+    #[derive(Clone, Default)]
+    pub struct MockWatermark {
+        epoch_hi_inclusive: u64,
+        checkpoint_hi_inclusive: u64,
+        tx_hi: u64,
+        timestamp_ms_hi_inclusive: u64,
+        reader_lo: u64,
+        pruner_timestamp: u64,
+        pruner_hi: u64,
+    }
+
+    #[derive(Clone)]
+    pub struct MockStore {
+        pub watermarks: Arc<Mutex<MockWatermark>>,
+        /// Map of checkpoint sequence number to list of transaction sequence numbers.
+        pub data: Arc<Mutex<HashMap<u64, Vec<u64>>>>,
+    }
+
+    #[derive(Clone)]
+    pub struct MockConnection<'c>(pub &'c MockStore);
+
+    #[async_trait]
+    impl Connection for MockConnection<'_> {
+        async fn committer_watermark(
+            &mut self,
+            _pipeline: &'static str,
+        ) -> Result<Option<CommitterWatermark>, anyhow::Error> {
+            let watermarks = self.0.watermarks.lock().unwrap();
+            Ok(Some(CommitterWatermark {
+                epoch_hi_inclusive: watermarks.epoch_hi_inclusive,
+                checkpoint_hi_inclusive: watermarks.checkpoint_hi_inclusive,
+                tx_hi: watermarks.tx_hi,
+                timestamp_ms_hi_inclusive: watermarks.timestamp_ms_hi_inclusive,
+            }))
+        }
+
+        async fn reader_watermark(
+            &mut self,
+            _pipeline: &'static str,
+        ) -> Result<Option<ReaderWatermark>, anyhow::Error> {
+            let watermarks = self.0.watermarks.lock().unwrap();
+            Ok(Some(ReaderWatermark {
+                checkpoint_hi_inclusive: watermarks.checkpoint_hi_inclusive,
+                reader_lo: watermarks.reader_lo,
+            }))
+        }
+
+        async fn pruner_watermark(
+            &mut self,
+            _pipeline: &'static str,
+            delay: Duration,
+        ) -> Result<Option<PrunerWatermark>, anyhow::Error> {
+            let watermarks = self.0.watermarks.lock().unwrap();
+            let elapsed_ms = watermarks.pruner_timestamp as i64
+                - SystemTime::now()
+                    .duration_since(UNIX_EPOCH)
+                    .unwrap()
+                    .as_millis() as i64;
+            let wait_for_ms = delay.as_millis() as i64 + elapsed_ms;
+            Ok(Some(PrunerWatermark {
+                pruner_hi: watermarks.pruner_hi,
+                reader_lo: watermarks.reader_lo,
+                wait_for_ms,
+            }))
+        }
+
+        async fn set_committer_watermark(
+            &mut self,
+            _pipeline: &'static str,
+            watermark: CommitterWatermark,
+        ) -> anyhow::Result<bool> {
+            let mut watermarks = self.0.watermarks.lock().unwrap();
+            watermarks.epoch_hi_inclusive = watermark.epoch_hi_inclusive;
+            watermarks.checkpoint_hi_inclusive = watermark.checkpoint_hi_inclusive;
+            watermarks.tx_hi = watermark.tx_hi;
+            watermarks.timestamp_ms_hi_inclusive = watermark.timestamp_ms_hi_inclusive;
+            Ok(true)
+        }
+
+        async fn set_reader_watermark(
+            &mut self,
+            _pipeline: &'static str,
+            reader_lo: u64,
+        ) -> anyhow::Result<bool> {
+            let mut watermarks = self.0.watermarks.lock().unwrap();
+            watermarks.reader_lo = reader_lo;
+            watermarks.pruner_timestamp = SystemTime::now()
+                .duration_since(UNIX_EPOCH)
+                .unwrap()
+                .as_millis() as u64;
+            Ok(true)
+        }
+
+        async fn set_pruner_watermark(
+            &mut self,
+            _pipeline: &'static str,
+            pruner_hi: u64,
+        ) -> anyhow::Result<bool> {
+            let mut watermarks = self.0.watermarks.lock().unwrap();
+            watermarks.pruner_hi = pruner_hi;
+            Ok(true)
+        }
+    }
+
+    #[async_trait]
+    impl Store for MockStore {
+        type Connection<'c> = MockConnection<'c>;
+
+        async fn connect<'c>(&'c self) -> Result<Self::Connection<'c>, anyhow::Error> {
+            Ok(MockConnection(self))
+        }
+    }
+
+    #[derive(FieldCount)]
+    pub struct StoredData {
+        pub cp_sequence_number: u64,
+        pub tx_sequence_numbers: Vec<u64>,
+    }
+
+    pub struct DataPipeline;
+
+    impl Processor for DataPipeline {
+        const NAME: &'static str = "data";
+
+        type Value = StoredData;
+
+        fn process(&self, checkpoint: &Arc<CheckpointData>) -> anyhow::Result<Vec<Self::Value>> {
+            let start_tx = checkpoint.checkpoint_summary.network_total_transactions as usize
+                - checkpoint.transactions.len();
+            let tx_sequence_numbers = checkpoint
+                .transactions
+                .iter()
+                .enumerate()
+                .map(|(i, _)| (start_tx + i) as u64)
+                .collect();
+            let value = StoredData {
+                cp_sequence_number: checkpoint.checkpoint_summary.sequence_number,
+                tx_sequence_numbers,
+            };
+
+            Ok(vec![value])
+        }
+    }
+
+    #[async_trait]
+    impl Handler for DataPipeline {
+        type Store = MockStore;
+
+        async fn commit<'a>(
+            values: &[Self::Value],
+            conn: &mut MockConnection<'a>,
+        ) -> anyhow::Result<usize> {
+            let mut data = conn.0.data.lock().unwrap();
+            for value in values {
+                data.insert(value.cp_sequence_number, value.tx_sequence_numbers.clone());
+            }
+            Ok(values.len())
+        }
+
+        async fn prune<'a>(
+            &self,
+            from: u64,
+            to_exclusive: u64,
+            conn: &mut MockConnection<'a>,
+        ) -> anyhow::Result<usize> {
+            let mut data = conn.0.data.lock().unwrap();
+            for cp_sequence_number in from..to_exclusive {
+                data.remove(&cp_sequence_number);
+            }
+            Ok((to_exclusive - from) as usize)
+        }
+    }
+
+    #[tokio::test]
+    async fn test_pruner() {
+        let handler = Arc::new(DataPipeline);
+        let pruner_config = PrunerConfig {
+            interval_ms: 10,
+            delay_ms: 2000,
+            retention: 1,
+            max_chunk_size: 100,
+            prune_concurrency: 1,
+        };
+        let registry = Registry::new_custom(Some("test".to_string()), None).unwrap();
+        let metrics = IndexerMetrics::new(&registry);
+        let cancel = CancellationToken::new();
+
+        // Update data
+        let test_data = HashMap::from([(1, vec![1, 2, 3]), (2, vec![4, 5, 6]), (3, vec![7, 8, 9])]);
+        // Update committer watermark
+        let timestamp = SystemTime::now()
+            .duration_since(UNIX_EPOCH)
+            .unwrap()
+            .as_millis() as u64;
+
+        let watermark = MockWatermark {
+            epoch_hi_inclusive: 0,
+            checkpoint_hi_inclusive: 3,
+            tx_hi: 9,
+            timestamp_ms_hi_inclusive: timestamp,
+            reader_lo: 3,
+            pruner_timestamp: timestamp,
+            pruner_hi: 0,
+        };
+        let store = MockStore {
+            watermarks: Arc::new(Mutex::new(watermark)),
+            data: Arc::new(Mutex::new(test_data.clone())),
+        };
+
+        // Start the pruner
+        let store_clone = store.clone();
+        let cancel_clone = cancel.clone();
+        let pruner_handle = tokio::spawn(async move {
+            pruner(
+                handler,
+                Some(pruner_config),
+                store_clone,
+                metrics,
+                cancel_clone,
+            )
+            .await
+        });
+
+        // Wait a short time within delay_ms
+        tokio::time::sleep(Duration::from_millis(200)).await;
+        {
+            let data = store.data.lock().unwrap();
+            assert!(
+                data.contains_key(&1),
+                "Checkpoint 1 shouldn't be pruned before delay"
+            );
+            assert!(
+                data.contains_key(&2),
+                "Checkpoint 2 shouldn't be pruned before delay"
+            );
+            assert!(
+                data.contains_key(&3),
+                "Checkpoint 3 shouldn't be pruned before delay"
+            );
+        }
+
+        // Wait for the delay to expire
+        tokio::time::sleep(Duration::from_millis(2000)).await;
+
+        // Now checkpoint 1 should be pruned
+        {
+            let data = store.data.lock().unwrap();
+            assert!(
+                !data.contains_key(&1),
+                "Checkpoint 1 should be pruned after delay"
+            );
+
+            // Checkpoint 3 should never be pruned (it's the reader_lo)
+            assert!(data.contains_key(&3), "Checkpoint 3 should be preserved");
+
+            // Check that the pruner_hi was updated past 1
+            let watermark = store.watermarks.lock().unwrap();
+            assert!(
+                watermark.pruner_hi > 1,
+                "Pruner watermark should be updated"
+            );
+        }
+
+        // Clean up
+        cancel.cancel();
+        let _ = tokio::time::timeout(Duration::from_millis(1000), pruner_handle).await;
+    }
+
+    #[tokio::test]
+    async fn test_pruner_timestamp_in_the_past() {
+        let handler = Arc::new(DataPipeline);
+        let pruner_config = PrunerConfig {
+            interval_ms: 10,
+            delay_ms: 20_000,
+            retention: 1,
+            max_chunk_size: 100,
+            prune_concurrency: 1,
+        };
+        let registry = Registry::new_custom(Some("test".to_string()), None).unwrap();
+        let metrics = IndexerMetrics::new(&registry);
+        let cancel = CancellationToken::new();
+
+        // Update data
+        let test_data = HashMap::from([(1, vec![1, 2, 3]), (2, vec![4, 5, 6]), (3, vec![7, 8, 9])]);
+        // Update committer watermark
+        let timestamp = SystemTime::now()
+            .duration_since(UNIX_EPOCH)
+            .unwrap()
+            .as_millis() as u64;
+
+        let watermark = MockWatermark {
+            epoch_hi_inclusive: 0,
+            checkpoint_hi_inclusive: 3,
+            tx_hi: 9,
+            timestamp_ms_hi_inclusive: timestamp,
+            reader_lo: 3,
+            pruner_timestamp: 0,
+            pruner_hi: 0,
+        };
+        let store = MockStore {
+            watermarks: Arc::new(Mutex::new(watermark)),
+            data: Arc::new(Mutex::new(test_data.clone())),
+        };
+
+        // Start the pruner
+        let store_clone = store.clone();
+        let cancel_clone = cancel.clone();
+        let pruner_handle = tokio::spawn(async move {
+            pruner(
+                handler,
+                Some(pruner_config),
+                store_clone,
+                metrics,
+                cancel_clone,
+            )
+            .await
+        });
+
+        // Because the `pruner_timestamp` is in the past, even with the delay_ms it should be pruned
+        // close to immediately. To be safe, sleep for 1000ms before checking, which is well under
+        // the delay_ms of 20_000 ms.
+        tokio::time::sleep(Duration::from_millis(500)).await;
+
+        {
+            let data = store.data.lock().unwrap();
+            assert!(!data.contains_key(&1), "Checkpoint 1 should be pruned");
+
+            assert!(!data.contains_key(&2), "Checkpoint 2 should be pruned");
+
+            // Checkpoint 3 should never be pruned (it's the reader_lo)
+            assert!(data.contains_key(&3), "Checkpoint 3 should be preserved");
+
+            // Check that the pruner_hi was updated past 1
+            let watermark = store.watermarks.lock().unwrap();
+            assert!(
+                watermark.pruner_hi > 1,
+                "Pruner watermark should be updated"
+            );
+        }
+
+        // Clean up
+        cancel.cancel();
+        let _ = tokio::time::timeout(Duration::from_millis(1000), pruner_handle).await;
+    }
+}
```

### crates/sui-pg-db/src/store.rs
```diff
@@ -95,7 +95,7 @@ impl store::Connection for Connection<'_> {
 
         if let Some(watermark) = watermark {
             Ok(Some(store::PrunerWatermark {
-                wait_for_ms: watermark.0 as u64,
+                wait_for_ms: watermark.0,
                 pruner_hi: watermark.1 as u64,
                 reader_lo: watermark.2 as u64,
             }))
```
