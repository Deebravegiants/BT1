# [?] fix: `forc build` panic when sway package folder contains dot (#5448)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-01-11
Source: https://github.com/FuelLabs/sway/commit/5dda9a72247cd272205fcb68149d868268bc5945
Type: security-commit

## Details
fix: `forc build` panic when sway package folder contains dot (#5448)

## Description
Close #5434

Since `canonical_manifest_dir` is a dir, not a file, to get the
last-level dir name, we should use `file_name()` instead of `file_stem`.

## Patch
### sway-core/src/build_config.rs
```diff
@@ -72,7 +72,7 @@ impl BuildConfig {
             true => root_module,
             false => {
                 assert!(
-                    root_module.starts_with(canonical_manifest_dir.file_stem().unwrap()),
+                    root_module.starts_with(canonical_manifest_dir.file_name().unwrap()),
                     "file_name must be either absolute or relative to manifest directory",
                 );
                 canonical_manifest_dir
@@ -160,3 +160,29 @@ impl BuildConfig {
         self.canonical_root_module.clone()
     }
 }
+
+#[cfg(test)]
+mod test {
+    use super::*;
+    #[test]
+    fn test_root_from_file_name_and_manifest_path() {
+        let root_module = PathBuf::from("mock_path/src/main.sw");
+        let canonical_manifest_dir = PathBuf::from("/tmp/sway_project/mock_path");
+        BuildConfig::root_from_file_name_and_manifest_path(
+            root_module,
+            canonical_manifest_dir,
+            BuildTarget::default(),
+        );
+    }
+
+    #[test]
+    fn test_root_from_file_name_and_manifest_path_contains_dot() {
+        let root_module = PathBuf::from("mock_path_contains_._dot/src/main.sw");
+        let canonical_manifest_dir = PathBuf::from("/tmp/sway_project/mock_path_contains_._dot");
+        BuildConfig::root_from_file_name_and_manifest_path(
+            root_module,
+            canonical_manifest_dir,
+            BuildTarget::default(),
+        );
+    }
+}
```
