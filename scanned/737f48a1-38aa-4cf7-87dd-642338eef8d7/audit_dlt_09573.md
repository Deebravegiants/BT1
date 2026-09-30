# [?] Fix panic in full state tests.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-06-20
Source: https://github.com/Conflux-Chain/conflux-rust/commit/aff50c2bf3358c20858a46b02687ce9e38343d0d
Type: security-commit

## Details
Fix panic in full state tests.

## Patch
### client/src/common/mod.rs
```diff
@@ -369,6 +369,7 @@ pub fn initialize_common_modules(
         conf.raw_conf.chain_id,
         &initial_nodes,
     );
+    storage_manager.notify_genesis_hash(genesis_block.hash());
     let mut genesis_accounts = genesis_accounts;
     let genesis_accounts = genesis_accounts
         .drain()
```

### core/storage/src/impls/state_manager.rs
```diff
@@ -632,6 +632,12 @@ impl StateManager {
             }
         }
     }
+
+    pub fn notify_genesis_hash(&self, genesis_hash: EpochId) {
+        if let Some(single_mpt_manager) = &self.single_mpt_storage_manager {
+            *single_mpt_manager.genesis_hash.lock() = genesis_hash;
+        }
+    }
 }
 
 impl StateManagerTrait for StateManager {
@@ -709,7 +715,7 @@ impl StateManagerTrait for StateManager {
     fn get_state_for_next_epoch(
         self: &Arc<Self>, parent_epoch_id: StateIndex,
     ) -> Result<Option<Box<dyn StateTrait>>> {
-        let parent_epoch = parent_epoch_id.epoch_id;
+        let mut parent_epoch = parent_epoch_id.epoch_id;
         let parent_height = parent_epoch_id.maybe_height;
         let state = self.get_state_for_next_epoch_inner(parent_epoch_id)?;
         if state.is_none() {
@@ -731,13 +737,11 @@ impl StateManagerTrait for StateManager {
             } else if single_mpt_storage_manager.available_height
                 == parent_height
             {
-                // FIXME: This makes the state modified in genesis
-                // initialization unavailable.
-                return Ok(Some(Box::new(ReplicatedState::new(
-                    state.unwrap(),
-                    single_mpt_storage_manager.get_state_for_genesis()?,
-                    single_mpt_storage_manager.get_state_filter(),
-                ))));
+                // For the first available single_mpt state, we read the genesis
+                // block state as the parent state to continue execution.
+                // This is only needed for tests because there is no eSpace
+                // state entries for Conflux Mainnet.
+                parent_epoch = *single_mpt_storage_manager.genesis_hash.lock();
             }
         }
         let single_mpt_state =
```

### core/storage/src/impls/storage_manager/single_mpt_storage_manager.rs
```diff
@@ -26,6 +26,8 @@ pub struct SingleMptStorageManager {
     // If it's None, we will keep data for both spaces.
     pub space: Option<Space>,
     pub available_height: u64,
+
+    pub genesis_hash: Mutex<EpochId>,
 }
 
 impl SingleMptStorageManager {
@@ -59,6 +61,8 @@ impl SingleMptStorageManager {
             mpt,
             space,
             available_height,
+            // This is only used after `notify_genesis_hash` called.
+            genesis_hash: Default::default(),
         })
     }
 
```
