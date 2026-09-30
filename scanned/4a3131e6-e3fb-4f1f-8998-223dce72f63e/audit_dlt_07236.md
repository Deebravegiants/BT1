# [?] Fix rare crash when a transaction executes after its shared object assignments have been deleted. (#19949)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2024-10-22
Source: https://github.com/MystenLabs/sui/commit/3aac32e2e5c97293a20644bd1fbc287dd61d8be0
Type: security-commit

## Details
Fix rare crash when a transaction executes after its shared object assignments have been deleted. (#19949)

Fix rare crash when a transaction executes after its shared object
assignments have been deleted.

This is only possible if a second execution of the same tx starts
concurrently, and the shared version assignments have been deleted as we
are checking for object availability in TransactionManager

## Patch
### crates/sui-core/src/authority.rs
```diff
@@ -11,6 +11,7 @@ use crate::verify_indexes::verify_indexes;
 use anyhow::anyhow;
 use arc_swap::{ArcSwap, Guard};
 use async_trait::async_trait;
+use authority_per_epoch_store::CertLockGuard;
 use chrono::prelude::*;
 use fastcrypto::encoding::Base58;
 use fastcrypto::encoding::Encoding;
@@ -1273,7 +1274,22 @@ impl AuthorityState {
         debug!("execute_certificate_internal");
 
         let tx_digest = certificate.digest();
-        let input_objects = self.read_objects_for_execution(certificate, epoch_store)?;
+
+        // prevent concurrent executions of the same tx.
+        let tx_guard = epoch_store.acquire_tx_guard(certificate).await?;
+
+        // The cert could have been processed by a concurrent attempt of the same cert, so check if
+        // the effects have already been written.
+        if let Some(effects) = self
+            .get_transaction_cache_reader()
+            .get_executed_effects(tx_digest)?
+        {
+            tx_guard.release();
+            return Ok((effects, None));
+        }
+
+        let input_objects =
+            self.read_objects_for_execution(tx_guard.as_lock_guard(), certificate, epoch_store)?;
 
         if expected_effects_digest.is_none() {
             // We could be re-executing a previously executed but uncommitted transaction, perhaps after
@@ -1283,12 +1299,6 @@ impl AuthorityState {
             expected_effects_digest = epoch_store.get_signed_effects_digest(tx_digest)?;
         }
 
-        // This acquires a lock on the tx digest to prevent multiple concurrent executions of the
-        // same tx. While we don't need this for safety (tx sequencing is ultimately atomic), it is
-        // very common to receive the same tx multiple times simultaneously due to gossip, so we
-        // may as well hold the lock and save the cpu time for other requests.
-        let tx_guard = epoch_store.acquire_tx_guard(certificate).await?;
-
         self.process_certificate(
             tx_guard,
             certificate,
@@ -1302,6 +1312,7 @@ impl AuthorityState {
 
     pub fn read_objects_for_execution(
         &self,
+        tx_lock: &CertLockGuard,
         certificate: &VerifiedExecutableTransaction,
         epoch_store: &Arc<AuthorityPerEpochStore>,
     ) -> SuiResult<InputObjects> {
@@ -1314,6 +1325,7 @@ impl AuthorityState {
         self.input_loader.read_objects_for_execution(
             epoch_store.as_ref(),
             &certificate.key(),
+            tx_lock,
             input_objects,
             epoch_store.epoch(),
         )
@@ -1403,15 +1415,6 @@ impl AuthorityState {
             }
         });
 
-        // The cert could have been processed by a concurrent attempt of the same cert, so check if
-        // the effects have already been written.
-        if let Some(effects) = self
-            .get_transaction_cache_reader()
-            .get_executed_effects(&digest)?
-        {
-            tx_guard.release();
-            return Ok((effects, None));
-        }
         let execution_guard = self
             .execution_lock_for_executable_transaction(certificate)
             .await;
@@ -5081,7 +5084,7 @@ impl AuthorityState {
         );
 
         fail_point_async!("change_epoch_tx_delay");
-        let _tx_lock = epoch_store.acquire_tx_lock(tx_digest).await;
+        let tx_lock = epoch_store.acquire_tx_lock(tx_digest).await;
 
         // The tx could have been executed by state sync already - if so simply return an error.
         // The checkpoint builder will shortly be terminated by reconfiguration anyway.
@@ -5109,7 +5112,8 @@ impl AuthorityState {
             )
             .await?;
 
-        let input_objects = self.read_objects_for_execution(&executable_tx, epoch_store)?;
+        let input_objects =
+            self.read_objects_for_execution(&tx_lock, &executable_tx, epoch_store)?;
 
         let (temporary_store, effects, _execution_error_opt) =
             self.prepare_certificate(&execution_guard, &executable_tx, input_objects, epoch_store)?;
```

### crates/sui-core/src/authority/authority_per_epoch_store.rs
```diff
@@ -129,6 +129,16 @@ pub struct CertTxGuard(#[allow(unused)] CertLockGuard);
 impl CertTxGuard {
     pub fn release(self) {}
     pub fn commit_tx(self) {}
+    pub fn as_lock_guard(&self) -> &CertLockGuard {
+        &self.0
+    }
+}
+
+impl CertLockGuard {
+    pub fn dummy_for_tests() -> Self {
+        let lock = Arc::new(tokio::sync::Mutex::new(()));
+        Self(lock.try_lock_owned().unwrap())
+    }
 }
 
 type JwkAggregator = GenericMultiStakeAggregator<(JwkId, JWK), true>;
@@ -1321,23 +1331,29 @@ impl AuthorityPerEpochStore {
         &self,
         key: &TransactionKey,
         objects: &[InputObjectKind],
-    ) -> BTreeSet<InputKey> {
-        let mut shared_locks = HashMap::<ObjectID, SequenceNumber>::new();
+    ) -> SuiResult<BTreeSet<InputKey>> {
+        let shared_locks =
+            once_cell::unsync::OnceCell::<Option<HashMap<ObjectID, SequenceNumber>>>::new();
         objects
             .iter()
             .map(|kind| {
-                match kind {
+                Ok(match kind {
                     InputObjectKind::SharedMoveObject { id, .. } => {
-                        if shared_locks.is_empty() {
-                            shared_locks = self
-                                .get_shared_locks(key)
-                                .expect("Read from storage should not fail!")
-                                .into_iter()
-                                .collect();
-                        }
-                        // If we can't find the locked version, it means
-                        // 1. either we have a bug that skips shared object version assignment
-                        // 2. or we have some DB corruption
+                        let shared_locks = shared_locks
+                            .get_or_init(|| {
+                                self.get_shared_locks(key)
+                                    .expect("reading shared locks should not fail")
+                                    .map(|locks| locks.into_iter().collect())
+                            })
+                            .as_ref()
+                            // Shared version assignments could have been deleted if the tx just
+                            // finished executing concurrently.
+                            .ok_or(SuiError::GenericAuthorityError {
+                                error: "no shared locks".to_string(),
+                            })?;
+
+                        // If we found locks, but they are missing the assignment for this object,
+                        // it indicates a serious inconsistency!
                         let Some(version) = shared_locks.get(id) else {
                             panic!(
                                 "Shared object locks should have been set. key: {key:?}, obj \
@@ -1354,7 +1370,7 @@ impl AuthorityPerEpochStore {
                         id: objref.0,
                         version: objref.1,
                     },
-                }
+                })
             })
             .collect()
     }
@@ -4281,12 +4297,8 @@ impl GetSharedLocks for AuthorityPerEpochStore {
     fn get_shared_locks(
         &self,
         key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, SuiError> {
-        Ok(self
-            .tables()?
-            .assigned_shared_object_versions_v2
-            .get(key)?
-            .unwrap_or_default())
+    ) -> SuiResult<Option<Vec<(ObjectID, SequenceNumber)>>> {
+        Ok(self.tables()?.assigned_shared_object_versions_v2.get(key)?)
     }
 }
 
```

### crates/sui-core/src/transaction_input_loader.rs
```diff
@@ -1,13 +1,16 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0
 
-use crate::execution_cache::ObjectCacheRead;
+use crate::{
+    authority::authority_per_epoch_store::CertLockGuard, execution_cache::ObjectCacheRead,
+};
 use itertools::izip;
+use mysten_common::fatal;
 use once_cell::unsync::OnceCell;
 use std::collections::HashMap;
 use std::sync::Arc;
 use sui_types::{
-    base_types::{EpochId, ObjectID, ObjectRef, SequenceNumber, TransactionDigest},
+    base_types::{EpochId, ObjectRef, TransactionDigest},
     error::{SuiError, SuiResult, UserInputError},
     storage::{GetSharedLocks, ObjectKey},
     transaction::{
@@ -126,10 +129,11 @@ impl TransactionInputLoader {
         &self,
         shared_lock_store: &impl GetSharedLocks,
         tx_key: &TransactionKey,
+        _tx_lock: &CertLockGuard, // see below for why this is needed
         input_object_kinds: &[InputObjectKind],
         epoch_id: EpochId,
     ) -> SuiResult<InputObjects> {
-        let shared_locks_cell: OnceCell<HashMap<_, _>> = OnceCell::new();
+        let shared_locks_cell: OnceCell<Option<HashMap<_, _>>> = OnceCell::new();
 
         let mut results = vec![None; input_object_kinds.len()];
         let mut object_keys = Vec::with_capacity(input_object_kinds.len());
@@ -153,17 +157,22 @@ impl TransactionInputLoader {
                     fetches.push((i, input));
                 }
                 InputObjectKind::SharedMoveObject { id, .. } => {
-                    let shared_locks = shared_locks_cell.get_or_try_init(|| {
-                        Ok::<HashMap<ObjectID, SequenceNumber>, SuiError>(
+                    let shared_locks = shared_locks_cell
+                        .get_or_init(|| {
                             shared_lock_store
-                                .get_shared_locks(tx_key)?
-                                .into_iter()
-                                .collect(),
-                        )
-                    })?;
-                    // If we can't find the locked version, it means
-                    // 1. either we have a bug that skips shared object version assignment
-                    // 2. or we have some DB corruption
+                                .get_shared_locks(tx_key)
+                                .expect("loading shared locks should not fail")
+                                .map(|locks| locks.into_iter().collect())
+                        })
+                        .as_ref()
+                        .unwrap_or_else(|| {
+                            // Important to hold the _tx_lock here - otherwise it would be possible
+                            // for a concurrent execution of the same tx to enter this point after the
+                            // first execution has finished and the shared locks have been deleted.
+                            fatal!("Failed to get shared locks for transaction {tx_key:?}");
+                        });
+
+                    // If we find a set of locks but an object is missing, it indicates a serious inconsistency:
                     let version = shared_locks.get(id).unwrap_or_else(|| {
                         panic!("Shared object locks should have been set. key: {tx_key:?}, obj id: {id:?}")
                     });
```

### crates/sui-core/src/transaction_manager.rs
```diff
@@ -9,6 +9,7 @@ use std::{
 };
 
 use lru::LruCache;
+use mysten_common::fatal;
 use mysten_metrics::monitored_scope;
 use parking_lot::RwLock;
 use sui_types::{
@@ -414,7 +415,7 @@ impl TransactionManager {
                     .transaction_cache_read
                     .is_tx_already_executed(&digest)
                     .unwrap_or_else(|err| {
-                        panic!("Failed to check if tx is already executed: {:?}", err)
+                        fatal!("Failed to check if tx is already executed: {:?}", err)
                     })
                 {
                     self.metrics
@@ -432,15 +433,32 @@ impl TransactionManager {
         let mut receiving_objects: HashSet<InputKey> = HashSet::new();
         let certs: Vec<_> = certs
             .into_iter()
-            .map(|(cert, fx_digest)| {
+            .filter_map(|(cert, fx_digest)| {
                 let input_object_kinds = cert
                     .data()
                     .intent_message()
                     .value
                     .input_objects()
                     .expect("input_objects() cannot fail");
                 let mut input_object_keys =
-                    epoch_store.get_input_object_keys(&cert.key(), &input_object_kinds);
+                    match epoch_store.get_input_object_keys(&cert.key(), &input_object_kinds) {
+                        Ok(keys) => keys,
+                        Err(e) => {
+                            // Because we do not hold the transaction lock during enqueue, it is possible
+                            // that the transaction was executed and the shared version assignments deleted
+                            // since the earlier check. This is a rare race condition, and it is better to
+                            // handle it ad-hoc here than to hold tx locks for every cert for the duration
+                            // of this function in order to remove the race.
+                            if self
+                                .transaction_cache_read
+                                .is_tx_already_executed(cert.digest())
+                                .expect("is_tx_already_executed cannot fail")
+                            {
+                                return None;
+                            }
+                            fatal!("Failed to get input object keys: {:?}", e);
+                        }
+                    };
 
                 if input_object_kinds.len() != input_object_keys.len() {
                     error!("Duplicated input objects: {:?}", input_object_kinds);
@@ -467,7 +485,7 @@ impl TransactionManager {
                     }
                 }
 
-                (cert, fx_digest, input_object_keys)
+                Some((cert, fx_digest, input_object_keys))
             })
             .collect();
 
```

### crates/sui-core/src/unit_tests/authority_tests.rs
```diff
@@ -4742,6 +4742,7 @@ async fn test_shared_object_transaction_ok() {
         .epoch_store_for_testing()
         .get_shared_locks(&certificate.key())
         .expect("Reading shared locks should not fail")
+        .expect("Locks should be set")
         .into_iter()
         .find_map(|(object_id, version)| {
             if object_id == shared_object_id {
@@ -4858,6 +4859,7 @@ async fn test_consensus_commit_prologue_generation() {
             .epoch_store_for_testing()
             .get_shared_locks(txn_key)
             .unwrap()
+            .expect("locks should be set")
             .iter()
             .filter_map(|(id, seq)| {
                 if id == &SUI_CLOCK_OBJECT_ID {
@@ -6216,6 +6218,7 @@ async fn test_consensus_handler_congestion_control_transaction_cancellation() {
         .epoch_store_for_testing()
         .get_shared_locks(&cancelled_txn.key())
         .expect("Reading shared locks should not fail")
+        .expect("locks should be set")
         .into_iter()
         .collect::<HashMap<_, _>>();
     assert_eq!(
@@ -6234,6 +6237,7 @@ async fn test_consensus_handler_congestion_control_transaction_cancellation() {
         .read_objects_for_execution(
             authority.epoch_store_for_testing().as_ref(),
             &cancelled_txn.key(),
+            &CertLockGuard::dummy_for_tests(),
             &cancelled_txn
                 .data()
                 .transaction_data()
```

### crates/sui-single-node-benchmark/src/mock_storage.rs
```diff
@@ -48,7 +48,7 @@ impl InMemoryObjectStore {
         tx_key: &TransactionKey,
         input_object_kinds: &[InputObjectKind],
     ) -> SuiResult<InputObjects> {
-        let shared_locks_cell: OnceCell<HashMap<_, _>> = OnceCell::new();
+        let shared_locks_cell: OnceCell<Option<HashMap<_, _>>> = OnceCell::new();
         let mut input_objects = Vec::new();
         for kind in input_object_kinds {
             let obj: Option<Object> = match kind {
@@ -58,11 +58,17 @@ impl InMemoryObjectStore {
                 }
 
                 InputObjectKind::SharedMoveObject { id, .. } => {
-                    let shared_locks = shared_locks_cell.get_or_try_init(|| {
-                        Ok::<HashMap<ObjectID, SequenceNumber>, SuiError>(
-                            shared_locks.get_shared_locks(tx_key)?.into_iter().collect(),
-                        )
-                    })?;
+                    let shared_locks = shared_locks_cell
+                        .get_or_init(|| {
+                            shared_locks
+                                .get_shared_locks(tx_key)
+                                .expect("get_shared_locks should not fail")
+                                .map(|l| l.into_iter().collect())
+                        })
+                        .as_ref()
+                        .ok_or_else(|| SuiError::GenericAuthorityError {
+                            error: "Shared object locks should have been set.".to_string(),
+                        })?;
                     let version = shared_locks.get(id).unwrap_or_else(|| {
                         panic!("Shared object locks should have been set. key: {tx_key:?}, obj id: {id:?}")
                     });
@@ -174,7 +180,7 @@ impl GetSharedLocks for InMemoryObjectStore {
     fn get_shared_locks(
         &self,
         _key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, SuiError> {
+    ) -> SuiResult<Option<Vec<(ObjectID, SequenceNumber)>>> {
         unreachable!()
     }
 }
```

### crates/sui-transactional-test-runner/src/lib.rs
```diff
@@ -15,6 +15,7 @@ use simulacrum::SimulatorStore;
 use simulator_persisted_store::PersistedStore;
 use std::path::Path;
 use std::sync::Arc;
+use sui_core::authority::authority_per_epoch_store::CertLockGuard;
 use sui_core::authority::authority_test_utils::send_and_confirm_transaction_with_execution_error;
 use sui_core::authority::AuthorityState;
 use sui_json_rpc::authority_state::StateRead;
@@ -142,7 +143,11 @@ impl TransactionalAdapter for ValidatorWithFullnode {
         );
 
         let epoch_store = self.validator.load_epoch_store_one_call_per_task().clone();
-        self.validator.read_objects_for_execution(&tx, &epoch_store)
+        self.validator.read_objects_for_execution(
+            &CertLockGuard::dummy_for_tests(),
+            &tx,
+            &epoch_store,
+        )
     }
 
     fn prepare_txn(
```

### crates/sui-types/src/storage/mod.rs
```diff
@@ -609,5 +609,5 @@ pub trait GetSharedLocks: Send + Sync {
     fn get_shared_locks(
         &self,
         key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, SuiError>;
+    ) -> SuiResult<Option<Vec<(ObjectID, SequenceNumber)>>>;
 }
```
