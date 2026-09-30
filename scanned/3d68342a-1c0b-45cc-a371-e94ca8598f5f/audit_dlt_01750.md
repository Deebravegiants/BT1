# [?] fix: panic on new if trie_state_resharder in progress (#13719)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-06-19
Source: https://github.com/near/nearcore/commit/f7430bce6353fd8063fcf9598dc734de18aca91f
Type: security-commit

## Details
fix: panic on new if trie_state_resharder in progress (#13719)

The goal of this PR is to prevent the node from starting operations if
the resharding was started but not completed, so it would be obvious to
the node operator that they need to run the resharding resume command.

An alternative could be to check for this in an initialization path more
explicitly like Chain::new for example.
This seems more contained.

## Patch
### chain/chain/src/resharding/resharding_actor.rs
```diff
@@ -5,6 +5,7 @@ use super::event_type::ReshardingSplitShardParams;
 use super::flat_storage_resharder::FlatStorageResharder;
 use super::trie_state_resharder::TrieStateResharder;
 use super::types::ScheduleResharding;
+use crate::resharding::trie_state_resharder::ResumeAllowed;
 use crate::types::RuntimeAdapter;
 use near_async::futures::{DelayedActionRunner, DelayedActionRunnerExt};
 use near_async::messaging::{self, HandlerWithContext};
@@ -66,8 +67,12 @@ impl ReshardingActor {
             resharding_handle.clone(),
             resharding_config.clone(),
         );
-        let trie_state_resharder =
-            TrieStateResharder::new(runtime_adapter, resharding_handle, resharding_config);
+        let trie_state_resharder = TrieStateResharder::new(
+            runtime_adapter,
+            resharding_handle,
+            resharding_config,
+            ResumeAllowed::No,
+        );
         Self {
             chain_store,
             resharding_events: HashMap::new(),
```

### chain/chain/src/resharding/trie_state_resharder.rs
```diff
@@ -78,13 +78,30 @@ pub struct TrieStateResharder {
     resharding_config: MutableConfigValue<ReshardingConfig>,
 }
 
+#[derive(Debug, Clone, Copy, PartialEq, Eq)]
+pub enum ResumeAllowed {
+    Yes,
+    No,
+}
+
 impl TrieStateResharder {
     pub fn new(
         runtime: Arc<dyn RuntimeAdapter>,
         handle: ReshardingHandle,
         resharding_config: MutableConfigValue<ReshardingConfig>,
+        resume_allowed: ResumeAllowed,
     ) -> Self {
-        Self { runtime, handle, resharding_config }
+        let resharder = Self { runtime, handle, resharding_config };
+        if resume_allowed == ResumeAllowed::No {
+            // Load the status to check if resharding is in progress
+            if let Some(status) = resharder.load_status().unwrap() {
+                panic!(
+                    "TrieStateReshardingStatus already exists for shard {}, must run resume_resharding to continue interrupted resharding operation before starting node.",
+                    status.parent_shard_uid
+                )
+            }
+        }
+        resharder
     }
 
     // Processes one batch of a trie state resharding and updates the status,
@@ -431,8 +448,12 @@ mod tests {
         let test = setup_test();
 
         let config = ChainConfig::test().resharding_config;
-        let resharder =
-            TrieStateResharder::new(test.runtime.clone(), ReshardingHandle::new(), config);
+        let resharder = TrieStateResharder::new(
+            test.runtime.clone(),
+            ReshardingHandle::new(),
+            config,
+            ResumeAllowed::No,
+        );
 
         let mut update_status = test.as_status();
         resharder.resharding_blocking_impl(&mut update_status).unwrap();
@@ -448,8 +469,12 @@ mod tests {
         let test = setup_test();
 
         let config = ChainConfig::test().resharding_config;
-        let resharder =
-            TrieStateResharder::new(test.runtime.clone(), ReshardingHandle::new(), config);
+        let resharder = TrieStateResharder::new(
+            test.runtime.clone(),
+            ReshardingHandle::new(),
+            config,
+            ResumeAllowed::No,
+        );
 
         // Set the batch size to 1, this should stop iteration after the first key.
         resharder
@@ -480,8 +505,12 @@ mod tests {
 
         // Test resuming the resharding operation.
         let config = ChainConfig::test().resharding_config;
-        let resharder =
-            TrieStateResharder::new(test.runtime.clone(), ReshardingHandle::new(), config);
+        let resharder = TrieStateResharder::new(
+            test.runtime.clone(),
+            ReshardingHandle::new(),
+            config,
+            ResumeAllowed::Yes,
+        );
         resharder.resume(test.parent_shard).expect("resume should succeed");
 
         // The resharding status should be None after completion.
@@ -491,6 +520,37 @@ mod tests {
         assert_eq!(0, test.runtime.store().iter(DBCol::StateShardUIdMapping).count());
     }
 
+    #[test]
+    #[should_panic(expected = "TrieStateReshardingStatus already exists")]
+    fn test_trie_state_resharder_panic_on_implicit_resume() {
+        let test = setup_test();
+
+        let config = ChainConfig::test().resharding_config;
+        let resharder = TrieStateResharder::new(
+            test.runtime.clone(),
+            ReshardingHandle::new(),
+            config,
+            ResumeAllowed::No,
+        );
+
+        // Set the batch size to 1, this should stop iteration after the first key.
+        resharder
+            .resharding_config
+            .update(ReshardingConfig { batch_size: ByteSize(1), ..ReshardingConfig::test() });
+        let mut update_status = test.as_status();
+        resharder.process_batch_and_update_status(&mut update_status).unwrap();
+
+        // Implicitly resuming the resharding operation should panic,
+        // as the status is not None and we are not allowed to resume.
+        let config = ChainConfig::test().resharding_config;
+        let _resharder = TrieStateResharder::new(
+            test.runtime.clone(),
+            ReshardingHandle::new(),
+            config,
+            ResumeAllowed::No,
+        );
+    }
+
     fn check_child_tries_contain_all_keys(test: &TestSetup) {
         let tries = test.runtime.get_tries();
         // Using view_trie to bypass the memtrie and read from disk.
```

### tools/flat-storage/src/resume_resharding.rs
```diff
@@ -1,6 +1,6 @@
 use crate::commands::ResumeReshardingCmd;
 use near_chain::resharding::flat_storage_resharder::FlatStorageResharder;
-use near_chain::resharding::trie_state_resharder::TrieStateResharder;
+use near_chain::resharding::trie_state_resharder::{ResumeAllowed, TrieStateResharder};
 use near_chain::types::RuntimeAdapter;
 use near_chain_configs::ReshardingHandle;
 use near_epoch_manager::EpochManager;
@@ -46,6 +46,7 @@ pub(crate) fn resume_resharding(
         runtime_adapter,
         ReshardingHandle::new(),
         config.client_config.resharding_config.clone(),
+        ResumeAllowed::Yes,
     );
     trie_state_resharder.resume(shard_uid)?;
 
```
