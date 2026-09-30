# [?] apollo_class_manager: recover orphaned class dir to avoid ENOTEMPTY sync deadlock (#14666) (#14750)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-07-12
Source: https://github.com/starkware-libs/sequencer/commit/2e80dff5c87918fd11f3d36fc56e96ce8081ae87
Type: security-commit

## Details
apollo_class_manager: recover orphaned class dir to avoid ENOTEMPTY sync deadlock (#14666) (#14750)

A crash between renaming the staged class directory into place and committing
the existence marker leaves an orphaned, non-empty persistent directory. On the
next attempt std::fs::rename fails with ENOTEMPTY, which permanently wedges sync
on that class. Remove a pre-existing persistent directory before the rename so
the write self-heals; the directory is content-addressed by class hash, so it
holds the same class. Covers both the regular and deprecated class write paths.


(cherry picked from commit 7b2c35ed5a5aadd9f4128aa2266a71a9ac8242f7)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/apollo_class_manager/src/class_storage.rs
```diff
@@ -24,7 +24,7 @@ use apollo_storage::StorageConfig;
 use starknet_api::class_cache::GlobalContractCache;
 use thiserror::Error;
 use tokio::task::AbortHandle;
-use tracing::instrument;
+use tracing::{instrument, warn};
 
 use crate::metrics::{increment_n_classes, record_class_size, CairoClassType, ClassObjectType};
 
@@ -459,11 +459,7 @@ impl FsClassStorage {
         class.write_to_file(concat_sierra_filename(&tmp_dir))?;
         executable_class.write_to_file(concat_executable_filename(&tmp_dir))?;
 
-        // Atomically rename directory to persistent one.
-        let persistent_dir = self.get_persistent_dir_with_create(class_id)?;
-        std::fs::rename(tmp_dir, persistent_dir)?;
-
-        Ok(())
+        self.rename_to_persistent_dir(tmp_dir, class_id)
     }
 
     fn write_deprecated_class_atomically(
@@ -475,8 +471,29 @@ impl FsClassStorage {
         let (_tmp_root, tmp_dir) = self.create_tmp_dir(class_id)?;
         class.write_to_file(concat_deprecated_executable_filename(&tmp_dir))?;
 
-        // Atomically rename directory to persistent one.
+        self.rename_to_persistent_dir(tmp_dir, class_id)
+    }
+
+    /// Atomically moves the staged class directory `tmp_dir` into its content-addressed persistent
+    /// directory.
+    ///
+    /// Recovers from a previous partial write: a crash between this rename and committing the
+    /// existence marker (see `FsClassStorage::set_class`) can leave an orphaned, non-empty
+    /// persistent directory. `std::fs::rename` refuses to replace a non-empty directory and fails
+    /// with `ENOTEMPTY`, which permanently wedges sync on the class. Callers reach this only when
+    /// the existence marker is absent, and the directory is named by the class hash, so an existing
+    /// directory holds the same class; removing it lets the rename proceed and the marker get
+    /// written, restoring filesystem/marker consistency.
+    fn rename_to_persistent_dir(
+        &self,
+        tmp_dir: PathBuf,
+        class_id: ClassId,
+    ) -> FsClassStorageResult<()> {
         let persistent_dir = self.get_persistent_dir_with_create(class_id)?;
+        if persistent_dir.exists() {
+            warn!("Recovering orphaned class dir from a prior partial write: {persistent_dir:?}");
+            std::fs::remove_dir_all(&persistent_dir)?;
+        }
         std::fs::rename(tmp_dir, persistent_dir)?;
 
         Ok(())
```

### crates/apollo_class_manager/src/class_storage_test.rs
```diff
@@ -189,6 +189,64 @@ async fn fs_storage_partial_write_no_atomic_marker() {
     assert_eq!(storage.get_executable(class_id), Ok(None));
 }
 
+/// Reproduces the production sync deadlock: a crash between writing the class files and committing
+/// the existence marker leaves an orphaned, non-empty persistent directory. Re-running `set_class`
+/// must recover and complete the write; previously `std::fs::rename` failed with ENOTEMPTY and
+/// wedged sync on the class forever.
+#[tokio::test]
+async fn set_class_recovers_from_orphaned_class_dir() {
+    let persistent_root = tempfile::tempdir().unwrap();
+    let class_hash_storage_path_prefix = tempfile::tempdir().unwrap();
+    let mut storage =
+        FsClassStorage::new_for_testing(&persistent_root, &class_hash_storage_path_prefix);
+
+    let class_id = ClassHash(felt!("0x1234"));
+    let class = RawClass::try_from(SierraContractClass::default()).unwrap();
+    let executable_class = RawExecutableClass::test_casm_contract_class();
+    let executable_class_hash_v2 = CompiledClassHash(felt!("0x5678"));
+
+    // Simulate a partial write: class files are on disk, but the existence marker was never
+    // committed (the process crashed in between).
+    storage.write_class_atomically(class_id, class.clone(), executable_class.clone()).unwrap();
+    assert_eq!(storage.get_executable_class_hash_v2(class_id), Ok(None));
+    assert!(storage.get_persistent_dir(class_id).join("sierra").exists());
+
+    // `set_class` must recover the orphaned directory and complete the write.
+    storage
+        .set_class(class_id, class.clone(), executable_class_hash_v2, executable_class.clone())
+        .unwrap();
+
+    // The class is now fully readable and marked as existent.
+    assert_eq!(storage.get_sierra(class_id).unwrap(), Some(class));
+    assert_eq!(storage.get_executable(class_id).unwrap(), Some(executable_class));
+    assert_eq!(storage.get_executable_class_hash_v2(class_id), Ok(Some(executable_class_hash_v2)));
+}
+
+/// As above, for the deprecated-class write path: an orphaned, non-empty directory at the class's
+/// persistent path must not permanently block `set_deprecated_class` with ENOTEMPTY.
+#[tokio::test]
+async fn set_deprecated_class_recovers_from_orphaned_class_dir() {
+    let persistent_root = tempfile::tempdir().unwrap();
+    let class_hash_storage_path_prefix = tempfile::tempdir().unwrap();
+    let mut storage =
+        FsClassStorage::new_for_testing(&persistent_root, &class_hash_storage_path_prefix);
+
+    let class_id = ClassHash(felt!("0x1234"));
+    let executable_class = RawExecutableClass::test_casm_contract_class();
+
+    // Simulate a leftover, non-empty persistent directory without the deprecated-class file, so the
+    // class is still considered absent.
+    let persistent_dir = storage.get_persistent_dir(class_id);
+    std::fs::create_dir_all(&persistent_dir).unwrap();
+    std::fs::write(persistent_dir.join("stale"), b"leftover").unwrap();
+    assert!(!storage.contains_deprecated_class(class_id));
+
+    // `set_deprecated_class` must recover the orphaned directory and complete the write.
+    storage.set_deprecated_class(class_id, executable_class.clone()).unwrap();
+
+    assert_eq!(storage.get_deprecated_class(class_id).unwrap(), Some(executable_class));
+}
+
 #[tokio::test]
 async fn cached_storage_none_flows_do_not_cache() {
     let persistent_root = tempfile::tempdir().unwrap();
```
