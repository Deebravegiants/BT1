# [?] Fix recovery panic caused by stale StateRootTask cache entries (#2655)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-03-31
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/c74172dae726411ce8c81a3a659cdaad787cef67
Type: security-commit

## Details
Fix recovery panic caused by stale StateRootTask cache entries (#2655)

## Patch
### crates/full-node/sov-sequencer/src/preferred/block_executor.rs
```diff
@@ -285,6 +285,7 @@ impl<S: Spec, Rt: Runtime<S>> RollupBlockExecutor<S, Rt> {
         self.next_event_number = other.next_event_number;
         self.next_tx_number = other.next_tx_number;
         self.uncommitted_changes = other.uncommitted_changes;
+        self.id = other.id;
 
         // Update our list of state roots from the other executor.
         self.state_roots = other.state_roots;
@@ -814,6 +815,7 @@ impl<S: Spec, Rt: Runtime<S>> RollupBlockExecutor<S, Rt> {
         if self
             .state_root_request_sender
             .send(StateRootComputeRequest {
+                executor_id: self.id,
                 raw_state_changes: changes.clone(),
                 uncommitted_changes: self.uncommitted_changes.clone(),
                 storage: self.checkpoint.storage().clone(),
```

### crates/full-node/sov-sequencer/src/preferred/state_root_compute.rs
```diff
@@ -12,6 +12,7 @@ use sov_state::{NativeStorage, ProvableNamespace, SlotKey, SlotValue, StateAcces
 use tokio::sync::{mpsc, oneshot};
 use tokio::task::JoinHandle;
 use tracing::{debug, error, info, span, trace, Level};
+use uuid::Uuid;
 
 /// The memory limit for old write sets that we keep around. These old sets are useful because they tell us what keys have been changed.
 /// Which lets us output a much handier error message when the state root computation changes.
@@ -20,7 +21,10 @@ const MAX_STATE_ROOTS_TO_CACHE: usize = 100;
 const NUM_STATE_ROOT_COMPUTE_REQUESTS: usize = 50;
 
 type Hasher<S> = <<S as Spec>::CryptoSpec as CryptoSpec>::Hasher;
+type StateRootCacheKey = (RollupHeight, Uuid);
+
 pub(crate) struct StateRootComputeRequest<S: Spec> {
+    pub executor_id: Uuid,
     pub raw_state_changes: Arc<RawStateChanges>,
     pub uncommitted_changes: SequencerStateChanges<Hasher<S>>,
     pub storage: S::Storage,
@@ -206,7 +210,8 @@ impl<S: Spec> StateRootTask<S> {
         info!("Starting sequencer state root computation background task");
         let (request_sender, mut request_receiver) = mpsc::channel(NUM_STATE_ROOT_COMPUTE_REQUESTS);
 
-        let mut cached_results: BTreeMap<RollupHeight, StateRootCacheEntry<S>> = BTreeMap::new();
+        let mut cached_results: BTreeMap<StateRootCacheKey, StateRootCacheEntry<S>> =
+            BTreeMap::new();
         let mut cached_results_size = 0;
         let handle = tokio::spawn(async move {
             loop {
@@ -232,19 +237,20 @@ impl<S: Spec> StateRootTask<S> {
                 };
                 // Wait for a new request, or shutdown.
                 let StateRootComputeRequest::<S> {
+                    executor_id,
                     raw_state_changes,
                     mut uncommitted_changes,
                     storage,
                     rollup_height,
                     max_slot_number,
                     response_channel,
-                    ..
                 } = request;
                 uncommitted_changes.push_front(raw_state_changes);
                 let state_accesses = uncommitted_changes.to_state_accesses();
+                let cache_key = (rollup_height, executor_id);
                 // If the entry is in cache, check that the state root is consistent and return early
-                if let Some(cached_entry) = cached_results.get(&rollup_height) {
-                    trace!(%rollup_height, "Known state root");
+                if let Some(cached_entry) = cached_results.get(&cache_key) {
+                    trace!(%executor_id, %rollup_height, "Known state root");
                     // If we're checking that the state roots are equal, we have some work to do.
                     let result = if check_state_roots {
                         cached_entry
@@ -302,7 +308,7 @@ impl<S: Spec> StateRootTask<S> {
 
                 // Add the new entry to the cache
                 cached_results.insert(
-                    rollup_height,
+                    cache_key,
                     StateRootCacheEntry {
                         root: root.clone(),
                         writes: writes_to_save,
@@ -323,7 +329,7 @@ impl<S: Spec> StateRootTask<S> {
     }
 
     fn prune_cache(
-        cached_results: &mut BTreeMap<RollupHeight, StateRootCacheEntry<S>>,
+        cached_results: &mut BTreeMap<StateRootCacheKey, StateRootCacheEntry<S>>,
         cached_results_size: &mut usize,
     ) {
         // If the cache is too big, prune the oldest writes sets
@@ -360,6 +366,7 @@ mod tests {
         generate_optimistic_runtime, TestHasher, TestJmtSpec, TestSpec, TestStorageSpec,
     };
     use tokio::task::JoinHandle;
+    use uuid::Uuid;
 
     generate_optimistic_runtime!(TestRuntime <=);
 
@@ -462,6 +469,42 @@ mod tests {
         header: &MockBlockHeader,
         pre_state_root: &<S::Storage as Storage>::Root,
     ) -> Arc<RawStateChanges> {
+        sample_batch_with_height_and_writes::<S, Rt, _>(
+            storage,
+            header,
+            pre_state_root,
+            |changes, height| {
+                changes.user.set(
+                    &SlotKey::from_slice(b"user_key_static"),
+                    SlotValue::from(b"value_user_{height}".to_vec()),
+                );
+                changes.user.set(
+                    &SlotKey::from_slice(format!("user_key_{height}").as_bytes()),
+                    SlotValue::from(b"value_a_{height}".to_vec()),
+                );
+                changes.kernel.set(
+                    &SlotKey::from_slice(format!("kernel_key_{height}").as_bytes()),
+                    SlotValue::from(b"value_2_{height}".to_vec()),
+                );
+                changes.user.set(
+                    &SlotKey::from_slice(b"kernel_key_static"),
+                    SlotValue::from(b"value_kernel_{height}".to_vec()),
+                );
+            },
+        )
+    }
+
+    fn sample_batch_with_height_and_writes<S, Rt, F>(
+        storage: &S::Storage,
+        header: &MockBlockHeader,
+        pre_state_root: &<S::Storage as Storage>::Root,
+        add_writes: F,
+    ) -> Arc<RawStateChanges>
+    where
+        S: Spec<Da = MockDaSpec>,
+        Rt: Runtime<S>,
+        F: FnOnce(&mut RawStateChanges, u64),
+    {
         let mut rt = Rt::default();
         let mut kernel = rt.kernel();
         let mut checkpoint = StateCheckpoint::new(storage.clone(), &kernel, None);
@@ -480,22 +523,7 @@ mod tests {
         );
         checkpoint.commit_revertable_storage_cache();
         let mut changes = checkpoint.to_raw_state_changes();
-        changes.user.set(
-            &SlotKey::from_slice(b"user_key_static"),
-            SlotValue::from(b"value_user_{height}".to_vec()),
-        );
-        changes.user.set(
-            &SlotKey::from_slice(format!("user_key_{height}").as_bytes()),
-            SlotValue::from(b"value_a_{height}".to_vec()),
-        );
-        changes.kernel.set(
-            &SlotKey::from_slice(format!("kernel_key_{height}").as_bytes()),
-            SlotValue::from(b"value_2_{height}".to_vec()),
-        );
-        changes.user.set(
-            &SlotKey::from_slice(b"kernel_key_static"),
-            SlotValue::from(b"value_kernel_{height}".to_vec()),
-        );
+        add_writes(&mut changes, height);
         changes.user.commit_revertable_storage_cache();
         changes.kernel.commit_revertable_storage_cache();
 
@@ -518,10 +546,32 @@ mod tests {
         uncommitted_changes: SequencerStateChanges<Hasher<S>>,
         rollup_height: RollupHeight,
         slot_number: SlotNumber,
+    ) -> <S::Storage as Storage>::Root {
+        get_root_from_background_task_with_executor_id(
+            task,
+            Uuid::nil(),
+            storage,
+            raw_state_changes,
+            uncommitted_changes,
+            rollup_height,
+            slot_number,
+        )
+        .await
+    }
+
+    async fn get_root_from_background_task_with_executor_id<S: Spec>(
+        task: &StateRootTask<S>,
+        executor_id: Uuid,
+        storage: S::Storage,
+        raw_state_changes: Arc<RawStateChanges>,
+        uncommitted_changes: SequencerStateChanges<Hasher<S>>,
+        rollup_height: RollupHeight,
+        slot_number: SlotNumber,
     ) -> <S::Storage as Storage>::Root {
         let (response_channel, response_receiver) = oneshot::channel();
         task.request_sender
             .send(StateRootComputeRequest {
+                executor_id,
                 raw_state_changes,
                 uncommitted_changes,
                 storage,
@@ -624,6 +674,65 @@ mod tests {
         assert_eq!(node_new_root, task_new_root);
     }
 
+    #[tokio::test(flavor = "multi_thread")]
+    async fn test_nomt_same_rollup_height_on_different_executor_generations() {
+        let mut storage_manager = SimpleStorageManager::<TestStorageSpec>::new();
+        genesis::<TestSpec, _, TestRuntime<TestSpec>>(&mut storage_manager);
+
+        let storage = storage_manager.create_prover_storage();
+        let prev_root = storage.get_root_hash(storage.latest_version()).unwrap();
+        let first_changes = sample_batch::<TestSpec, TestRuntime<TestSpec>>(&storage, &prev_root);
+        let second_changes =
+            sample_batch_with_height_and_writes::<TestSpec, TestRuntime<TestSpec>, _>(
+                &storage,
+                &MockBlockHeader::from_height(1),
+                &prev_root,
+                |changes, height| {
+                    changes.user.set(
+                        &SlotKey::from_slice(b"user_key_static"),
+                        SlotValue::from(b"value_user_generation_2".to_vec()),
+                    );
+                    changes.user.set(
+                        &SlotKey::from_slice(format!("user_key_{height}").as_bytes()),
+                        SlotValue::from(b"value_b_1".to_vec()),
+                    );
+                },
+            );
+
+        let (task, handle, shutdown_sender) =
+            start_background_task::<TestSpec, TestRuntime<TestSpec>>();
+
+        let first_root = get_root_from_background_task_with_executor_id::<TestSpec>(
+            &task,
+            Uuid::from_u128(1),
+            storage.clone(),
+            first_changes,
+            SequencerStateChanges::default(),
+            RollupHeight::new(1),
+            SlotNumber::new(1),
+        )
+        .await;
+
+        let second_root = get_root_from_background_task_with_executor_id::<TestSpec>(
+            &task,
+            Uuid::from_u128(2),
+            storage,
+            second_changes,
+            SequencerStateChanges::default(),
+            RollupHeight::new(1),
+            SlotNumber::new(1),
+        )
+        .await;
+
+        shutdown_sender.try_send(()).unwrap();
+        handle.await.unwrap();
+
+        assert_ne!(
+            first_root.namespace_root(ProvableNamespace::User),
+            second_root.namespace_root(ProvableNamespace::User)
+        );
+    }
+
     #[tokio::test(flavor = "multi_thread")]
     async fn test_nomt_known_rollup_height_state_root_on_stale_storage_with_deep_jumps() {
         let path = tempfile::tempdir().unwrap();
```
