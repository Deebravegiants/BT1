# [?] fix(exex): prevent ExExManager deadlock when buffer clears after being full (#21135)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-01-16
Source: https://github.com/paradigmxyz/reth/commit/a1646541459fb9b39e352a0e176369f592a29e50
Type: security-commit

## Details
fix(exex): prevent ExExManager deadlock when buffer clears after being full (#21135)

## Patch
### crates/exex/exex/src/manager.rs
```diff
@@ -503,6 +503,7 @@ where
             }
             break
         }
+        let buffer_full = this.buffer.len() >= this.max_capacity;
 
         // Update capacity
         this.update_capacity();
@@ -536,6 +537,12 @@ where
         // Update capacity
         this.update_capacity();
 
+        // If the buffer was full and we made space, we need to wake up to accept new notifications
+        if buffer_full && this.buffer.len() < this.max_capacity {
+            debug!(target: "exex::manager", "Buffer has space again, waking up senders");
+            cx.waker().wake_by_ref();
+        }
+
         // Update watch channel block number
         let finished_height = this.exex_handles.iter_mut().try_fold(u64::MAX, |curr, exex| {
             exex.finished_height.map_or(Err(()), |height| Ok(height.number.min(curr)))
@@ -1443,4 +1450,83 @@ mod tests {
 
         Ok(())
     }
+
+    #[tokio::test]
+    async fn test_deadlock_manager_wakes_after_buffer_clears() {
+        // This test simulates the scenario where the buffer fills up, ingestion pauses,
+        // and then space clears. We verify the manager wakes up to process pending items.
+
+        let temp_dir = tempfile::tempdir().unwrap();
+        let wal = Wal::new(temp_dir.path()).unwrap();
+        let provider_factory = create_test_provider_factory();
+        init_genesis(&provider_factory).unwrap();
+        let provider = BlockchainProvider::new(provider_factory.clone()).unwrap();
+
+        // 1. Setup Manager with Capacity = 1
+        let (exex_handle, _, mut notifications) = ExExHandle::new(
+            "test_exex".to_string(),
+            Default::default(),
+            provider,
+            EthEvmConfig::mainnet(),
+            wal.handle(),
+        );
+
+        let max_capacity = 2;
+        let exex_manager = ExExManager::new(
+            provider_factory,
+            vec![exex_handle],
+            max_capacity,
+            wal,
+            empty_finalized_header_stream(),
+        );
+
+        let manager_handle = exex_manager.handle();
+
+        // Spawn manager in background so it runs continuously
+        tokio::spawn(async move {
+            exex_manager.await.ok();
+        });
+
+        // Helper to create notifications
+        let mut rng = generators::rng();
+        let mut make_notif = |id: u64| {
+            let block = random_block(&mut rng, id, BlockParams::default()).try_recover().unwrap();
+            ExExNotification::ChainCommitted {
+                new: Arc::new(Chain::new(
+                    vec![block],
+                    Default::default(),
+                    Default::default(),
+                    Default::default(),
+                )),
+            }
+        };
+
+        manager_handle.send(ExExNotificationSource::Pipeline, make_notif(1)).unwrap();
+
+        // Send the "Stuck" Item (Notification #100).
+        // At this point, the Manager loop has skipped the ingestion logic because buffer is full
+        // (buffer_full=true). This item sits in the unbounded 'handle_rx' channel waiting.
+        manager_handle.send(ExExNotificationSource::Pipeline, make_notif(100)).unwrap();
+
+        // 3. Relieve Pressure
+        // We consume items from the ExEx.
+        // As we pull items out, the ExEx frees space -> Manager sends buffered item -> Manager
+        // frees space. Once Manager frees space, the FIX (wake_by_ref) should trigger,
+        // causing it to read Notif #100.
+
+        // Consume the jam
+        let _ = notifications.next().await.unwrap();
+
+        // 4. Assert No Deadlock
+        // We expect Notification #100 next.
+        // If the wake_by_ref fix is missing, this will Time Out because the manager is sleeping
+        // despite having empty buffer.
+        let result =
+            tokio::time::timeout(std::time::Duration::from_secs(1), notifications.next()).await;
+
+        assert!(
+            result.is_ok(),
+            "Deadlock detected! Manager failed to wake up and process Pending Item #100."
+        );
+    }
 }
```
