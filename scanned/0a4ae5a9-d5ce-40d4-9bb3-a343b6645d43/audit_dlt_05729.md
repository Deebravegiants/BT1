# [?] fix(usability): Improve the cache dir and database startup panics (#9441)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-05-06
Source: https://github.com/ZcashFoundation/zebra/commit/ee65be98c50336645ad8af4a857dbb9ab8ef35e1
Type: security-commit

## Details
fix(usability): Improve the cache dir and database startup panics (#9441)

* improve cache dir database panics

* Apply suggestions from code review

Co-authored-by: Arya <aryasolhi@gmail.com>

* fix build

---------

Co-authored-by: Arya <aryasolhi@gmail.com>

## Patch
### zebra-state/src/constants.rs
```diff
@@ -118,5 +118,5 @@ pub const MAX_INVALIDATED_BLOCKS: usize = 100;
 
 lazy_static! {
     /// Regex that matches the RocksDB error when its lock file is already open.
-    pub static ref LOCK_FILE_ERROR: Regex = Regex::new("(lock file).*(temporarily unavailable)|(in use)|(being used by another process)").expect("regex is valid");
+    pub static ref LOCK_FILE_ERROR: Regex = Regex::new("(lock file).*(temporarily unavailable)|(in use)|(being used by another process)|(Database likely already open)").expect("regex is valid");
 }
```

### zebra-state/src/service/finalized_state/disk_db.rs
```diff
@@ -22,7 +22,7 @@ use std::{
 use itertools::Itertools;
 use rlimit::increase_nofile_limit;
 
-use rocksdb::{ColumnFamilyDescriptor, Options, ReadOptions};
+use rocksdb::{ColumnFamilyDescriptor, ErrorKind, Options, ReadOptions};
 use semver::Version;
 use zebra_chain::{parameters::Network, primitives::byte_array::increment_big_endian};
 
@@ -833,6 +833,11 @@ impl DiskDb {
     /// Opens or creates the database at a path based on the kind, major version and network,
     /// with the supplied column families, preserving any existing column families,
     /// and returns a shared low-level database wrapper.
+    ///
+    /// # Panics
+    ///
+    /// - If the cache directory does not exist and can't be created.
+    /// - If the database cannot be opened for whatever reason.
     pub fn new(
         config: &Config,
         db_kind: impl AsRef<str>,
@@ -841,6 +846,11 @@ impl DiskDb {
         column_families_in_code: impl IntoIterator<Item = String>,
         read_only: bool,
     ) -> DiskDb {
+        // If the database is ephemeral, we don't need to check the cache directory.
+        if !config.ephemeral {
+            DiskDb::validate_cache_dir(&config.cache_dir);
+        }
+
         let db_kind = db_kind.as_ref();
         let path = config.db_path(db_kind, format_version_in_code.major, network);
 
@@ -901,11 +911,15 @@ impl DiskDb {
                 db
             }
 
-            // TODO: provide a different hint if the disk is full, see #1623
+            Err(e) if matches!(e.kind(), ErrorKind::Busy | ErrorKind::IOError) => panic!(
+                "Database likely already open {path:?} \
+                         Hint: Check if another zebrad process is running."
+            ),
+
             Err(e) => panic!(
-                "Opening database {path:?} failed: {e:?}. \
-                 Hint: Check if another zebrad process is running. \
-                 Try changing the state cache_dir in the Zebra config.",
+                "Opening database {path:?} failed. \
+                        Hint: Try changing the state cache_dir in the Zebra config. \
+                        Error: {e}",
             ),
         }
     }
@@ -1515,6 +1529,24 @@ impl DiskDb {
             );
         }
     }
+
+    // Validates a cache directory and creates it if it doesn't exist.
+    // If the directory cannot be created, it panics with a specific error message.
+    fn validate_cache_dir(cache_dir: &std::path::PathBuf) {
+        if let Err(e) = fs::create_dir_all(cache_dir) {
+            match e.kind() {
+                std::io::ErrorKind::PermissionDenied => panic!(
+                    "Permission denied creating {cache_dir:?}. \
+                     Hint: check if cache directory exist and has write permissions."
+                ),
+                std::io::ErrorKind::StorageFull => panic!(
+                    "No space left on device creating {cache_dir:?}. \
+                     Hint: check if the disk is full."
+                ),
+                _ => panic!("Could not create cache dir {:?}: {}", cache_dir, e),
+            }
+        }
+    }
 }
 
 impl Drop for DiskDb {
```
