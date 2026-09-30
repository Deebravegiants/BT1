# [?] Hotfix: prevent node crashes when restarting (#1172)

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2023-11-22
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/0d0284427314f424a9a98f242ab8805f35a7c655
Type: security-commit

## Details
Hotfix: prevent node crashes when restarting (#1172)

* Make state db update atomic

* Hotfix; use big-endian encoding for jmtnode versions

## Patch
### Cargo.lock
```diff
@@ -3952,15 +3952,15 @@ dependencies = [
 
 [[package]]
 name = "ics23"
-version = "0.10.2"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "442d4bab37956e76f739c864f246c825d87c0bb7f9afa65660c57833c91bf6d4"
+checksum = "661e2d6f79952a65bc92b1c81f639ebd37228dae6ff412a5aba7d474bdc4b957"
 dependencies = [
  "anyhow",
  "bytes",
  "hex",
  "informalsystems-pbjson",
- "prost 0.11.9",
+ "prost 0.12.2",
  "ripemd",
  "serde",
  "sha2 0.10.8",
@@ -4321,9 +4321,8 @@ checksum = "af150ab688ff2122fcef229be89cb50dd66af9e01a4ff320cc137eecc9bacc38"
 
 [[package]]
 name = "jmt"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "23f1cb339f7d5288603665c0ccbef7ad33a782ced36e18b6b207f175479eb3b7"
+version = "0.9.0"
+source = "git+https://github.com/penumbra-zone/jmt.git?rev=1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6#1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6"
 dependencies = [
  "anyhow",
  "borsh",
```

### Cargo.toml
```diff
@@ -60,7 +60,8 @@ repository = "https://github.com/sovereign-labs/sovereign-sdk"
 
 [workspace.dependencies]
 # Dependencies maintained by Sovereign
-jmt = "0.8.0"
+jmt = { git = "https://github.com/penumbra-zone/jmt.git", rev = "1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6" }
+
 
 # External dependencies
 async-trait = "0.1.71"
```

### examples/demo-rollup/provers/risc0/guest-celestia/Cargo.lock
```diff
@@ -421,7 +421,7 @@ version = "0.1.0"
 source = "git+https://github.com/eigerco/celestia-node-rs.git?rev=66b7c6c#66b7c6cd58213c0cbf79207ba549cef82764ddca"
 dependencies = [
  "anyhow",
- "prost 0.12.1",
+ "prost",
  "prost-build",
  "prost-types",
  "serde",
@@ -992,15 +992,15 @@ dependencies = [
 
 [[package]]
 name = "ics23"
-version = "0.10.2"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "442d4bab37956e76f739c864f246c825d87c0bb7f9afa65660c57833c91bf6d4"
+checksum = "661e2d6f79952a65bc92b1c81f639ebd37228dae6ff412a5aba7d474bdc4b957"
 dependencies = [
  "anyhow",
  "bytes",
  "hex",
  "informalsystems-pbjson",
- "prost 0.11.9",
+ "prost",
  "ripemd",
  "serde",
  "sha2 0.10.8",
@@ -1091,9 +1091,8 @@ checksum = "af150ab688ff2122fcef229be89cb50dd66af9e01a4ff320cc137eecc9bacc38"
 
 [[package]]
 name = "jmt"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "23f1cb339f7d5288603665c0ccbef7ad33a782ced36e18b6b207f175479eb3b7"
+version = "0.9.0"
+source = "git+https://github.com/penumbra-zone/jmt.git?rev=1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6#1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6"
 dependencies = [
  "anyhow",
  "borsh",
@@ -1469,24 +1468,14 @@ dependencies = [
  "unarray",
 ]
 
-[[package]]
-name = "prost"
-version = "0.11.9"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0b82eaa1d779e9a4bc1c3217db8ffbeabaae1dca241bf70183242128d48681cd"
-dependencies = [
- "bytes",
- "prost-derive 0.11.9",
-]
-
 [[package]]
 name = "prost"
 version = "0.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "f4fdd22f3b9c31b53c060df4a0613a1c7f062d4115a2b984dd15b1858f7e340d"
 dependencies = [
  "bytes",
- "prost-derive 0.12.1",
+ "prost-derive",
 ]
 
 [[package]]
@@ -1503,27 +1492,14 @@ dependencies = [
  "once_cell",
  "petgraph",
  "prettyplease",
- "prost 0.12.1",
+ "prost",
  "prost-types",
  "regex",
  "syn 2.0.38",
  "tempfile",
  "which",
 ]
 
-[[package]]
-name = "prost-derive"
-version = "0.11.9"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e5d2d8d10f3c6ded6da8b05b5fb3b8a5082514344d56c9f871412d29b4e075b4"
-dependencies = [
- "anyhow",
- "itertools 0.10.5",
- "proc-macro2",
- "quote",
- "syn 1.0.109",
-]
-
 [[package]]
 name = "prost-derive"
 version = "0.12.1"
@@ -1543,7 +1519,7 @@ version = "0.12.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "e081b29f63d83a4bc75cfc9f3fe424f9156cf92d8a4f0c9407cce9a1b67327cf"
 dependencies = [
- "prost 0.12.1",
+ "prost",
 ]
 
 [[package]]
@@ -2054,7 +2030,7 @@ dependencies = [
  "celestia-types",
  "hex",
  "nmt-rs",
- "prost 0.12.1",
+ "prost",
  "risc0-zkvm",
  "risc0-zkvm-platform",
  "serde",
@@ -2396,7 +2372,7 @@ dependencies = [
  "instant",
  "num-traits",
  "once_cell",
- "prost 0.12.1",
+ "prost",
  "prost-types",
  "serde",
  "serde_bytes",
@@ -2420,7 +2396,7 @@ dependencies = [
  "flex-error",
  "num-derive 0.3.3",
  "num-traits",
- "prost 0.12.1",
+ "prost",
  "prost-types",
  "serde",
  "serde_bytes",
```

### examples/demo-rollup/provers/risc0/guest-mock/Cargo.lock
```diff
@@ -410,9 +410,9 @@ dependencies = [
 
 [[package]]
 name = "ics23"
-version = "0.10.2"
+version = "0.11.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "442d4bab37956e76f739c864f246c825d87c0bb7f9afa65660c57833c91bf6d4"
+checksum = "661e2d6f79952a65bc92b1c81f639ebd37228dae6ff412a5aba7d474bdc4b957"
 dependencies = [
  "anyhow",
  "bytes",
@@ -452,9 +452,8 @@ checksum = "af150ab688ff2122fcef229be89cb50dd66af9e01a4ff320cc137eecc9bacc38"
 
 [[package]]
 name = "jmt"
-version = "0.8.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "23f1cb339f7d5288603665c0ccbef7ad33a782ced36e18b6b207f175479eb3b7"
+version = "0.9.0"
+source = "git+https://github.com/penumbra-zone/jmt.git?rev=1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6#1d007e11cb68aa5ca13e9a5af4a12e6439d5f7b6"
 dependencies = [
  "anyhow",
  "borsh",
@@ -619,25 +618,25 @@ dependencies = [
 
 [[package]]
 name = "prost"
-version = "0.11.9"
+version = "0.12.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0b82eaa1d779e9a4bc1c3217db8ffbeabaae1dca241bf70183242128d48681cd"
+checksum = "146c289cda302b98a28d40c8b3b90498d6e526dd24ac2ecea73e4e491685b94a"
 dependencies = [
  "bytes",
  "prost-derive",
 ]
 
 [[package]]
 name = "prost-derive"
-version = "0.11.9"
+version = "0.12.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e5d2d8d10f3c6ded6da8b05b5fb3b8a5082514344d56c9f871412d29b4e075b4"
+checksum = "efb6c9a1dd1def8e2124d17e83a20af56f1570d6c2d2bd9e266ccb768df3840e"
 dependencies = [
  "anyhow",
  "itertools",
  "proc-macro2",
  "quote",
- "syn 1.0.109",
+ "syn 2.0.38",
 ]
 
 [[package]]
```

### full-node/db/sov-db/src/schema/tables.rs
```diff
@@ -27,7 +27,7 @@
 
 use borsh::{maybestd, BorshDeserialize, BorshSerialize};
 use byteorder::{BigEndian, ReadBytesExt, WriteBytesExt};
-use jmt::storage::{Node, NodeKey};
+use jmt::storage::{NibblePath, Node, NodeKey};
 use jmt::Version;
 use sov_rollup_interface::stf::{Event, EventKey};
 use sov_schema_db::schema::{KeyDecoder, KeyEncoder, ValueCodec};
@@ -261,12 +261,28 @@ define_table_without_codec!(
 
 impl KeyEncoder<JmtNodes> for NodeKey {
     fn encode_key(&self) -> sov_schema_db::schema::Result<Vec<u8>> {
-        self.try_to_vec().map_err(CodecError::from)
+        // 8 bytes for version, 4 each for the num_nibbles and bytes.len() fields, plus 1 byte per byte of nibllepath
+        let mut output =
+            Vec::with_capacity(8 + 4 + 4 + ((self.nibble_path().num_nibbles() + 1) / 2));
+        let version = self.version().to_be_bytes();
+        output.extend_from_slice(&version);
+        self.nibble_path().serialize(&mut output)?;
+        Ok(output)
     }
 }
 impl KeyDecoder<JmtNodes> for NodeKey {
     fn decode_key(data: &[u8]) -> sov_schema_db::schema::Result<Self> {
-        Ok(Self::deserialize_reader(&mut &data[..])?)
+        if data.len() < 8 {
+            return Err(CodecError::InvalidKeyLength {
+                expected: 9,
+                got: data.len(),
+            });
+        }
+        let mut version = [0u8; 8];
+        version.copy_from_slice(&data[..8]);
+        let version = u64::from_be_bytes(version);
+        let nibble_path = NibblePath::deserialize_reader(&mut &data[8..])?;
+        Ok(Self::new(version, nibble_path))
     }
 }
 
```

### full-node/db/sov-db/src/state_db.rs
```diff
@@ -3,7 +3,7 @@ use std::sync::{Arc, Mutex};
 
 use jmt::storage::{TreeReader, TreeWriter};
 use jmt::{KeyHash, Version};
-use sov_schema_db::DB;
+use sov_schema_db::{SchemaBatch, DB};
 
 use crate::rocks_db_config::gen_rocksdb_options;
 use crate::schema::tables::{JmtNodes, JmtValues, KeyHashToKey, STATE_TABLES};
@@ -46,8 +46,15 @@ impl StateDB {
 
     /// Put the preimage of a hashed key into the database. Note that the preimage is not checked for correctness,
     /// since the DB is unaware of the hash function used by the JMT.
-    pub fn put_preimage(&self, key_hash: KeyHash, key: &Vec<u8>) -> Result<(), anyhow::Error> {
-        self.db.put::<KeyHashToKey>(&key_hash.0, key)
+    pub fn put_preimages<'a>(
+        &self,
+        items: impl IntoIterator<Item = (KeyHash, &'a Vec<u8>)>,
+    ) -> Result<(), anyhow::Error> {
+        let mut batch = SchemaBatch::new();
+        for (key_hash, key) in items.into_iter() {
+            batch.put::<KeyHashToKey>(&key_hash.0, key)?;
+        }
+        self.db.write_schemas(batch)
     }
 
     /// Get an optional value from the database, given a version and a key hash.
@@ -87,11 +94,11 @@ impl StateDB {
     }
 
     fn last_version_written(db: &DB) -> anyhow::Result<Option<Version>> {
-        let mut iter = db.iter::<JmtValues>()?;
+        let mut iter = db.iter::<JmtNodes>()?;
         iter.seek_to_last();
 
         let version = match iter.next() {
-            Some(Ok(((_, version), _))) => Some(version),
+            Some(Ok((key, _))) => Some(key.version()),
             _ => None,
         };
         Ok(version)
@@ -127,8 +134,9 @@ impl TreeReader for StateDB {
 
 impl TreeWriter for StateDB {
     fn write_node_batch(&self, node_batch: &jmt::storage::NodeBatch) -> anyhow::Result<()> {
+        let mut batch = SchemaBatch::new();
         for (node_key, node) in node_batch.nodes() {
-            self.db.put::<JmtNodes>(node_key, node)?;
+            batch.put::<JmtNodes>(node_key, node)?;
         }
 
         for ((version, key_hash), value) in node_batch.values() {
@@ -138,8 +146,9 @@ impl TreeWriter for StateDB {
                     .ok_or(anyhow::format_err!(
                         "Could not find preimage for key hash {key_hash:?}. Has `StateDB::put_preimage` been called for this key?"
                     ))?;
-            self.db.put::<JmtValues>(&(key_preimage, *version), value)?;
+            batch.put::<JmtValues>(&(key_preimage, *version), value)?;
         }
+        self.db.write_schemas(batch)?;
         Ok(())
     }
 }
@@ -236,7 +245,7 @@ mod state_db_tests {
         let key = vec![2u8; 100];
         let value = [8u8; 150];
 
-        db.put_preimage(key_hash, &key).unwrap();
+        db.put_preimages(vec![(key_hash, &key)]).unwrap();
         let mut batch = NodeBatch::default();
         batch.extend(vec![], vec![((0, key_hash), Some(value.to_vec()))]);
         db.write_node_batch(&batch).unwrap();
```

### module-system/sov-state/src/prover_storage.rs
```diff
@@ -167,16 +167,14 @@ impl<S: MerkleProofSpec> Storage for ProverStorage<S> {
     }
 
     fn commit(&self, state_update: &Self::StateUpdate, accessory_writes: &OrderedReadsAndWrites) {
-        for (key_hash, key) in state_update.key_preimages.iter() {
-            // Clone should be cheap
-            self.db
-                .put_preimage(*key_hash, key.key.as_ref())
-                .expect("preimage must succeed");
-        }
-
         self.db
-            .write_node_batch(&state_update.node_batch)
-            .expect("db write must succeed");
+            .put_preimages(
+                state_update
+                    .key_preimages
+                    .iter()
+                    .map(|(key_hash, key)| (*key_hash, key.key.as_ref())),
+            )
+            .expect("Preimage put must succeed");
 
         self.native_db
             .set_values(
@@ -187,6 +185,14 @@ impl<S: MerkleProofSpec> Storage for ProverStorage<S> {
             )
             .expect("native db write must succeed");
 
+        // Write the state values last, since we base our view of what has been touched
+        // on state. If the node crashes between the `native_db` update and this update,
+        // then the whole `commit` will be re-run later so no data can be lost.
+        self.db
+            .write_node_batch(&state_update.node_batch)
+            .expect("db write must succeed");
+
+        // Finally, update our in-memory view of the current item numbers
         self.db.inc_next_version();
     }
 
```
