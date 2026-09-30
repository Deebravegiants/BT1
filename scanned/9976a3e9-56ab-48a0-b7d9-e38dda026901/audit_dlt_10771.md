# [?] Merge branch 'zhangsoledad/lazy_dep' into ckb-ghsa-j35p-q24r-5367

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-06-11
Source: https://github.com/nervosnetwork/ckb/commit/8e8798a7c3826ecf8ec40b96ee6a0f2e21375e53
Type: security-commit

## Details
Merge branch 'zhangsoledad/lazy_dep' into ckb-ghsa-j35p-q24r-5367

## Patch
### Cargo.lock
```diff
@@ -2782,9 +2782,9 @@ checksum = "7e81a7c05f79578dbc15793d8b619db9ba32b4577003ef3af1a91c416798c58d"
 
 [[package]]
 name = "indicatif"
-version = "0.15.0"
+version = "0.16.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7baab56125e25686df467fe470785512329883aab42696d661247aca2a2896e4"
+checksum = "2d207dc617c7a380ab07ff572a6e52fa202a2a8f355860ac9c38e23f8196be1b"
 dependencies = [
  "console",
  "lazy_static",
@@ -3538,9 +3538,9 @@ dependencies = [
 
 [[package]]
 name = "number_prefix"
-version = "0.3.0"
+version = "0.4.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "17b02fc0ff9a9e4b35b3342880f48e896ebf69f2967921fe8646bf5b7125956a"
+checksum = "830b246a0e5f20af87141b25c173cd1b609bd7779a4617d6ec582abaf90870f3"
 
 [[package]]
 name = "numext-constructor"
```

### chain/src/tests/load_input_data_hash_cell.rs
```diff
@@ -4,7 +4,6 @@ use crate::tests::util::{
 use ckb_chain_spec::consensus::ConsensusBuilder;
 use ckb_dao_utils::genesis_dao_data;
 use ckb_test_chain_utils::load_input_data_hash_cell;
-use ckb_tx_pool::{PlugTarget, TxEntry};
 use ckb_types::prelude::*;
 use ckb_types::{
     bytes::Bytes,
@@ -49,7 +48,7 @@ pub(crate) fn create_load_input_data_hash_transaction(
         .build()
 }
 
-// Ensure tx-pool reject tx which calls syscall load_cell_data_hash from input
+// Ensure tx-pool accept tx which calls syscall load_cell_data_hash from input
 #[test]
 fn test_load_input_data_hash_cell() {
     let (_, _, load_input_data_hash_script) = load_input_data_hash_cell();
@@ -86,16 +85,9 @@ fn test_load_input_data_hash_cell() {
     let tx1 = create_load_input_data_hash_transaction(&tx0, 0);
 
     let tx_pool = shared.tx_pool_controller();
-    let ret = tx_pool.submit_local_tx(tx0.clone()).unwrap();
-    assert!(ret.is_err());
-    //ValidationFailure(2) missing item
-    assert!(format!("{}", ret.err().unwrap()).contains("ValidationFailure(2)"));
+    let ret = tx_pool.submit_local_tx(tx0).unwrap();
+    assert!(ret.is_ok());
 
-    let entry0 = vec![TxEntry::dummy_resolve(tx0, 0, Capacity::shannons(0), 100)];
-    tx_pool.plug_entry(entry0, PlugTarget::Proposed).unwrap();
-
-    // Ensure tx which calls syscall load_cell_data_hash will got reject even previous tx is already in tx-pool
     let ret = tx_pool.submit_local_tx(tx1).unwrap();
-    assert!(ret.is_err());
-    assert!(format!("{}", ret.err().unwrap()).contains("ValidationFailure(2)"));
+    assert!(ret.is_ok());
 }
```

### db-migration/Cargo.toml
```diff
@@ -15,7 +15,7 @@ ckb-db = { path = "../db", version = "= 0.43.0-pre" }
 ckb-logger = { path = "../util/logger", version = "= 0.43.0-pre" }
 ckb-error = { path = "../error", version = "= 0.43.0-pre" }
 ckb-db-schema = { path = "../db-schema", version = "= 0.43.0-pre" }
-indicatif = "0.15"
+indicatif = "0.16"
 console = ">=0.9.1, <1.0.0"
 
 [dev-dependencies]
```

### db-migration/src/lib.rs
```diff
@@ -109,8 +109,8 @@ impl Migrations {
                     let mpbc = Arc::clone(&mpb);
                     let pb = move |count: u64| -> ProgressBar {
                         let pb = mpbc.add(ProgressBar::new(count));
-                        pb.set_draw_target(ProgressDrawTarget::to_term(Term::stdout(), None));
-                        pb.set_prefix(&format!("[{}/{}]", idx + 1, migrations_count));
+                        pb.set_draw_target(ProgressDrawTarget::term(Term::stdout(), None));
+                        pb.set_prefix(format!("[{}/{}]", idx + 1, migrations_count));
                         pb
                     };
                     db = m.migrate(db, Arc::new(pb))?;
@@ -244,13 +244,13 @@ mod tests {
             ) -> Result<RocksDB, Error> {
                 let txn = db.transaction();
                 // append 1u8 to each value of column `0`
-                let migration = |key: &[u8], value: &[u8]| -> Result<(), Error> {
+                let mut migration = |key: &[u8], value: &[u8]| -> Result<(), Error> {
                     let mut new_value = value.to_vec();
                     new_value.push(1);
                     txn.put(COLUMN, key, &new_value)?;
                     Ok(())
                 };
-                db.traverse(COLUMN, migration)?;
+                db.full_traverse(COLUMN, &mut migration)?;
                 txn.commit()?;
                 Ok(db)
             }
```

### db-schema/src/lib.rs
```diff
@@ -3,7 +3,7 @@
 /// Column families alias type
 pub type Col = &'static str;
 /// Total column number
-pub const COLUMNS: u32 = 14;
+pub const COLUMNS: u32 = 15;
 /// Column store chain index
 pub const COLUMN_INDEX: Col = "0";
 /// Column store block's header
@@ -34,6 +34,8 @@ pub const COLUMN_UNCLES: Col = "11";
 pub const COLUMN_CELL_DATA: Col = "12";
 /// Column store block number-hash pair
 pub const COLUMN_NUMBER_HASH: Col = "13";
+/// Column store cell data hash
+pub const COLUMN_CELL_DATA_HASH: Col = "14";
 
 /// META_TIP_HEADER_KEY tracks the latest known best block header
 pub const META_TIP_HEADER_KEY: &[u8] = b"TIP_HEADER";
```

### db/src/db.rs
```diff
@@ -177,7 +177,7 @@ impl RocksDB {
     }
 
     /// Traverse database column with the given callback function.
-    pub fn traverse<F>(&self, col: Col, mut callback: F) -> Result<()>
+    pub fn full_traverse<F>(&self, col: Col, callback: &mut F) -> Result<()>
     where
         F: FnMut(&[u8], &[u8]) -> Result<()>,
     {
@@ -192,6 +192,36 @@ impl RocksDB {
         Ok(())
     }
 
+    /// Traverse database column with the given callback function.
+    pub fn traverse<F>(
+        &self,
+        col: Col,
+        callback: &mut F,
+        mode: IteratorMode,
+        limit: usize,
+    ) -> Result<(usize, Vec<u8>)>
+    where
+        F: FnMut(&[u8], &[u8]) -> Result<()>,
+    {
+        let mut count: usize = 0;
+        let mut next_key: Vec<u8> = vec![];
+        let cf = cf_handle(&self.inner, col)?;
+        let iter = self
+            .inner
+            .full_iterator_cf(cf, mode)
+            .map_err(internal_error)?;
+        for (key, val) in iter {
+            if count > limit {
+                next_key = key.to_vec();
+                break;
+            }
+
+            callback(&key, &val)?;
+            count += 1;
+        }
+        Ok((count, next_key))
+    }
+
     /// Set a snapshot at start of transaction by setting set_snapshot=true
     pub fn transaction(&self) -> RocksDBTransaction {
         let write_options = WriteOptions::default();
@@ -389,11 +419,11 @@ mod tests {
         assert!(db.get_pinned("1", &[2]).unwrap().is_none());
 
         let mut r = HashMap::new();
-        let callback = |k: &[u8], v: &[u8]| -> Result<()> {
+        let mut callback = |k: &[u8], v: &[u8]| -> Result<()> {
             r.insert(k.to_vec(), v.to_vec());
             Ok(())
         };
-        db.traverse("1", callback).unwrap();
+        db.full_traverse("1", &mut callback).unwrap();
         assert!(r.len() == 1);
         assert_eq!(r.get(&vec![1, 1]), Some(&vec![1, 1, 1]));
     }
```

### miner/Cargo.toml
```diff
@@ -26,7 +26,7 @@ futures = "0.1"
 lru = "0.6.0"
 ckb-stop-handler = { path = "../util/stop-handler", version = "= 0.43.0-pre" }
 ckb-error = { path = "../error", version = "= 0.43.0-pre" }
-indicatif = "0.15"
+indicatif = "0.16"
 console = "0.13.0"
 eaglesong = "0.1"
 base64 = "0.13.0"
```

### miner/src/miner.rs
```diff
@@ -145,7 +145,7 @@ impl Miner {
                 self.pb
                     .println(format!("Found! #{} {:#x}", block.number(), block_hash));
                 self.pb
-                    .set_message(&format!("Total nonces found: {:>3}", self.nonces_found));
+                    .set_message(format!("Total nonces found: {:>3}", self.nonces_found));
                 self.pb.inc(1);
             }
         }
```

### miner/src/worker/eaglesong_simple.rs
```diff
@@ -97,7 +97,7 @@ impl Worker for EaglesongSimple {
                             + u64::from(elapsed.subsec_nanos()))
                             as f64
                             / 1_000_000_000.0;
-                        progress_bar.set_message(&format!(
+                        progress_bar.set_message(format!(
                             "hash rate: {:>10.3} / nonces found: {:>10}",
                             state_update_counter as f64 / elapsed_nanos,
                             self.nonces_found,
```

### miner/src/worker/mod.rs
```diff
@@ -70,7 +70,7 @@ pub fn start_worker(
                 let worker_name = "Dummy-Worker";
                 let pb = mp.add(ProgressBar::new(100));
                 pb.set_style(ProgressStyle::default_bar().template(PROGRESS_BAR_TEMPLATE));
-                pb.set_prefix(&worker_name);
+                pb.set_prefix(worker_name);
 
                 let (worker_tx, worker_rx) = unbounded();
                 let mut worker = Dummy::try_new(config, nonce_tx, worker_rx)
@@ -104,7 +104,7 @@ pub fn start_worker(
                         // since we only show the spinner in console.
                         let pb = mp.add(ProgressBar::new(100));
                         pb.set_style(ProgressStyle::default_bar().template(PROGRESS_BAR_TEMPLATE));
-                        pb.set_prefix(&worker_name);
+                        pb.set_prefix(worker_name.clone());
 
                         let (worker_tx, worker_rx) = unbounded();
                         let nonce_tx = nonce_tx.clone();
```

### rpc/src/module/experiment.rs
```diff
@@ -214,12 +214,12 @@ pub(crate) struct DryRunner<'a> {
 }
 
 impl<'a> CellProvider for DryRunner<'a> {
-    fn cell(&self, out_point: &packed::OutPoint, with_data: bool) -> CellStatus {
+    fn cell(&self, out_point: &packed::OutPoint, eager_load: bool) -> CellStatus {
         let snapshot = self.shared.snapshot();
         snapshot
             .get_cell(out_point)
             .map(|mut cell_meta| {
-                if with_data {
+                if eager_load {
                     if let Some((data, data_hash)) = snapshot.get_cell_data(out_point) {
                         cell_meta.mem_cell_data = Some(data);
                         cell_meta.mem_cell_data_hash = Some(data_hash);
```

### script/src/syscalls/load_cell.rs
```diff
@@ -6,6 +6,7 @@ use crate::{
     },
 };
 use byteorder::{LittleEndian, WriteBytesExt};
+use ckb_traits::CellDataProvider;
 use ckb_types::{
     core::{cell::CellMeta, Capacity},
     packed::CellOutput,
@@ -16,23 +17,26 @@ use ckb_vm::{
     Error as VMError, Register, SupportMachine, Syscalls,
 };
 
-pub struct LoadCell<'a> {
+pub struct LoadCell<'a, DL> {
+    data_loader: &'a DL,
     outputs: &'a [CellMeta],
     resolved_inputs: &'a [CellMeta],
     resolved_cell_deps: &'a [CellMeta],
     group_inputs: &'a [usize],
     group_outputs: &'a [usize],
 }
 
-impl<'a> LoadCell<'a> {
+impl<'a, DL: CellDataProvider + 'a> LoadCell<'a, DL> {
     pub fn new(
+        data_loader: &'a DL,
         outputs: &'a [CellMeta],
         resolved_inputs: &'a [CellMeta],
         resolved_cell_deps: &'a [CellMeta],
         group_inputs: &'a [usize],
         group_outputs: &'a [usize],
-    ) -> LoadCell<'a> {
+    ) -> LoadCell<'a, DL> {
         LoadCell {
+            data_loader,
             outputs,
             resolved_inputs,
             resolved_cell_deps,
@@ -98,9 +102,8 @@ impl<'a> LoadCell<'a> {
                 (SUCCESS, store_data(machine, &buffer)?)
             }
             CellField::DataHash => {
-                if let Some(data_hash) = &cell.mem_cell_data_hash {
-                    let bytes = data_hash.raw_data();
-                    (SUCCESS, store_data(machine, &bytes)?)
+                if let Some(bytes) = self.data_loader.load_cell_data_hash(cell) {
+                    (SUCCESS, store_data(machine, &bytes.as_bytes())?)
                 } else {
                     (ITEM_MISSING, 0)
                 }
@@ -144,7 +147,7 @@ impl<'a> LoadCell<'a> {
     }
 }
 
-impl<'a, Mac: SupportMachine> Syscalls<Mac> for LoadCell<'a> {
+impl<'a, Mac: SupportMachine, DL: CellDataProvider> Syscalls<Mac> for LoadCell<'a, DL> {
     fn initialize(&mut self, _machine: &mut Mac) -> Result<(), VMError> {
         Ok(())
     }
```
