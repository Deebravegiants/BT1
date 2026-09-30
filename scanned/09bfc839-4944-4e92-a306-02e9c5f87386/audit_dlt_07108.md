# [?] Race condition fix + Reliability improvements around forks pruning (#1132)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2020-05-16
Source: https://github.com/sigp/lighthouse/commit/59ead67f76489c0df467f380ed5f6f01ed853db2
Type: security-commit

## Details
Race condition fix + Reliability improvements around forks pruning (#1132)

* Improve error handling in block iteration

* Introduce atomic DB operations

* Fix race condition

An invariant was violated:  For every block hash in head_tracker, that
block is accessible from the store.

## Patch
### beacon_node/beacon_chain/src/beacon_chain.rs
```diff
@@ -1482,7 +1482,6 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
 
         metrics::stop_timer(fork_choice_register_timer);
 
-        self.head_tracker.register_block(block_root, &block);
         metrics::observe(
             &metrics::OPERATIONS_PER_BLOCK_ATTESTATION,
             block.body.attestations.len() as f64,
@@ -1503,6 +1502,9 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         self.store.put_state(&block.state_root, &state)?;
         self.store.put_block(&block_root, signed_block.clone())?;
 
+        let parent_root = block.parent_root;
+        let slot = block.slot;
+
         self.snapshot_cache
             .try_write_for(BLOCK_PROCESSING_CACHE_LOCK_TIMEOUT)
             .map(|mut snapshot_cache| {
@@ -1522,6 +1524,9 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
                 );
             });
 
+        self.head_tracker
+            .register_block(block_root, parent_root, slot);
+
         metrics::stop_timer(db_write_timer);
 
         metrics::inc_counter(&metrics::BLOCK_PROCESSING_SUCCESSES);
@@ -2007,9 +2012,8 @@ impl<T: BeaconChainTypes> BeaconChain<T> {
         };
 
         for (head_hash, _head_slot) in heads {
-            for (block_hash, signed_beacon_block) in
-                ParentRootBlockIterator::new(&*self.store, head_hash)
-            {
+            for maybe_pair in ParentRootBlockIterator::new(&*self.store, head_hash) {
+                let (block_hash, signed_beacon_block) = maybe_pair.unwrap();
                 if visited.contains(&block_hash) {
                     break;
                 }
```

### beacon_node/beacon_chain/src/head_tracker.rs
```diff
@@ -2,7 +2,7 @@ use parking_lot::RwLock;
 use ssz_derive::{Decode, Encode};
 use std::collections::HashMap;
 use std::iter::FromIterator;
-use types::{BeaconBlock, EthSpec, Hash256, Slot};
+use types::{Hash256, Slot};
 
 #[derive(Debug, PartialEq)]
 pub enum Error {
@@ -23,10 +23,10 @@ impl HeadTracker {
     /// This function assumes that no block is imported without its parent having already been
     /// imported. It cannot detect an error if this is not the case, it is the responsibility of
     /// the upstream user.
-    pub fn register_block<E: EthSpec>(&self, block_root: Hash256, block: &BeaconBlock<E>) {
+    pub fn register_block(&self, block_root: Hash256, parent_root: Hash256, slot: Slot) {
         let mut map = self.0.write();
-        map.remove(&block.parent_root);
-        map.insert(block_root, block.slot);
+        map.remove(&parent_root);
+        map.insert(block_root, slot);
     }
 
     /// Removes abandoned head.
@@ -107,7 +107,7 @@ pub struct SszHeadTracker {
 mod test {
     use super::*;
     use ssz::{Decode, Encode};
-    use types::MainnetEthSpec;
+    use types::{BeaconBlock, EthSpec, MainnetEthSpec};
 
     type E = MainnetEthSpec;
 
@@ -118,7 +118,7 @@ mod test {
         let head_tracker = HeadTracker::default();
 
         for i in 0..16 {
-            let mut block = BeaconBlock::empty(spec);
+            let mut block: BeaconBlock<E> = BeaconBlock::empty(spec);
             let block_root = Hash256::from_low_u64_be(i);
 
             block.slot = Slot::new(i);
@@ -128,7 +128,7 @@ mod test {
                 Hash256::from_low_u64_be(i - 1)
             };
 
-            head_tracker.register_block::<E>(block_root, &block);
+            head_tracker.register_block(block_root, block.parent_root, block.slot);
         }
 
         assert_eq!(
@@ -137,11 +137,11 @@ mod test {
             "should only have one head"
         );
 
-        let mut block = BeaconBlock::empty(spec);
+        let mut block: BeaconBlock<E> = BeaconBlock::empty(spec);
         let block_root = Hash256::from_low_u64_be(42);
         block.slot = Slot::new(15);
         block.parent_root = Hash256::from_low_u64_be(14);
-        head_tracker.register_block::<E>(block_root, &block);
+        head_tracker.register_block(block_root, block.parent_root, block.slot);
 
         let heads = head_tracker.heads();
 
```

### beacon_node/beacon_chain/src/migrate.rs
```diff
@@ -3,13 +3,12 @@ use crate::head_tracker::HeadTracker;
 use parking_lot::Mutex;
 use slog::{debug, warn, Logger};
 use std::collections::{HashMap, HashSet};
-use std::iter::FromIterator;
 use std::mem;
 use std::sync::mpsc;
 use std::sync::Arc;
 use std::thread;
 use store::iter::{ParentRootBlockIterator, RootsIterator};
-use store::{hot_cold_store::HotColdDBError, Error, SimpleDiskStore, Store};
+use store::{hot_cold_store::HotColdDBError, Error, SimpleDiskStore, Store, StoreOp};
 pub use store::{DiskStore, MemoryStore};
 use types::*;
 use types::{BeaconState, EthSpec, Hash256, Slot};
@@ -49,18 +48,21 @@ pub trait Migrate<S: Store<E>, E: EthSpec>: Send + Sync + 'static {
 
         // Collect hashes from new_finalized_block back to old_finalized_block (inclusive)
         let mut found_block = false; // hack for `take_until`
-        let newly_finalized_blocks: HashMap<SignedBeaconBlockHash, Slot> = HashMap::from_iter(
+        let newly_finalized_blocks: HashMap<SignedBeaconBlockHash, Slot> =
             ParentRootBlockIterator::new(&*store, new_finalized_block_hash.into())
-                .take_while(|(block_hash, _)| {
-                    if found_block {
-                        false
-                    } else {
-                        found_block |= *block_hash == old_finalized_block_hash.into();
-                        true
+                .take_while(|result| match result {
+                    Ok((block_hash, _)) => {
+                        if found_block {
+                            false
+                        } else {
+                            found_block |= *block_hash == old_finalized_block_hash.into();
+                            true
+                        }
                     }
+                    Err(_) => true,
                 })
-                .map(|(block_hash, block)| (block_hash.into(), block.slot())),
-        );
+                .map(|result| result.map(|(block_hash, block)| (block_hash.into(), block.slot())))
+                .collect::<Result<_, _>>()?;
 
         // We don't know which blocks are shared among abandoned chains, so we buffer and delete
         // everything in one fell swoop.
@@ -141,14 +143,16 @@ pub trait Migrate<S: Store<E>, E: EthSpec>: Send + Sync + 'static {
             }
         }
 
-        // XXX Should be performed atomically, see
-        // https://github.com/sigp/lighthouse/issues/692
-        for block_hash in abandoned_blocks.into_iter() {
-            store.delete_block(&block_hash.into())?;
-        }
-        for (slot, state_hash) in abandoned_states.into_iter() {
-            store.delete_state(&state_hash.into(), slot)?;
-        }
+        let batch: Vec<StoreOp> = abandoned_blocks
+            .into_iter()
+            .map(|block_hash| StoreOp::DeleteBlock(block_hash))
+            .chain(
+                abandoned_states
+                    .into_iter()
+                    .map(|(slot, state_hash)| StoreOp::DeleteState(state_hash, slot)),
+            )
+            .collect();
+        store.do_atomically(&batch)?;
         for head_hash in abandoned_heads.into_iter() {
             head_tracker.remove_head(head_hash);
         }
```

### beacon_node/store/src/errors.rs
```diff
@@ -1,7 +1,7 @@
 use crate::chunked_vector::ChunkError;
 use crate::hot_cold_store::HotColdDBError;
 use ssz::DecodeError;
-use types::BeaconStateError;
+use types::{BeaconStateError, Hash256};
 
 #[derive(Debug, PartialEq)]
 pub enum Error {
@@ -12,6 +12,7 @@ pub enum Error {
     HotColdDBError(HotColdDBError),
     DBError { message: String },
     RlpError(String),
+    BlockNotFound(Hash256),
 }
 
 impl From<DecodeError> for Error {
```

### beacon_node/store/src/hot_cold_store.rs
```diff
@@ -8,6 +8,7 @@ use crate::iter::{ParentRootBlockIterator, StateRootsIterator};
 use crate::metrics;
 use crate::{
     leveldb_store::LevelDB, DBColumn, Error, PartialBeaconState, SimpleStoreItem, Store, StoreItem,
+    StoreOp,
 };
 use lru::LruCache;
 use parking_lot::{Mutex, RwLock};
@@ -203,6 +204,21 @@ impl<E: EthSpec> Store<E> for HotColdDB<E> {
         Ok(())
     }
 
+    fn do_atomically(&self, batch: &[StoreOp]) -> Result<(), Error> {
+        let mut guard = self.block_cache.lock();
+        self.hot_db.do_atomically(batch)?;
+        for op in batch {
+            match op {
+                StoreOp::DeleteBlock(block_hash) => {
+                    let untyped_hash: Hash256 = (*block_hash).into();
+                    guard.pop(&untyped_hash);
+                }
+                StoreOp::DeleteState(_, _) => (),
+            }
+        }
+        Ok(())
+    }
+
     /// Advance the split point of the store, moving new finalized states to the freezer.
     fn process_finalization(
         store: Arc<Self>,
@@ -562,15 +578,24 @@ impl<E: EthSpec> HotColdDB<E> {
         end_slot: Slot,
         end_block_hash: Hash256,
     ) -> Result<Vec<SignedBeaconBlock<E>>, Error> {
-        let mut blocks = ParentRootBlockIterator::new(self, end_block_hash)
-            .map(|(_, block)| block)
-            // Include the block at the end slot (if any), it needs to be
-            // replayed in order to construct the canonical state at `end_slot`.
-            .filter(|block| block.message.slot <= end_slot)
-            // Include the block at the start slot (if any). Whilst it doesn't need to be applied
-            // to the state, it contains a potentially useful state root.
-            .take_while(|block| block.message.slot >= start_slot)
-            .collect::<Vec<_>>();
+        let mut blocks: Vec<SignedBeaconBlock<E>> =
+            ParentRootBlockIterator::new(self, end_block_hash)
+                .map(|result| result.map(|(_, block)| block))
+                // Include the block at the end slot (if any), it needs to be
+                // replayed in order to construct the canonical state at `end_slot`.
+                .filter(|result| {
+                    result
+                        .as_ref()
+                        .map_or(true, |block| block.message.slot <= end_slot)
+                })
+                // Include the block at the start slot (if any). Whilst it doesn't need to be applied
+                // to the state, it contains a potentially useful state root.
+                .take_while(|result| {
+                    result
+                        .as_ref()
+                        .map_or(true, |block| block.message.slot >= start_slot)
+                })
+                .collect::<Result<_, _>>()?;
         blocks.reverse();
         Ok(blocks)
     }
```

### beacon_node/store/src/iter.rs
```diff
@@ -217,25 +217,32 @@ impl<'a, E: EthSpec, S: Store<E>> ParentRootBlockIterator<'a, E, S> {
             _phantom: PhantomData,
         }
     }
-}
-
-impl<'a, E: EthSpec, S: Store<E>> Iterator for ParentRootBlockIterator<'a, E, S> {
-    type Item = (Hash256, SignedBeaconBlock<E>);
 
-    fn next(&mut self) -> Option<Self::Item> {
+    fn do_next(&mut self) -> Result<Option<(Hash256, SignedBeaconBlock<E>)>, Error> {
         // Stop once we reach the zero parent, otherwise we'll keep returning the genesis
         // block forever.
         if self.next_block_root.is_zero() {
-            None
+            Ok(None)
         } else {
             let block_root = self.next_block_root;
-            let block = self.store.get_block(&block_root).ok()??;
+            let block = self
+                .store
+                .get_block(&block_root)?
+                .ok_or(Error::BlockNotFound(block_root))?;
             self.next_block_root = block.message.parent_root;
-            Some((block_root, block))
+            Ok(Some((block_root, block)))
         }
     }
 }
 
+impl<'a, E: EthSpec, S: Store<E>> Iterator for ParentRootBlockIterator<'a, E, S> {
+    type Item = Result<(Hash256, SignedBeaconBlock<E>), Error>;
+
+    fn next(&mut self) -> Option<Self::Item> {
+        self.do_next().transpose()
+    }
+}
+
 #[derive(Clone)]
 /// Extends `BlockRootsIterator`, returning `SignedBeaconBlock` instances, instead of their roots.
 pub struct BlockIterator<'a, T: EthSpec, U> {
```

### beacon_node/store/src/leveldb_store.rs
```diff
@@ -3,6 +3,7 @@ use crate::forwards_iter::SimpleForwardsBlockRootsIterator;
 use crate::impls::beacon_state::{get_full_state, store_full_state};
 use crate::metrics;
 use db_key::Key;
+use leveldb::database::batch::{Batch, Writebatch};
 use leveldb::database::kv::KV;
 use leveldb::database::Database;
 use leveldb::error::Error as LevelDBError;
@@ -145,6 +146,41 @@ impl<E: EthSpec> Store<E> for LevelDB<E> {
     ) -> Self::ForwardsBlockRootsIterator {
         SimpleForwardsBlockRootsIterator::new(store, start_slot, end_state, end_block_root)
     }
+
+    fn do_atomically(&self, ops_batch: &[StoreOp]) -> Result<(), Error> {
+        let mut leveldb_batch = Writebatch::new();
+        for op in ops_batch {
+            match op {
+                StoreOp::DeleteBlock(block_hash) => {
+                    let untyped_hash: Hash256 = (*block_hash).into();
+                    let key = Self::get_key_for_col(
+                        DBColumn::BeaconBlock.into(),
+                        untyped_hash.as_bytes(),
+                    );
+                    leveldb_batch.delete(key);
+                }
+
+                StoreOp::DeleteState(state_hash, slot) => {
+                    let untyped_hash: Hash256 = (*state_hash).into();
+                    let state_summary_key = Self::get_key_for_col(
+                        DBColumn::BeaconStateSummary.into(),
+                        untyped_hash.as_bytes(),
+                    );
+                    leveldb_batch.delete(state_summary_key);
+
+                    if *slot % E::slots_per_epoch() == 0 {
+                        let state_key = Self::get_key_for_col(
+                            DBColumn::BeaconState.into(),
+                            untyped_hash.as_bytes(),
+                        );
+                        leveldb_batch.delete(state_key);
+                    }
+                }
+            }
+        }
+        self.db.write(self.write_options(), &leveldb_batch)?;
+        Ok(())
+    }
 }
 
 impl From<LevelDBError> for Error {
```

### beacon_node/store/src/lib.rs
```diff
@@ -90,12 +90,15 @@ pub trait Store<E: EthSpec>: Sync + Send + Sized + 'static {
 
     /// Delete a block from the store.
     fn delete_block(&self, block_root: &Hash256) -> Result<(), Error> {
-        self.delete::<SignedBeaconBlock<E>>(block_root)
+        self.key_delete(DBColumn::BeaconBlock.into(), block_root.as_bytes())
     }
 
     /// Store a state in the store.
     fn put_state(&self, state_root: &Hash256, state: &BeaconState<E>) -> Result<(), Error>;
 
+    /// Execute either all of the operations in `batch` or none at all, returning an error.
+    fn do_atomically(&self, batch: &[StoreOp]) -> Result<(), Error>;
+
     /// Store a state summary in the store.
     // NOTE: this is a hack for the HotColdDb, we could consider splitting this
     // trait and removing the generic `S: Store` types everywhere?
@@ -180,6 +183,13 @@ pub trait Store<E: EthSpec>: Sync + Send + Sized + 'static {
     }
 }
 
+/// Reified key-value storage operation.  Helps in modifying the storage atomically.
+/// See also https://github.com/sigp/lighthouse/issues/692
+pub enum StoreOp {
+    DeleteBlock(SignedBeaconBlockHash),
+    DeleteState(BeaconStateHash, Slot),
+}
+
 /// A unique column identifier.
 #[derive(Debug, Clone, Copy, PartialEq)]
 pub enum DBColumn {
```

### beacon_node/store/src/memory_store.rs
```diff
@@ -1,4 +1,4 @@
-use super::{Error, Store};
+use super::{DBColumn, Error, Store, StoreOp};
 use crate::forwards_iter::SimpleForwardsBlockRootsIterator;
 use crate::impls::beacon_state::{get_full_state, store_full_state};
 use parking_lot::RwLock;
@@ -89,6 +89,30 @@ impl<E: EthSpec> Store<E> for MemoryStore<E> {
         get_full_state(self, state_root)
     }
 
+    fn do_atomically(&self, batch: &[StoreOp]) -> Result<(), Error> {
+        for op in batch {
+            match op {
+                StoreOp::DeleteBlock(block_hash) => {
+                    let untyped_hash: Hash256 = (*block_hash).into();
+                    self.key_delete(DBColumn::BeaconBlock.into(), untyped_hash.as_bytes())?;
+                }
+
+                StoreOp::DeleteState(state_hash, slot) => {
+                    let untyped_hash: Hash256 = (*state_hash).into();
+                    if *slot % E::slots_per_epoch() == 0 {
+                        self.key_delete(DBColumn::BeaconState.into(), untyped_hash.as_bytes())?;
+                    } else {
+                        self.key_delete(
+                            DBColumn::BeaconStateSummary.into(),
+                            untyped_hash.as_bytes(),
+                        )?;
+                    }
+                }
+            }
+        }
+        Ok(())
+    }
+
     fn forwards_block_roots_iterator(
         store: Arc<Self>,
         start_slot: Slot,
```
