# [?] fix: storage lock race condition (#17823)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-08-12
Source: https://github.com/paradigmxyz/reth/commit/772d92056da6ddb40a0ed86f18aeea7aed06d1f6
Type: security-commit

## Details
fix: storage lock race condition (#17823)

## Patch
### crates/storage/db/src/lockfile.rs
```diff
@@ -61,16 +61,32 @@ impl StorageLock {
     }
 }
 
-impl Drop for StorageLock {
+impl Drop for StorageLockInner {
     fn drop(&mut self) {
         // The lockfile is not created in disable-lock mode, so we don't need to delete it.
         #[cfg(any(test, not(feature = "disable-lock")))]
-        if Arc::strong_count(&self.0) == 1 && self.0.file_path.exists() {
-            // TODO: should only happen during tests that the file does not exist: tempdir is
-            // getting dropped first. However, tempdir shouldn't be dropped
-            // before any of the storage providers.
-            if let Err(err) = reth_fs_util::remove_file(&self.0.file_path) {
-                reth_tracing::tracing::error!(%err, "Failed to delete lock file");
+        {
+            let file_path = &self.file_path;
+            if file_path.exists() {
+                if let Ok(Some(process_uid)) = ProcessUID::parse(file_path) {
+                    // Only remove if the lock file belongs to our process
+                    if process_uid.pid == process::id() as usize {
+                        if let Err(err) = reth_fs_util::remove_file(file_path) {
+                            reth_tracing::tracing::error!(%err, "Failed to delete lock file");
+                        }
+                    } else {
+                        reth_tracing::tracing::warn!(
+                            "Lock file belongs to different process (PID: {}), not removing",
+                            process_uid.pid
+                        );
+                    }
+                } else {
+                    // If we can't parse the lock file, still try to remove it
+                    // as it might be corrupted or from a previous run
+                    if let Err(err) = reth_fs_util::remove_file(file_path) {
+                        reth_tracing::tracing::error!(%err, "Failed to delete lock file");
+                    }
+                }
             }
         }
     }
```
