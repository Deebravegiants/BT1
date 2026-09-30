# [?] fix(db): Fix a sprout/history tree read panic in Zebra 1.4.0, which only happens before the 25.3.0 state upgrade completes (#7972)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-11-22
Source: https://github.com/ZcashFoundation/zebra/commit/d20ec3940e2fabae75189976cfd9aafe279e34f0
Type: security-commit

## Details
fix(db): Fix a sprout/history tree read panic in Zebra 1.4.0, which only happens before the 25.3.0 state upgrade completes (#7972)

* Avoid a race condition in the 25.3.0 state upgrade

* Look for the most recent sprout tree height if needed

* Get the latest history tree not the tip height history tree

* Discard keys provided by low level database method

* Remove extra ;

* Provide key types & rustfmt

* Fix weird closure type syntax

* Update zebra-state/src/service/finalized_state/disk_format/upgrade/fix_tree_key_type.rs

Co-authored-by: Marek <mail@marek.onl>

---------

Co-authored-by: Marek <mail@marek.onl>

## Patch
### zebra-state/src/service/finalized_state/disk_format/upgrade/fix_tree_key_type.rs
```diff
@@ -28,11 +28,6 @@ pub fn run(
     // Writing the trees back to the database automatically updates their format.
     let mut batch = DiskWriteBatch::new();
 
-    // Delete the previous `Height` tip key format, which is now a duplicate.
-    // It's ok to do a full delete, because the trees are restored before the batch is written.
-    batch.delete_range_sprout_tree(upgrade_db, &Height(0), &MAX_ON_DISK_HEIGHT);
-    batch.delete_range_history_tree(upgrade_db, &Height(0), &MAX_ON_DISK_HEIGHT);
-
     // Update the sprout tip key format in the database.
     batch.update_sprout_tree(upgrade_db, &sprout_tip_tree);
     batch.update_history_tree(upgrade_db, &history_tip_tree);
@@ -46,6 +41,24 @@ pub fn run(
         .write_batch(batch)
         .expect("updating tree key formats should always succeed");
 
+    // The deletes below can be slow due to tombstones for previously deleted keys,
+    // so we do it in a separate batch to avoid data races with syncing (#7961).
+    let mut batch = DiskWriteBatch::new();
+
+    // Delete the previous `Height` tip key format, which is now a duplicate.
+    // This doesn't delete the new `()` key format, because it serializes to an empty array.
+    batch.delete_range_sprout_tree(upgrade_db, &Height(0), &MAX_ON_DISK_HEIGHT);
+    batch.delete_range_history_tree(upgrade_db, &Height(0), &MAX_ON_DISK_HEIGHT);
+
+    // Return before we write if the upgrade is cancelled.
+    if !matches!(cancel_receiver.try_recv(), Err(mpsc::TryRecvError::Empty)) {
+        return Err(CancelFormatChange);
+    }
+
+    upgrade_db
+        .write_batch(batch)
+        .expect("cleaning up old tree key formats should always succeed");
+
     Ok(())
 }
 
```

### zebra-state/src/service/finalized_state/zebra_db/chain.rs
```diff
@@ -59,11 +59,13 @@ impl ZebraDb {
         let mut history_tree: Option<Arc<HistoryTree>> = self.db.zs_get(&history_tree_cf, &());
 
         if history_tree.is_none() {
-            let tip_height = self
-                .finalized_tip_height()
-                .expect("just checked for an empty database");
-
-            history_tree = self.db.zs_get(&history_tree_cf, &tip_height);
+            // In Zebra 1.4.0 and later, we only update the history tip tree when it has changed (for every block after heartwood).
+            // But we write with a `()` key, not a height key.
+            // So we need to look for the most recent update height if the `()` key has never been written.
+            history_tree = self
+                .db
+                .zs_last_key_value(&history_tree_cf)
+                .map(|(_key, tree_value): (Height, _)| tree_value);
         }
 
         history_tree.unwrap_or_default()
```

### zebra-state/src/service/finalized_state/zebra_db/shielded.rs
```diff
@@ -109,11 +109,13 @@ impl ZebraDb {
             self.db.zs_get(&sprout_tree_cf, &());
 
         if sprout_tree.is_none() {
-            let tip_height = self
-                .finalized_tip_height()
-                .expect("just checked for an empty database");
-
-            sprout_tree = self.db.zs_get(&sprout_tree_cf, &tip_height);
+            // In Zebra 1.4.0 and later, we don't update the sprout tip tree unless it is changed.
+            // And we write with a `()` key, not a height key.
+            // So we need to look for the most recent update height if the `()` key has never been written.
+            sprout_tree = self
+                .db
+                .zs_last_key_value(&sprout_tree_cf)
+                .map(|(_key, tree_value): (Height, _)| tree_value);
         }
 
         sprout_tree.expect("Sprout note commitment tree must exist if there is a finalized tip")
```
