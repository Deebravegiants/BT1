# [?] idl: Fix potential panic on external type resolution (#2954)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2024-05-09
Source: https://github.com/otter-sec/anchor/commit/14309ea14639b8042055e1b432bd6be24434970f
Type: security-commit

## Details
idl: Fix potential panic on external type resolution (#2954)

## Patch
### CHANGELOG.md
```diff
@@ -24,6 +24,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - cli: Use npm's configured default license for new projects made with `anchor init` ([#2929](https://github.com/coral-xyz/anchor/pull/2929)).
 - cli: add filename to 'Unable to read keypair file' errors ([#2932](https://github.com/coral-xyz/anchor/pull/2932)).
 - idl: Fix path resolution of the `Cargo.lock` of the project when generating idls for external types ([#2946](https://github.com/coral-xyz/anchor/pull/2946)).
+- idl: Fix potential panic on external type resolution ([#2954](https://github.com/coral-xyz/anchor/pull/2954)).
 
 ### Breaking
 
```

### lang/syn/src/idl/common.rs
```diff
@@ -1,22 +1,19 @@
-use std::{
-    fs,
-    path::{Path, PathBuf},
-};
+use std::path::{Path, PathBuf};
 
-use anyhow::Result;
+use anyhow::{anyhow, Result};
 use proc_macro2::TokenStream;
 use quote::{quote, ToTokens};
 
 pub fn find_path(name: &str, path: impl AsRef<Path>) -> Result<PathBuf> {
-    let parent_path = path.as_ref().parent().unwrap();
-    for entry in fs::read_dir(parent_path)? {
-        let entry = entry?;
-        if entry.file_name().to_string_lossy() == name {
-            return entry.path().canonicalize().map_err(Into::into);
+    let path = path.as_ref();
+    for ancestor in path.ancestors() {
+        let file_path = ancestor.join(name);
+        if file_path.exists() {
+            return file_path.canonicalize().map_err(Into::into);
         }
     }
 
-    find_path(name, parent_path)
+    Err(anyhow!("Path ({path:?}) not found"))
 }
 
 pub fn get_no_docs() -> bool {
```
