# [?] Improve random db crash and fix found bugs. (#916)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-02-07
Source: https://github.com/Conflux-Chain/conflux-rust/commit/fc9f1e8d85bbfdb7fcdcb8464a80d62397ee7172
Type: security-commit

## Details
Improve random db crash and fix found bugs. (#916)

## Patch
### client/src/rpc/impls/cfx.rs
```diff
@@ -642,6 +642,7 @@ impl TestRpc for TestRpcImpl {
             fn get_transaction_receipt(&self, tx_hash: H256) -> RpcResult<Option<RpcReceipt>>;
             fn say_hello(&self) -> RpcResult<String>;
             fn stop(&self) -> RpcResult<()>;
+            fn save_node_db(&self) -> RpcResult<()>;
         }
 
         target self.rpc_impl {
```

### client/src/rpc/impls/common.rs
```diff
@@ -628,7 +628,7 @@ impl RpcImpl {
     pub fn sign(
         &self, data: Bytes, address: RpcH160, password: Option<String>,
     ) -> RpcResult<RpcH520> {
-        let message = self.eth_data_hash(data.0);
+        let message = eth_data_hash(data.0);
         let password = password.map(Password::from);
         let signature =
             match self.accounts.sign(address.into(), password, message) {
@@ -641,14 +641,18 @@ impl RpcImpl {
         Ok(RpcH520(signature.into()))
     }
 
-    /// Returns a eth_sign-compatible hash of data to sign.
-    /// The data is prepended with special message to prevent
-    /// malicious DApps from using the function to sign forged transactions.
-    fn eth_data_hash(&self, mut data: Vec<u8>) -> H256 {
-        let mut message_data =
-            format!("\x19Ethereum Signed Message:\n{}", data.len())
-                .into_bytes();
-        message_data.append(&mut data);
-        keccak(message_data)
+    pub fn save_node_db(&self) -> RpcResult<()> {
+        self.network.save_node_db();
+        Ok(())
     }
 }
+
+/// Returns a eth_sign-compatible hash of data to sign.
+/// The data is prepended with special message to prevent
+/// malicious DApps from using the function to sign forged transactions.
+fn eth_data_hash(mut data: Vec<u8>) -> H256 {
+    let mut message_data =
+        format!("\x19Ethereum Signed Message:\n{}", data.len()).into_bytes();
+    message_data.append(&mut data);
+    keccak(message_data)
+}
```

### client/src/rpc/impls/light.rs
```diff
@@ -351,6 +351,7 @@ impl TestRpc for TestRpcImpl {
             fn get_transaction_receipt(&self, tx_hash: H256) -> RpcResult<Option<RpcReceipt>>;
             fn say_hello(&self) -> RpcResult<String>;
             fn stop(&self) -> RpcResult<()>;
+            fn save_node_db(&self) -> RpcResult<()>;
         }
     }
 
```

### client/src/rpc/traits/test.rs
```diff
@@ -109,4 +109,7 @@ pub trait TestRpc {
     fn set_db_crash(
         &self, crash_probability: f64, crash_exit_code: i32,
     ) -> RpcResult<()>;
+
+    #[rpc(name = "save_node_db")]
+    fn save_node_db(&self) -> RpcResult<()>;
 }
```

### core/src/consensus/consensus_inner/consensus_new_block_handler.rs
```diff
@@ -1487,9 +1487,6 @@ impl ConsensusNewBlockHandler {
     /// This function is only invoked from recover_graph_from_db with
     /// header_only being false.
     pub fn construct_pivot_state(&self, inner: &mut ConsensusGraphInner) {
-        if inner.pivot_chain.len() < DEFERRED_STATE_EPOCH_COUNT as usize {
-            return;
-        }
         // FIXME: this line doesn't exactly match its purpose.
         // FIXME: Is it the checkpoint or synced snapshot or could it be
         // anything else?
@@ -1525,6 +1522,10 @@ impl ConsensusNewBlockHandler {
                     .push(inner.arena[inner.pivot_chain[pivot_index]].hash);
             }
         }
+
+        if inner.pivot_chain.len() < DEFERRED_STATE_EPOCH_COUNT as usize {
+            return;
+        }
         for pivot_index in start_pivot_index + 1
             ..inner.pivot_chain.len() - DEFERRED_STATE_EPOCH_COUNT as usize + 1
         {
```

### core/src/lib.rs
```diff
@@ -89,11 +89,28 @@ pub use parameters::{
     sync as sync_parameters, WORKER_COMPUTATION_PARALLELISM,
 };
 
+/// TODO Disable/enable at compilation time.
+/// This module can trigger random process crashes during testing.
+/// This is only used to insert crashes before db modifications.
 pub mod test_context {
     use parking_lot::Mutex;
+    use rand::{thread_rng, Rng};
     lazy_static! {
+        /// The process exit code set for random crash.
         pub static ref CRASH_EXIT_CODE: Mutex<i32> = Mutex::new(100);
+        /// The probability to trigger a random crash.
+        /// Set to `None` to disable random crash.
         pub static ref CRASH_EXIT_PROBABILITY: Mutex<Option<f64>> =
             Mutex::new(None);
     }
+
+    /// Randomly crash with the probability and exit code already set.
+    pub fn random_crash_if_enabled(exit_str: &str) {
+        if let Some(p) = *CRASH_EXIT_PROBABILITY.lock() {
+            if thread_rng().gen_bool(p) {
+                info!("exit before {}", exit_str);
+                std::process::exit(*CRASH_EXIT_CODE.lock());
+            }
+        }
+    }
 }
```

### core/src/storage/impls/state.rs
```diff
@@ -582,14 +582,14 @@ impl State {
         let maybe_existing_merkle_root =
             self.delta_trie.get_merkle_root_by_epoch_id(&epoch_id)?;
         if maybe_existing_merkle_root.is_some() {
+            // TODO This may happen for genesis when we restart
             error!(
                 "Overwriting computed state for epoch {:?}, \
                  committed merkle root {:?}, new merkle root {:?}",
                 epoch_id,
                 maybe_existing_merkle_root.unwrap(),
                 merkle_root
             );
-            debug_assert!(false);
             assert_eq!(
                 maybe_existing_merkle_root,
                 Some(*merkle_root),
```

### core/src/storage/impls/storage_db/kvdb_rocksdb.rs
```diff
@@ -29,6 +29,7 @@ impl KeyValueDbTypes for KvdbRocksdb {
 
 impl KeyValueDbTrait for KvdbRocksdb {
     fn delete(&self, key: &[u8]) -> Result<Option<Option<Box<[u8]>>>> {
+        random_crash_if_enabled("rocksdb delete");
         let mut transaction = self.kvdb.transaction();
         transaction.delete(self.col, key);
         Ok(None)
@@ -37,12 +38,7 @@ impl KeyValueDbTrait for KvdbRocksdb {
     fn put(
         &self, key: &[u8], value: &[u8],
     ) -> Result<Option<Option<Box<[u8]>>>> {
-        if let Some(p) = *CRASH_EXIT_PROBABILITY.lock() {
-            if thread_rng().gen_bool(p) {
-                info!("exit before db put");
-                std::process::exit(*CRASH_EXIT_CODE.lock());
-            }
-        }
+        random_crash_if_enabled("rocksdb put");
         let mut transaction = self.kvdb.transaction();
         transaction.put(self.col, key, value);
         self.kvdb.write(transaction)?;
@@ -78,6 +74,7 @@ impl KeyValueDbTraitOwnedRead for KvdbRocksDbTransaction {
 
 impl KeyValueDbTransactionTrait for KvdbRocksDbTransaction {
     fn commit(&mut self, db: &dyn Any) -> Result<()> {
+        random_crash_if_enabled("rocksdb commit");
         match db.downcast_ref::<KvdbRocksdb>() {
             Some(as_kvdb_rocksdb) => {
                 let wrapped_ops = DBTransaction {
@@ -140,5 +137,4 @@ use super::super::{
 };
 use kvdb::DBTransaction;
 use kvdb_rocksdb::Database;
-use rand::{thread_rng, Rng};
 use std::{any::Any, sync::Arc};
```

### core/src/storage/impls/storage_db/kvdb_sqlite.rs
```diff
@@ -797,6 +797,7 @@ where ValueType::Type:
     fn put_impl(
         &mut self, key: &[u8], value: &<Self::ValueType as DbValueType>::Type,
     ) -> Result<Option<Option<Self::ValueType>>> {
+        random_crash_if_enabled("sqlite put");
         let (connection, statements) = self.destructure_mut();
         match connection {
             None => Err(Error::from(ErrorKind::DbNotExist)),
@@ -819,6 +820,7 @@ where ValueType::Type:
     fn put_with_number_key_impl(
         &mut self, key: i64, value: &<Self::ValueType as DbValueType>::Type,
     ) -> Result<Option<Option<Self::ValueType>>> {
+        random_crash_if_enabled("sqlite put_with_number_key");
         let (connection, statements) = self.destructure_mut();
         match connection {
             None => Err(Error::from(ErrorKind::DbNotExist)),
@@ -849,6 +851,7 @@ where ValueType::Type:
     fn delete_impl(
         &self, key: &[u8],
     ) -> Result<Option<Option<Self::ValueType>>> {
+        random_crash_if_enabled("sqlite delete");
         let (connection, statements) = self.destructure();
         match connection {
             None => Err(Error::from(ErrorKind::DbNotExist)),
@@ -874,6 +877,7 @@ where ValueType::Type:
     fn delete_with_number_key_impl(
         &self, key: i64,
     ) -> Result<Option<Option<Self::ValueType>>> {
+        random_crash_if_enabled("sqlite delete_with_number_key");
         let (connection, statements) = self.destructure();
         match connection {
             None => Err(Error::from(ErrorKind::DbNotExist)),
@@ -1234,6 +1238,7 @@ use super::{
     },
     sqlite::*,
 };
+use crate::test_context::random_crash_if_enabled;
 use sqlite::{Connection, Statement};
 use std::{
     any::Any,
```

### network/src/service.rs
```diff
@@ -321,6 +321,12 @@ impl NetworkService {
         );
         Some(peer)
     }
+
+    pub fn save_node_db(&self) {
+        if let Some(inner) = &self.inner {
+            inner.node_db.write().save();
+        }
+    }
 }
 
 type SharedSession = Arc<RwLock<Session>>;
@@ -351,7 +357,6 @@ struct ProtocolTimer {
 
 /// The inner implementation of NetworkService. Note that all accesses to the
 /// RWLocks of the fields have to follow the defined order to avoid race
-#[allow(dead_code)]
 pub struct NetworkServiceInner {
     pub sessions: SessionManager,
     pub metadata: HostMetadata,
@@ -366,7 +371,6 @@ pub struct NetworkServiceInner {
     timer_counter: RwLock<usize>,
     pub node_db: RwLock<NodeDatabase>,
     reserved_nodes: RwLock<HashSet<NodeId>>,
-    nodes: RwLock<HashMap<NodeId, NodeEntry>>,
     dropped_nodes: RwLock<HashSet<StreamToken>>,
 
     /// Delayed message queue and corresponding latency
@@ -545,7 +549,6 @@ impl NetworkServiceInner {
                 config.subnet_quota,
             )),
             reserved_nodes: RwLock::new(HashSet::new()),
-            nodes: RwLock::new(HashMap::new()),
             dropped_nodes: RwLock::new(HashSet::new()),
             delayed_queue: None,
         };
```

### tests/conflux_tracing.py
```diff
@@ -301,7 +301,7 @@ def __init__(
             start_timeout=10,
             blockgen_timeout=0.25,
             snapshot_timeout=5.0,
-            db_crash_timeout=2,
+            db_crash_timeout=10,
             replay=False,
             snapshot_file=None,
             txs_file=None):
@@ -391,6 +391,7 @@ def _enable_db_crash(self):
                 chosen_peer = alive_peer_indices[random.randint(
                     1, len(alive_peer_indices) - 1)]
                 self.log.info("enable db crash {}".format(chosen_peer))
+                self.nodes[chosen_peer].save_node_db()
                 self.nodes[chosen_peer].set_db_crash(CRASH_EXIT_PROBABILITY, CRASH_EXIT_CODE)
         except Exception as e:
             self.log.info('got exception[{}] during db crash'.format(repr(e)))
```

### tests/test_framework/simple_rpc_proxy.py
```diff
@@ -35,18 +35,23 @@ def __call__(self, *args, **argsn):
         except Exception as e:
             node = self.node
             if node is not None and node.auto_recovery:
+                # wait to ensure that the process has completely exited
+                time.sleep(0.01)
                 return_code = node.process.poll()
                 # TODO Parameterize return_code
-                if return_code == 100:
+                # -11 means segfault, which may be triggered if rocksdb is not properly dropped.
+                # 100 is our random db crash exit code.
+                if return_code in [-11, 100]:
                     # TODO Handle extra_args
                     node.start(stdout=node.stdout, stderr=node.stderr)
                     node.wait_for_rpc_connection()
                     node.wait_for_nodeid()
-                    node.wait_for_recovery("NormalSyncPhase", 30)
+                    node.wait_for_recovery("NormalSyncPhase", 10)
                     response = self.client.send(request, timeout=self.timeout)
                     return response.data.result
                 else:
-                    print(node.index, "exit with code", return_code)
+                    if return_code is not None:
+                        print(node.index, "exit with code", return_code, "during calling", self.method)
                     raise e
             else:
                 raise e
```
