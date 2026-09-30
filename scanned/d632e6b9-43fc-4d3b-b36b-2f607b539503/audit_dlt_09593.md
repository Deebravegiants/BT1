# [?] Fix storage unit test crash when exiting (#1778)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-08-14
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f574737ef23e3f159a5d5b84badfb33aa77111d2
Type: security-commit

## Details
Fix storage unit test crash when exiting (#1778)

This bug has no impact on production.

Co-authored-by: Zhe Yang <yz@conflux-chain.org>

## Patch
### .gitignore
```diff
@@ -14,4 +14,3 @@ build/
 **/*.log
 **/testnet.toml
 *~
-conflux_unit_test_data_dir
```

### core/examples/snapshot_merge_test.rs
```diff
@@ -295,7 +295,7 @@ fn new_state_manager(
 }
 
 fn initialize_genesis(
-    manager: &StateManager,
+    manager: &Arc<StateManager>,
 ) -> Result<(H256, MerkleHash), Error> {
     let mut state = manager.get_state_for_genesis_write();
 
@@ -321,8 +321,9 @@ fn initialize_genesis(
 }
 
 fn prepare_state(
-    manager: &StateManager, parent: H256, height: &mut u64, accounts: usize,
-    accounts_per_epoch: usize, account_map: &mut HashMap<Address, Account>,
+    manager: &Arc<StateManager>, parent: H256, height: &mut u64,
+    accounts: usize, accounts_per_epoch: usize,
+    account_map: &mut HashMap<Address, Account>,
     old_state_root: &StateRootWithAuxInfo, state_root: &StateRootWithAuxInfo,
 ) -> Result<(H256, MerkleHash), StorageError>
 {
@@ -347,7 +348,7 @@ fn prepare_state(
 }
 
 fn add_accounts(
-    manager: &StateManager, parent: H256, height: &mut u64,
+    manager: &Arc<StateManager>, parent: H256, height: &mut u64,
     accounts_per_epoch: usize, new_account_map: &HashMap<Address, Account>,
     old_state_root: &StateRootWithAuxInfo, state_root: &StateRootWithAuxInfo,
 ) -> Result<(H256, MerkleHash), StorageError>
@@ -407,7 +408,7 @@ fn add_accounts(
 }
 
 fn add_accounts_and_commit<'a, Iter>(
-    manager: &StateManager, accounts: usize, account_map: &mut Iter,
+    manager: &Arc<StateManager>, accounts: usize, account_map: &mut Iter,
     state_index: StateIndex,
 ) -> H256
 where
```

### core/src/executive/context.rs
```diff
@@ -424,10 +424,7 @@ mod tests {
         machine::{new_machine_with_builtin, Machine},
         parameters::consensus::TRANSACTION_DEFAULT_EPOCH_BOUND,
         state::{State, Substate},
-        storage::{
-            new_storage_manager_for_testing, tests::FakeStateManager,
-            StorageManager,
-        },
+        storage::{new_storage_manager_for_testing, tests::FakeStateManager},
         test_helpers::get_state_for_genesis_write,
         vm::{
             CallType, Context as ContextTrait, ContractCreateResult,
@@ -464,9 +461,12 @@ mod tests {
         }
     }
 
+    // storage_manager is apparently unused but it must be held to keep the
+    // database directory.
+    #[allow(unused)]
     struct TestSetup {
-        storage_manager: Option<Box<FakeStateManager>>,
-        state: Option<State>,
+        storage_manager: FakeStateManager,
+        state: State,
         machine: Machine,
         internal_contract_map: InternalContractMap,
         spec: Spec,
@@ -475,36 +475,25 @@ mod tests {
     }
 
     impl TestSetup {
-        fn init_state(&mut self, storage_manager: &'static StorageManager) {
-            self.state = Some(get_state_for_genesis_write(storage_manager));
-        }
-
         fn new() -> Self {
-            let storage_manager = Box::new(new_storage_manager_for_testing());
+            let storage_manager = new_storage_manager_for_testing();
+            let state = get_state_for_genesis_write(&*storage_manager);
             let machine = new_machine_with_builtin(Default::default());
             let env = get_test_env();
             let spec = machine.spec(env.number);
             let internal_contract_map = InternalContractMap::new();
 
             let mut setup = Self {
-                storage_manager: None,
-                state: None,
+                storage_manager,
+                state,
                 machine,
                 internal_contract_map,
                 spec,
                 substate: Substate::new(),
                 env,
             };
-            setup.storage_manager = Some(storage_manager);
-            setup.init_state(unsafe {
-                &*(&**setup.storage_manager.as_ref().unwrap().as_ref()
-                    as *const StorageManager)
-            });
-
             setup
                 .state
-                .as_mut()
-                .unwrap()
                 .init_code(&Address::zero(), vec![], Address::zero())
                 .ok();
 
@@ -515,7 +504,7 @@ mod tests {
     #[test]
     fn can_be_created() {
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         let ctx = Context::new(
@@ -538,7 +527,7 @@ mod tests {
     #[test]
     fn can_return_block_hash_no_env() {
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         let mut ctx = Context::new(
@@ -580,7 +569,7 @@ mod tests {
     //            last_hashes.push(test_hash.clone());
     //            env.last_hashes = Arc::new(last_hashes);
     //        }
-    //        let state = &mut setup.state.unwrap();
+    //        let state = &mut setup.state;
     //        let origin = get_test_origin();
     //
     //        let mut ctx = Context::new(
@@ -610,7 +599,7 @@ mod tests {
     #[should_panic]
     fn can_call_fail_empty() {
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         let mut ctx = Context::new(
@@ -658,7 +647,7 @@ mod tests {
         .unwrap()];
 
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         {
@@ -687,7 +676,7 @@ mod tests {
         refund_account.set_user_account_type_bits();
 
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let mut origin = get_test_origin();
 
         let mut contract_address = Address::zero();
@@ -731,7 +720,7 @@ mod tests {
         use std::str::FromStr;
 
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         let address = {
@@ -777,7 +766,7 @@ mod tests {
         use std::str::FromStr;
 
         let mut setup = TestSetup::new();
-        let state = &mut setup.state.unwrap();
+        let state = &mut setup.state;
         let origin = get_test_origin();
 
         let address = {
```

### core/src/genesis.rs
```diff
@@ -98,8 +98,9 @@ pub fn initialize_internal_contract_accounts(state: &mut State) {
 /// ` test_net_version` is used to update the genesis author so that after
 /// resetting, the chain of the older version will be discarded
 pub fn genesis_block(
-    storage_manager: &StorageManager, genesis_accounts: HashMap<Address, U256>,
-    test_net_version: Address, initial_difficulty: U256,
+    storage_manager: &Arc<StorageManager>,
+    genesis_accounts: HashMap<Address, U256>, test_net_version: Address,
+    initial_difficulty: U256,
 ) -> Block
 {
     let mut state = State::new(
```

### core/src/state/state_tests.rs
```diff
@@ -19,8 +19,11 @@ use crate::{
 use cfx_types::{address_util::AddressUtil, Address, BigEndianHash, U256};
 use keccak_hash::{keccak, KECCAK_EMPTY};
 use primitives::{EpochId, StorageKey, StorageLayout};
+use std::sync::Arc;
 
-fn get_state(storage_manager: &StorageManager, epoch_id: &EpochId) -> State {
+fn get_state(
+    storage_manager: &Arc<StorageManager>, epoch_id: &EpochId,
+) -> State {
     State::new(
         StateDb::new(
             storage_manager
```

### core/src/storage/impls/state_manager.rs
```diff
@@ -540,23 +540,20 @@ impl StateManager {
 
 impl StateManagerTrait for StateManager {
     fn get_state_no_commit(
-        &self, state_index: StateIndex, try_open: bool,
+        self: &Arc<Self>, state_index: StateIndex, try_open: bool,
     ) -> Result<Option<State>> {
         let maybe_state_trees = self.get_state_trees(&state_index, try_open)?;
         match maybe_state_trees {
             None => Ok(None),
-            Some(state_trees) => Ok(Some(State::new(
-                // Safe because StateManager is always an Arc.
-                unsafe { shared_from_this(self) },
-                state_trees,
-            ))),
+            Some(state_trees) => {
+                Ok(Some(State::new(self.clone(), state_trees)))
+            }
         }
     }
 
-    fn get_state_for_genesis_write(&self) -> State {
+    fn get_state_for_genesis_write(self: &Arc<Self>) -> State {
         State::new(
-            // Safe because StateManager is always an Arc.
-            unsafe { shared_from_this(self) },
+            self.clone(),
             StateTrees {
                 snapshot_db: self
                     .storage_manager
@@ -600,19 +597,17 @@ impl StateManagerTrait for StateManager {
     // Due to the complexity of the latter approach, we stay with the
     // simple approach.
     fn get_state_for_next_epoch(
-        &self, parent_epoch_id: StateIndex,
+        self: &Arc<Self>, parent_epoch_id: StateIndex,
     ) -> Result<Option<State>> {
         let maybe_state_trees = self.get_state_trees_for_next_epoch(
             &parent_epoch_id,
             /* try_open = */ false,
         )?;
         match maybe_state_trees {
             None => Ok(None),
-            Some(state_trees) => Ok(Some(State::new(
-                // Safe because StateManager is always an Arc.
-                unsafe { shared_from_this(self) },
-                state_trees,
-            ))),
+            Some(state_trees) => {
+                Ok(Some(State::new(self.clone(), state_trees)))
+            }
         }
     }
 }
@@ -630,7 +625,6 @@ use crate::storage::{
     state::*,
     state_manager::*,
     storage_db::*,
-    utils::arc_ext::shared_from_this,
     StorageConfiguration,
 };
 use malloc_size_of_derive::MallocSizeOf as MallocSizeOfDerive;
```

### core/src/storage/state_manager.rs
```diff
@@ -31,12 +31,12 @@ pub trait StateManagerTrait {
     /// With try_open == true, the call fails immediately when the max number of
     /// snapshot open is reached.
     fn get_state_no_commit(
-        &self, epoch_id: StateIndex, try_open: bool,
+        self: &Arc<Self>, epoch_id: StateIndex, try_open: bool,
     ) -> Result<Option<State>>;
     fn get_state_for_next_epoch(
-        &self, parent_epoch_id: StateIndex,
+        self: &Arc<Self>, parent_epoch_id: StateIndex,
     ) -> Result<Option<State>>;
-    fn get_state_for_genesis_write(&self) -> State;
+    fn get_state_for_genesis_write(self: &Arc<Self>) -> State;
 }
 
 impl StateIndex {
```

### core/src/storage/tests/mod.rs
```diff
@@ -56,7 +56,7 @@ impl KeyValueDB for FakeDbForStateTest {
 #[cfg(test)]
 pub struct FakeStateManager {
     data_dir: String,
-    state_manager: Option<StateManager>,
+    state_manager: Option<Arc<StateManager>>,
 }
 
 #[cfg(test)]
@@ -82,27 +82,30 @@ impl FakeStateManager {
             let unit_test_data_path = Path::new(&unit_test_data_dir);
             Ok(FakeStateManager {
                 data_dir: unit_test_data_dir.clone(),
-                state_manager: Some(StateManager::new(StorageConfiguration {
-                    additional_maintained_snapshot_count: 0,
-                    consensus_param: ConsensusParam {
-                        snapshot_epoch_count,
+                state_manager: Some(Arc::new(StateManager::new(
+                    StorageConfiguration {
+                        additional_maintained_snapshot_count: 0,
+                        consensus_param: ConsensusParam {
+                            snapshot_epoch_count,
+                        },
+                        debug_snapshot_checker_threads: 0,
+                        delta_mpts_cache_recent_lfu_factor: 4.0,
+                        delta_mpts_cache_size: 20_000_000,
+                        delta_mpts_cache_start_size: 1_000_000,
+                        delta_mpts_node_map_vec_size: 20_000_000,
+                        delta_mpts_slab_idle_size: 200_000,
+                        max_open_snapshots:
+                            defaults::DEFAULT_MAX_OPEN_SNAPSHOTS,
+                        path_delta_mpts_dir: unit_test_data_path
+                            .join(&*storage_dir::DELTA_MPTS_DIR),
+                        path_snapshot_dir: unit_test_data_path
+                            .join(&*storage_dir::SNAPSHOT_DIR),
+                        path_snapshot_info_db: unit_test_data_path
+                            .join(&*storage_dir::SNAPSHOT_INFO_DB_PATH),
+                        path_storage_dir: unit_test_data_path
+                            .join(&*storage_dir::STORAGE_DIR),
                     },
-                    debug_snapshot_checker_threads: 0,
-                    delta_mpts_cache_recent_lfu_factor: 4.0,
-                    delta_mpts_cache_size: 20_000_000,
-                    delta_mpts_cache_start_size: 1_000_000,
-                    delta_mpts_node_map_vec_size: 20_000_000,
-                    delta_mpts_slab_idle_size: 200_000,
-                    max_open_snapshots: defaults::DEFAULT_MAX_OPEN_SNAPSHOTS,
-                    path_delta_mpts_dir: unit_test_data_path
-                        .join(&*storage_dir::DELTA_MPTS_DIR),
-                    path_snapshot_dir: unit_test_data_path
-                        .join(&*storage_dir::SNAPSHOT_DIR),
-                    path_snapshot_info_db: unit_test_data_path
-                        .join(&*storage_dir::SNAPSHOT_INFO_DB_PATH),
-                    path_storage_dir: unit_test_data_path
-                        .join(&*storage_dir::STORAGE_DIR),
-                })?),
+                )?)),
             })
         }
     }
@@ -122,7 +125,7 @@ impl Drop for FakeStateManager {
 
 #[cfg(test)]
 impl Deref for FakeStateManager {
-    type Target = StateManager;
+    type Target = Arc<StateManager>;
 
     fn deref(&self) -> &Self::Target { self.state_manager.as_ref().unwrap() }
 }
@@ -298,4 +301,5 @@ use std::{
     fs, mem,
     ops::{Deref, DerefMut},
     path::Path,
+    sync::Arc,
 };
```

### core/src/storage/tests/state.rs
```diff
@@ -591,7 +591,7 @@ fn test_set_order() {
 #[test]
 fn test_set_order_concurrent() {
     let mut rng = get_rng_for_test();
-    let state_manager = Arc::new(new_state_manager_for_unit_test());
+    let state_manager = new_state_manager_for_unit_test();
     let keys = Arc::new(
         generate_keys(TEST_NUMBER_OF_KEYS / 10)
             .iter()
```

### core/src/test_helpers.rs
```diff
@@ -6,16 +6,19 @@ use crate::{
     storage::{StateIndex, StorageManager, StorageManagerTrait},
 };
 use primitives::EpochId;
+use std::sync::Arc;
 
-pub fn get_state_for_genesis_write(storage_manager: &StorageManager) -> State {
+pub fn get_state_for_genesis_write(
+    storage_manager: &Arc<StorageManager>,
+) -> State {
     get_state_for_genesis_write_with_factory(
         storage_manager,
         Factory::default(),
     )
 }
 
 pub fn get_state_for_genesis_write_with_factory(
-    storage_manager: &StorageManager, factory: Factory,
+    storage_manager: &Arc<StorageManager>, factory: Factory,
 ) -> State {
     let mut state = State::new(
         StateDb::new(storage_manager.get_state_for_genesis_write()),
```
