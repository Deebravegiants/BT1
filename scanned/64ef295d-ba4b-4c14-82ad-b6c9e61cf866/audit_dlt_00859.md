# [?] fix(en): Fix race condition in EN storage initialization (#3515)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2025-01-23
Source: https://github.com/matter-labs/zksync-era/commit/c916797d49d636c9e642264786d4124ebd338ec3
Type: security-commit

## Details
fix(en): Fix race condition in EN storage initialization (#3515)

## What ❔

Reworks `NodeStorageInitializer::is_chain_tip_correct()` so that it
performs the minimum amount of work possible, i.e. detects whether the
latest L1 batch / L2 block diverge or not.

## Why ❔

EN storage initialization is prone to a data race: the "is storage
initialized" check calls
`NodeStorageInitializer::is_chain_tip_correct()`, which internally
performs the entire iteration of the reorg detector (in particular,
binary search for the first diverged block). This can lead to a data
race with block revert logic, which may be executed concurrently. This
data race was observed on the revert integration tests.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

## Patch
### core/node/node_storage_init/src/external_node/revert.rs
```diff
@@ -34,6 +34,12 @@ impl RevertStorage for ExternalNodeReverter {
         Ok(())
     }
 
+    async fn is_reorg_needed(&self, stop_receiver: watch::Receiver<bool>) -> anyhow::Result<bool> {
+        ReorgDetector::new(self.client.clone(), self.pool.clone())
+            .check_reorg_presence(stop_receiver)
+            .await
+    }
+
     async fn last_correct_batch_for_reorg(
         &self,
         stop_receiver: watch::Receiver<bool>,
```

### core/node/node_storage_init/src/lib.rs
```diff
@@ -182,10 +182,7 @@ impl NodeStorageInitializer {
     ) -> anyhow::Result<bool> {
         // May be `true` if stop signal is received, but the node will shut down without launching any tasks anyway.
         let initialized = if let Some(reverter) = &self.strategy.block_reverter {
-            reverter
-                .last_correct_batch_for_reorg(stop_receiver)
-                .await?
-                .is_none()
+            !reverter.is_reorg_needed(stop_receiver).await?
         } else {
             true
         };
```

### core/node/node_storage_init/src/traits.rs
```diff
@@ -18,6 +18,9 @@ pub trait InitializeStorage: fmt::Debug + Send + Sync + 'static {
 /// This trait assumes that for any invalid state there exists a batch number to which the storage can be rolled back.
 #[async_trait::async_trait]
 pub trait RevertStorage: fmt::Debug + Send + Sync + 'static {
+    /// Checks whether a reorg is needed for the storage.
+    async fn is_reorg_needed(&self, stop_receiver: watch::Receiver<bool>) -> anyhow::Result<bool>;
+
     /// Checks if the storage is invalid state and has to be rolled back.
     async fn last_correct_batch_for_reorg(
         &self,
```

### core/node/reorg_detector/src/lib.rs
```diff
@@ -266,26 +266,32 @@ impl ReorgDetector {
         &self.health_check
     }
 
-    async fn check_consistency(&mut self) -> Result<(), Error> {
+    async fn find_last_diverged_batch(&mut self) -> Result<Option<L1BatchNumber>, HashMatchError> {
         let mut storage = self.pool.connection().await?;
-        let Some(local_l1_batch) = storage
+        // Create a readonly transaction to get a consistent view of the storage.
+        let mut storage_tx = storage
+            .transaction_builder()?
+            .set_readonly()
+            .build()
+            .await?;
+        let Some(local_l1_batch) = storage_tx
             .blocks_dal()
             .get_last_l1_batch_number_with_tree_data()
             .await?
         else {
-            return Ok(());
+            return Ok(None);
         };
-        let Some(local_l2_block) = storage.blocks_dal().get_sealed_l2_block_number().await? else {
-            return Ok(());
+        let Some(local_l2_block) = storage_tx.blocks_dal().get_sealed_l2_block_number().await?
+        else {
+            return Ok(None);
         };
+        drop(storage_tx);
         drop(storage);
 
         let remote_l1_batch = self.client.sealed_l1_batch_number().await?;
         let remote_l2_block = self.client.sealed_l2_block_number().await?;
-
         let checked_l1_batch = local_l1_batch.min(remote_l1_batch);
         let checked_l2_block = local_l2_block.min(remote_l2_block);
-
         let root_hashes_match = self.root_hashes_match(checked_l1_batch).await?;
         let l2_block_hashes_match = self.l2_block_hashes_match(checked_l2_block).await?;
 
@@ -295,13 +301,21 @@ impl ReorgDetector {
         // In other cases either there is only a height mismatch which means that one of
         // the nodes needs to do catching up; however, it is not certain that there is actually
         // a re-org taking place.
-        if root_hashes_match && l2_block_hashes_match {
+        Ok(if root_hashes_match && l2_block_hashes_match {
             self.event_handler
                 .update_correct_block(checked_l2_block, checked_l1_batch);
+            None
+        } else {
+            let diverged_l1_batch = checked_l1_batch + (root_hashes_match as u32);
+            self.event_handler.report_divergence(diverged_l1_batch);
+            Some(diverged_l1_batch)
+        })
+    }
+
+    async fn check_consistency(&mut self) -> Result<(), Error> {
+        let Some(diverged_l1_batch) = self.find_last_diverged_batch().await? else {
             return Ok(());
-        }
-        let diverged_l1_batch = checked_l1_batch + (root_hashes_match as u32);
-        self.event_handler.report_divergence(diverged_l1_batch);
+        };
 
         // Check that the first L1 batch matches, to make sure that
         // we are actually tracking the same chain as the main node.
@@ -455,15 +469,7 @@ impl ReorgDetector {
     ) -> Result<(), Error> {
         while !*stop_receiver.borrow_and_update() {
             let sleep_interval = match self.check_consistency().await {
-                Err(Error::HashMatch(HashMatchError::MissingData(MissingData::RootHash))) => {
-                    tracing::debug!("Last L1 batch on the main node doesn't have a state root hash; waiting until it is computed");
-                    self.sleep_interval / 10
-                }
-                Err(err) if err.is_retriable() => {
-                    tracing::warn!("Following transient error occurred: {err}");
-                    tracing::info!("Trying again after a delay");
-                    self.sleep_interval
-                }
+                Err(Error::HashMatch(err)) => self.handle_hash_err(err)?,
                 Err(err) => return Err(err),
                 Ok(()) if stop_after_success => return Ok(()),
                 Ok(()) => self.sleep_interval,
@@ -480,6 +486,46 @@ impl ReorgDetector {
         }
         Ok(())
     }
+
+    /// Returns the sleep interval if the error is transient.
+    fn handle_hash_err(&self, err: HashMatchError) -> Result<Duration, HashMatchError> {
+        match err {
+            HashMatchError::MissingData(MissingData::RootHash) => {
+                tracing::debug!("Last L1 batch on the main node doesn't have a state root hash; waiting until it is computed");
+                Ok(self.sleep_interval / 10)
+            }
+            err if err.is_retriable() => {
+                tracing::warn!("Following transient error occurred: {err}");
+                tracing::info!("Trying again after a delay");
+                Ok(self.sleep_interval)
+            }
+            err => Err(err),
+        }
+    }
+
+    /// Checks whether a reorg is present. Unlike [`Self::run_once()`], this method doesn't pinpoint the first diverged L1 batch;
+    /// it just checks whether diverged batches / blocks exist in general.
+    ///
+    /// Internally retries transient errors. Returns `Ok(false)` if a stop signal is received.
+    pub async fn check_reorg_presence(
+        &mut self,
+        mut stop_receiver: watch::Receiver<bool>,
+    ) -> anyhow::Result<bool> {
+        while !*stop_receiver.borrow_and_update() {
+            let sleep_interval = match self.find_last_diverged_batch().await {
+                Err(err) => self.handle_hash_err(err)?,
+                Ok(maybe_diverged_batch) => return Ok(maybe_diverged_batch.is_some()),
+            };
+
+            if tokio::time::timeout(sleep_interval, stop_receiver.changed())
+                .await
+                .is_ok()
+            {
+                break;
+            }
+        }
+        Ok(false)
+    }
 }
 
 /// Fallible and async predicate for binary search.
```

### core/node/reorg_detector/src/tests.rs
```diff
@@ -312,12 +312,19 @@ async fn reorg_is_detected_on_batch_hash_mismatch() {
     store_l2_block(&mut storage, 2, l2_block_hash).await;
     detector.check_consistency().await.unwrap();
 
+    let (_stop_sender, stop_receiver) = watch::channel(false);
+    assert!(!detector
+        .check_reorg_presence(stop_receiver.clone())
+        .await
+        .unwrap());
+
     seal_l1_batch(&mut storage, 2, H256::repeat_byte(0xff)).await;
     // ^ Hash of L1 batch #2 differs from that on the main node.
     assert_matches!(
         detector.check_consistency().await,
         Err(Error::ReorgDetected(L1BatchNumber(1)))
     );
+    assert!(detector.check_reorg_presence(stop_receiver).await.unwrap());
 }
 
 #[tokio::test]
@@ -621,6 +628,9 @@ async fn reorg_is_detected_based_on_l2_block_hashes(last_correct_l1_batch: u32)
         detector.check_consistency().await,
         Err(Error::ReorgDetected(L1BatchNumber(num))) if num == last_correct_l1_batch
     );
+
+    let (_stop_sender, stop_receiver) = watch::channel(false);
+    assert!(detector.check_reorg_presence(stop_receiver).await.unwrap());
 }
 
 #[derive(Debug)]
```
