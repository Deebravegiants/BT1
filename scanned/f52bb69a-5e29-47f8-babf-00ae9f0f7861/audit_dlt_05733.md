# [?] fix(state): Avoid panics and history tree consensus database concurrency bugs  (#7590)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-09-20
Source: https://github.com/ZcashFoundation/zebra/commit/2dce6862a056957b5093f3659d46e4ce09e69978
Type: security-commit

## Details
fix(state): Avoid panics and history tree consensus database concurrency bugs  (#7590)

* Add a RawBytes database serialization type

* Fix a history tree database concurrency bug

* Fix a sprout tree concurrency panic

## Patch
### zebra-state/src/service/finalized_state/disk_format.rs
```diff
@@ -110,6 +110,44 @@ impl FromDisk for () {
     }
 }
 
+/// Access database keys or values as raw bytes.
+/// Mainly for use in tests, runtime checks, or format compatibility code.
+#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd)]
+pub struct RawBytes(Vec<u8>);
+
+// Note: don't implement From or Into for RawBytes, because it makes it harder to spot in reviews.
+// Instead, implement IntoDisk and FromDisk on the original type, or a specific wrapper type.
+
+impl RawBytes {
+    /// Create a new raw byte key or data.
+    ///
+    /// Mainly for use in tests or runtime checks.
+    /// These methods
+    pub fn new_raw_bytes(bytes: Vec<u8>) -> Self {
+        Self(bytes)
+    }
+
+    /// Create a new raw byte key or data.
+    /// Mainly for use in tests.
+    pub fn raw_bytes(&self) -> &Vec<u8> {
+        &self.0
+    }
+}
+
+impl IntoDisk for RawBytes {
+    type Bytes = Vec<u8>;
+
+    fn as_bytes(&self) -> Self::Bytes {
+        self.raw_bytes().clone()
+    }
+}
+
+impl FromDisk for RawBytes {
+    fn from_bytes(bytes: impl AsRef<[u8]>) -> Self {
+        Self::new_raw_bytes(bytes.as_ref().to_vec())
+    }
+}
+
 // Serialization Modification Functions
 
 /// Truncates `mem_bytes` to `disk_len`, by removing zero bytes from the start of the slice.
```

### zebra-state/src/service/finalized_state/zebra_db/chain.rs
```diff
@@ -24,6 +24,7 @@ use crate::{
     request::SemanticallyVerifiedBlockWithTrees,
     service::finalized_state::{
         disk_db::{DiskDb, DiskWriteBatch, ReadDisk, WriteDisk},
+        disk_format::RawBytes,
         zebra_db::ZebraDb,
     },
     BoxError, SemanticallyVerifiedBlock,
@@ -33,11 +34,32 @@ impl ZebraDb {
     /// Returns the ZIP-221 history tree of the finalized tip or `None`
     /// if it does not exist yet in the state (pre-Heartwood).
     pub fn history_tree(&self) -> Arc<HistoryTree> {
-        if let Some(height) = self.finalized_tip_height() {
+        if self.finalized_tip_height().is_some() {
             let history_tree_cf = self.db.cf_handle("history_tree").unwrap();
 
-            let history_tree: Option<NonEmptyHistoryTree> =
-                self.db.zs_get(&history_tree_cf, &height);
+            // # Concurrency
+            //
+            // There is only one tree in this column family, which is atomically updated by a block
+            // write batch (database transaction). If this update runs between the height read and
+            // the tree read, the height will be wrong, and the tree will be missing.
+            // That could cause consensus bugs.
+            //
+            // Instead, always read the last tree in the column family, regardless of height.
+            //
+            // See ticket #7581 for more details.
+            //
+            // TODO: this concurrency bug will be permanently fixed in PR #7392,
+            //       by changing the block update to overwrite the tree, rather than deleting it.
+            //
+            // # Forwards Compatibility
+            //
+            // This code can read the column family format in 1.2.0 and earlier (tip height key),
+            // and after PR #7392 is merged (empty key).
+            let history_tree: Option<NonEmptyHistoryTree> = self
+                .db
+                .zs_last_key_value(&history_tree_cf)
+                // RawBytes will deserialize both Height and `()` (empty) keys.
+                .map(|(_key, value): (RawBytes, _)| value);
 
             if let Some(non_empty_tree) = history_tree {
                 return Arc::new(HistoryTree::from(non_empty_tree));
```

### zebra-state/src/service/finalized_state/zebra_db/shielded.rs
```diff
@@ -30,6 +30,7 @@ use crate::{
     request::SemanticallyVerifiedBlockWithTrees,
     service::finalized_state::{
         disk_db::{DiskDb, DiskWriteBatch, ReadDisk, WriteDisk},
+        disk_format::RawBytes,
         zebra_db::ZebraDb,
     },
     BoxError, SemanticallyVerifiedBlock,
@@ -84,16 +85,33 @@ impl ZebraDb {
     /// Returns the Sprout note commitment tree of the finalized tip
     /// or the empty tree if the state is empty.
     pub fn sprout_tree(&self) -> Arc<sprout::tree::NoteCommitmentTree> {
-        let height = match self.finalized_tip_height() {
-            Some(h) => h,
-            None => return Default::default(),
-        };
+        if self.finalized_tip_height().is_none() {
+            return Default::default();
+        }
 
         let sprout_nct_handle = self.db.cf_handle("sprout_note_commitment_tree").unwrap();
 
+        // # Concurrency
+        //
+        // There is only one tree in this column family, which is atomically updated by a block
+        // write batch (database transaction). If this update runs between the height read and the
+        // tree read, the height will be wrong, and the tree will be missing.
+        //
+        // Instead, always read the last tree in the column family, regardless of height.
+        //
+        // See ticket #7581 for more details.
+        //
+        // TODO: this concurrency bug will be permanently fixed in PR #7392,
+        //       by changing the block update to overwrite the tree, rather than deleting it.
+        //
+        // # Forwards Compatibility
+        //
+        // This code can read the column family format in 1.2.0 and earlier (tip height key),
+        // and after PR #7392 is merged (empty key).
         self.db
-            .zs_get(&sprout_nct_handle, &height)
-            .map(Arc::new)
+            .zs_last_key_value(&sprout_nct_handle)
+            // RawBytes will deserialize both Height and `()` (empty) keys.
+            .map(|(_key, value): (RawBytes, _)| Arc::new(value))
             .expect("Sprout note commitment tree must exist if there is a finalized tip")
     }
 
```
