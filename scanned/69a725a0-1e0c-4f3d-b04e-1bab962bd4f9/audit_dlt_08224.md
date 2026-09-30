# [?] Fix startup panic if removing accounts directory fails (#27386)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-08-26
Source: https://github.com/solana-labs/solana/commit/5eefc256d68366dfbd055283fb0834190468519c
Type: security-commit

## Details
Fix startup panic if removing accounts directory fails (#27386)

* Remove contents of accounts directory if deleting the directory fails.

## Patch
### core/src/validator.rs
```diff
@@ -2076,7 +2076,7 @@ fn move_and_async_delete_path(path: impl AsRef<Path> + Copy) {
             "Path renaming failed: {}.  Falling back to rm_dir in sync mode",
             err.to_string()
         );
-        std::fs::remove_dir_all(&path).unwrap();
+        delete_contents_of_path(path);
         return;
     }
 
@@ -2088,6 +2088,51 @@ fn move_and_async_delete_path(path: impl AsRef<Path> + Copy) {
         .unwrap();
 }
 
+/// Delete the files and subdirectories in a directory.
+/// This is useful if the process does not have permission
+/// to delete the top level directory it might be able to
+/// delete the contents of that directory.
+fn delete_contents_of_path(path: impl AsRef<Path> + Copy) {
+    if let Ok(dir_entries) = std::fs::read_dir(&path) {
+        for entry in dir_entries.flatten() {
+            let sub_path = entry.path();
+            let metadata = match entry.metadata() {
+                Ok(metadata) => metadata,
+                Err(err) => {
+                    warn!(
+                        "Failed to get metadata for {}. Error: {}",
+                        sub_path.display(),
+                        err.to_string()
+                    );
+                    break;
+                }
+            };
+            if metadata.is_dir() {
+                if let Err(err) = std::fs::remove_dir_all(&sub_path) {
+                    warn!(
+                        "Failed to remove sub directory {}.  Error: {}",
+                        sub_path.display(),
+                        err.to_string()
+                    );
+                }
+            } else if metadata.is_file() {
+                if let Err(err) = std::fs::remove_file(&sub_path) {
+                    warn!(
+                        "Failed to remove file {}.  Error: {}",
+                        sub_path.display(),
+                        err.to_string()
+                    );
+                }
+            }
+        }
+    } else {
+        warn!(
+            "Failed to read the sub paths of {}",
+            path.as_ref().display()
+        );
+    }
+}
+
 fn cleanup_accounts_paths(config: &ValidatorConfig) {
     for accounts_path in &config.account_paths {
         move_and_async_delete_path(accounts_path);
```
