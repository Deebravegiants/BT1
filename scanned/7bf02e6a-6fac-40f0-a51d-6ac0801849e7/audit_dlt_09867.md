# [?] Fix rare crash when a transaction executes after its shared object assignments have been deleted (#4757)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-01-23
Source: https://github.com/iotaledger/iota/commit/cec92b78c62640cf8f0e59fbda2764c6aed57f5b
Type: security-commit

## Details
Fix rare crash when a transaction executes after its shared object assignments have been deleted (#4757)

* Apply upstream change of MystenLabs/sui@3aac32e

* Fix errors

* Fix typo

* Fix error

* Clippy

* Update crates/iota-core/src/authority.rs

Co-authored-by: DaughterOfMars <chloedaughterofmars@gmail.com>

* Update crates/iota-core/src/authority.rs

Co-authored-by: DaughterOfMars <chloedaughterofmars@gmail.com>

* Fmt

* Remove unused macro for CertLockGuard

* Move the _tx_lock comments

* Rename dummy_for_tests to guard_for_tests

* Refine expect mesage

* Add TODO comments for fatal! usage

* Modify the comments

* Enhance tag

* Use fatal macro

---------

Co-authored-by: DaughterOfMars <chloedaughterofmars@gmail.com>

## Patch
### crates/iota-core/src/authority.rs
```diff
@@ -18,6 +18,7 @@ use std::{
 use anyhow::anyhow;
 use arc_swap::{ArcSwap, Guard};
 use async_trait::async_trait;
+use authority_per_epoch_store::CertLockGuard;
 pub use authority_store::{AuthorityStore, ResolverWrapper, UpdateType};
 use chrono::prelude::*;
 use fastcrypto::{
@@ -1151,7 +1152,21 @@ impl AuthorityState {
         debug!("execute_certificate_internal");
 
         let tx_digest = certificate.digest();
-        let input_objects = self.read_objects_for_execution(certificate, epoch_store)?;
+
+        // Acquire a lock to prevent concurrent executions of the same transaction.
+        let tx_guard = epoch_store.acquire_tx_guard(certificate).await?;
+
+        // The cert could have been processed by a concurrent attempt of the same cert,
+        // so check if the effects have already been written.
+        if let Some(effects) = self
+            .get_transaction_cache_reader()
+            .get_executed_effects(tx_digest)?
+        {
+            tx_guard.release();
+            return Ok((effects, None));
+        }
+        let input_objects =
+            self.read_objects_for_execution(tx_guard.as_lock_guard(), certificate, epoch_store)?;
 
         if expected_effects_digest.is_none() {
             // We could be re-executing a previously executed but uncommitted transaction,
@@ -1161,13 +1176,6 @@ impl AuthorityState {
             expected_effects_digest = epoch_store.get_signed_effects_digest(tx_digest)?;
         }
 
-        // This acquires a lock on the tx digest to prevent multiple concurrent
-        // executions of the same tx. While we don't need this for safety (tx
-        // sequencing is ultimately atomic), it is very common to receive the
-        // same tx multiple times simultaneously due to gossip, so we
-        // may as well hold the lock and save the cpu time for other requests.
-        let tx_guard = epoch_store.acquire_tx_guard(certificate).await?;
-
         self.process_certificate(
             tx_guard,
             certificate,
@@ -1181,6 +1189,7 @@ impl AuthorityState {
 
     pub fn read_objects_for_execution(
         &self,
+        tx_lock: &CertLockGuard,
         certificate: &VerifiedExecutableTransaction,
         epoch_store: &Arc<AuthorityPerEpochStore>,
     ) -> IotaResult<InputObjects> {
@@ -1193,6 +1202,7 @@ impl AuthorityState {
         self.input_loader.read_objects_for_execution(
             epoch_store.as_ref(),
             &certificate.key(),
+            tx_lock,
             input_objects,
             epoch_store.epoch(),
         )
@@ -1283,15 +1293,6 @@ impl AuthorityState {
             }
         });
 
-        // The cert could have been processed by a concurrent attempt of the same cert,
-        // so check if the effects have already been written.
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
@@ -4599,7 +4600,7 @@ impl AuthorityState {
         );
 
         fail_point_async!("change_epoch_tx_delay");
-        let _tx_lock = epoch_store.acquire_tx_lock(tx_digest).await;
+        let tx_lock = epoch_store.acquire_tx_lock(tx_digest).await;
 
         // The tx could have been executed by state sync already - if so simply return
         // an error. The checkpoint builder will shortly be terminated by
@@ -4628,7 +4629,8 @@ impl AuthorityState {
             ])
             .await?;
 
-        let input_objects = self.read_objects_for_execution(&executable_tx, epoch_store)?;
+        let input_objects =
+            self.read_objects_for_execution(&tx_lock, &executable_tx, epoch_store)?;
 
         let (temporary_store, effects, _execution_error_opt) =
             self.prepare_certificate(&execution_guard, &executable_tx, input_objects, epoch_store)?;
```

### crates/iota-core/src/authority/authority_per_epoch_store.rs
```diff
@@ -132,11 +132,21 @@ pub(crate) type EncG = bls12381::G2Element;
 // storage, having this distinction will be useful, as we will most likely have
 // to re-implement a retry / write-ahead-log at that point.
 pub struct CertLockGuard(#[expect(unused)] MutexGuard);
-pub struct CertTxGuard(#[expect(unused)] CertLockGuard);
+pub struct CertTxGuard(CertLockGuard);
 
 impl CertTxGuard {
     pub fn release(self) {}
     pub fn commit_tx(self) {}
+    pub fn as_lock_guard(&self) -> &CertLockGuard {
+        &self.0
+    }
+}
+
+impl CertLockGuard {
+    pub fn guard_for_tests() -> Self {
+        let lock = Arc::new(tokio::sync::Mutex::new(()));
+        Self(lock.try_lock_owned().unwrap())
+    }
 }
 
 type JwkAggregator = GenericMultiStakeAggregator<(JwkId, JWK), true>;
@@ -1263,23 +1273,28 @@ impl AuthorityPerEpochStore {
         &self,
         key: &TransactionKey,
         objects: &[InputObjectKind],
-    ) -> BTreeSet<InputKey> {
-        let mut shared_locks = HashMap::<ObjectID, SequenceNumber>::new();
+    ) -> IotaResult<BTreeSet<InputKey>> {
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
+                            .ok_or(IotaError::GenericAuthority {
+                                error: "no shared locks".to_string(),
+                            })?;
+                        // If we found locks, but they are missing the assignment for this object,
+                        // it indicates a serious inconsistency!
                         let Some(version) = shared_locks.get(id) else {
                             panic!(
                                 "Shared object locks should have been set. key: {key:?}, obj \
@@ -1296,7 +1311,7 @@ impl AuthorityPerEpochStore {
                         id: objref.0,
                         version: objref.1,
                     },
-                }
+                })
             })
             .collect()
     }
@@ -4051,12 +4066,8 @@ impl GetSharedLocks for AuthorityPerEpochStore {
     fn get_shared_locks(
         &self,
         key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, IotaError> {
-        Ok(self
-            .tables()?
-            .assigned_shared_object_versions
-            .get(key)?
-            .unwrap_or_default())
+    ) -> IotaResult<Option<Vec<(ObjectID, SequenceNumber)>>> {
+        Ok(self.tables()?.assigned_shared_object_versions.get(key)?)
     }
 }
 
```

### crates/iota-core/src/transaction_input_loader.rs
```diff
@@ -4,8 +4,9 @@
 
 use std::{collections::HashMap, sync::Arc};
 
+use iota_common::fatal;
 use iota_types::{
-    base_types::{EpochId, ObjectID, ObjectRef, SequenceNumber, TransactionDigest},
+    base_types::{EpochId, ObjectRef, TransactionDigest},
     error::{IotaError, IotaResult, UserInputError},
     storage::{GetSharedLocks, ObjectKey},
     transaction::{
@@ -17,7 +18,9 @@ use itertools::izip;
 use once_cell::unsync::OnceCell;
 use tracing::instrument;
 
-use crate::execution_cache::ObjectCacheRead;
+use crate::{
+    authority::authority_per_epoch_store::CertLockGuard, execution_cache::ObjectCacheRead,
+};
 
 pub(crate) struct TransactionInputLoader {
     cache: Arc<dyn ObjectCacheRead>,
@@ -134,10 +137,14 @@ impl TransactionInputLoader {
         &self,
         shared_lock_store: &impl GetSharedLocks,
         tx_key: &TransactionKey,
+        // Important to hold the _tx_lock, otherwise it would be possible for a concurrent
+        // execution of the same tx to enter this point after the first execution has
+        // finished and the shared locks have been deleted.
+        _tx_lock: &CertLockGuard,
         input_object_kinds: &[InputObjectKind],
         epoch_id: EpochId,
     ) -> IotaResult<InputObjects> {
-        let shared_locks_cell: OnceCell<HashMap<_, _>> = OnceCell::new();
+        let shared_locks_cell: OnceCell<Option<HashMap<_, _>>> = OnceCell::new();
 
         let mut results = vec![None; input_object_kinds.len()];
         let mut object_keys = Vec::with_capacity(input_object_kinds.len());
@@ -161,17 +168,20 @@ impl TransactionInputLoader {
                     fetches.push((i, input));
                 }
                 InputObjectKind::SharedMoveObject { id, .. } => {
-                    let shared_locks = shared_locks_cell.get_or_try_init(|| {
-                        Ok::<HashMap<ObjectID, SequenceNumber>, IotaError>(
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
+                            // _tx_lock is held, so this should not happen
+                            fatal!("Failed to get shared locks for transaction {tx_key:?}");
+                        });
+                    // If we find a set of locks but an object is missing, it indicates a serious
+                    // inconsistency:
                     let version = shared_locks.get(id).unwrap_or_else(|| {
                         panic!("Shared object locks should have been set. key: {tx_key:?}, obj id: {id:?}")
                     });
```

### crates/iota-core/src/transaction_manager.rs
```diff
@@ -9,6 +9,7 @@ use std::{
     time::Duration,
 };
 
+use iota_common::fatal;
 use iota_config::node::AuthorityOverloadConfig;
 use iota_metrics::monitored_scope;
 use iota_types::{
@@ -420,7 +421,7 @@ impl TransactionManager {
                     .transaction_cache_read
                     .is_tx_already_executed(&digest)
                     .unwrap_or_else(|err| {
-                        panic!("Failed to check if tx is already executed: {:?}", err)
+                        fatal!("Failed to check if tx is already executed: {:?}", err)
                     })
                 {
                     self.metrics
@@ -438,15 +439,33 @@ impl TransactionManager {
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
+                            // Because we do not hold the transaction lock during enqueue, it is
+                            // possible that the transaction was executed and the shared version
+                            // assignments deleted since the earlier check. This is a rare race
+                            // condition, and it is better to handle it ad-hoc here than to hold tx
+                            // locks for every cert for the duration of this function in order to
+                            // remove the race.
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
@@ -473,7 +492,7 @@ impl TransactionManager {
                     }
                 }
 
-                (cert, fx_digest, input_object_keys)
+                Some((cert, fx_digest, input_object_keys))
             })
             .collect();
 
```

### crates/iota-core/src/unit_tests/authority_tests.rs
```diff
@@ -2069,15 +2069,15 @@ async fn test_conflicting_transactions() {
             &ok.clone().status.into_signed_for_testing(),
             object_info
                 .lock_for_debugging
-                .expect("object should be locked")
+                .expect("object is not locked")
                 .auth_sig()
         );
 
         assert_eq!(
             &ok.clone().status.into_signed_for_testing(),
             gas_info
                 .lock_for_debugging
-                .expect("gas should be locked")
+                .expect("gas is not locked")
                 .auth_sig()
         );
 
@@ -2421,7 +2421,7 @@ async fn test_handle_confirmation_transaction_ok() {
                 &authority_state.epoch_store_for_testing()
             )
             .await
-            .expect("Exists")
+            .expect("failed to retrieve transaction lock")
             .is_none()
     );
 }
@@ -4712,7 +4712,8 @@ async fn test_shared_object_transaction_ok() {
     let shared_object_version = authority
         .epoch_store_for_testing()
         .get_shared_locks(&certificate.key())
-        .expect("Reading shared locks should not fail")
+        .expect("failed to read shared locks")
+        .expect("locks are not set")
         .into_iter()
         .find_map(|(object_id, version)| {
             if object_id == shared_object_id {
@@ -4721,7 +4722,7 @@ async fn test_shared_object_transaction_ok() {
                 None
             }
         })
-        .expect("Shared object must be locked");
+        .expect("shared object is not locked");
     assert_eq!(shared_object_version, OBJECT_START_VERSION);
 
     // Finally (Re-)execute the contract should succeed.
@@ -4824,6 +4825,7 @@ async fn test_consensus_commit_prologue_generation() {
             .epoch_store_for_testing()
             .get_shared_locks(txn_key)
             .unwrap()
+            .expect("locks are not set")
             .iter()
             .filter_map(|(id, seq)| {
                 if id == &IOTA_CLOCK_OBJECT_ID {
@@ -6149,7 +6151,8 @@ async fn test_consensus_handler_congestion_control_transaction_cancellation() {
     let shared_object_version = authority
         .epoch_store_for_testing()
         .get_shared_locks(&cancelled_txn.key())
-        .expect("Reading shared locks should not fail")
+        .expect("failed to read shared locks")
+        .expect("locks are not set")
         .into_iter()
         .collect::<HashMap<_, _>>();
     assert_eq!(
@@ -6168,6 +6171,7 @@ async fn test_consensus_handler_congestion_control_transaction_cancellation() {
         .read_objects_for_execution(
             authority.epoch_store_for_testing().as_ref(),
             &cancelled_txn.key(),
+            &CertLockGuard::guard_for_tests(),
             &cancelled_txn
                 .data()
                 .transaction_data()
```

### crates/iota-single-node-benchmark/src/mock_storage.rs
```diff
@@ -57,7 +57,7 @@ impl InMemoryObjectStore {
         tx_key: &TransactionKey,
         input_object_kinds: &[InputObjectKind],
     ) -> IotaResult<InputObjects> {
-        let shared_locks_cell: OnceCell<HashMap<_, _>> = OnceCell::new();
+        let shared_locks_cell: OnceCell<Option<HashMap<_, _>>> = OnceCell::new();
         let mut input_objects = Vec::new();
         for kind in input_object_kinds {
             let obj: Option<Object> = match kind {
@@ -67,11 +67,17 @@ impl InMemoryObjectStore {
                 }
 
                 InputObjectKind::SharedMoveObject { id, .. } => {
-                    let shared_locks = shared_locks_cell.get_or_try_init(|| {
-                        Ok::<HashMap<ObjectID, SequenceNumber>, IotaError>(
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
+                        .ok_or_else(|| IotaError::GenericAuthority {
+                            error: "Shared object locks should have been set.".to_string(),
+                        })?;
                     let version = shared_locks.get(id).unwrap_or_else(|| {
                         panic!("Shared object locks should have been set. key: {tx_key:?}, obj id: {id:?}")
                     });
@@ -174,7 +180,7 @@ impl GetSharedLocks for InMemoryObjectStore {
     fn get_shared_locks(
         &self,
         _key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, IotaError> {
+    ) -> IotaResult<Option<Vec<(ObjectID, SequenceNumber)>>> {
         unreachable!()
     }
 }
```

### crates/iota-transactional-test-runner/src/lib.rs
```diff
@@ -13,7 +13,8 @@ pub mod test_adapter;
 use std::{path::Path, sync::Arc};
 
 use iota_core::authority::{
-    AuthorityState, authority_test_utils::send_and_confirm_transaction_with_execution_error,
+    AuthorityState, authority_per_epoch_store::CertLockGuard,
+    authority_test_utils::send_and_confirm_transaction_with_execution_error,
 };
 use iota_json_rpc::authority_state::StateRead;
 use iota_json_rpc_types::{DevInspectResults, EventFilter};
@@ -134,7 +135,11 @@ impl TransactionalAdapter for ValidatorWithFullnode {
         );
 
         let epoch_store = self.validator.load_epoch_store_one_call_per_task().clone();
-        self.validator.read_objects_for_execution(&tx, &epoch_store)
+        self.validator.read_objects_for_execution(
+            &CertLockGuard::guard_for_tests(),
+            &tx,
+            &epoch_store,
+        )
     }
 
     fn prepare_txn(
```

### crates/iota-types/src/storage/mod.rs
```diff
@@ -572,5 +572,5 @@ pub trait GetSharedLocks: Send + Sync {
     fn get_shared_locks(
         &self,
         key: &TransactionKey,
-    ) -> Result<Vec<(ObjectID, SequenceNumber)>, IotaError>;
+    ) -> IotaResult<Option<Vec<(ObjectID, SequenceNumber)>>>;
 }
```
