# [?] fix(lsp): crash when file not in workspace (#4146)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-01-24
Source: https://github.com/noir-lang/noir/commit/cf7130f2e19e2d241e003c5527de9bf9d74cea40
Type: security-commit

## Details
fix(lsp): crash when file not in workspace (#4146)

# Description

## Problem\*

Resolves <!-- Link to GitHub Issue -->

LSP crash when source file not in workspace #4143

## Summary\*



## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### tooling/lsp/src/lib.rs
```diff
@@ -4,11 +4,12 @@
 #![cfg_attr(not(test), warn(unused_crate_dependencies, unused_extern_crates))]
 
 use std::{
-    collections::HashMap,
+    collections::{BTreeMap, HashMap},
     future::Future,
     ops::{self, ControlFlow},
     path::{Path, PathBuf},
     pin::Pin,
+    str::FromStr,
     task::{self, Poll},
 };
 
@@ -20,7 +21,11 @@ use async_lsp::{
 use fm::{codespan_files as files, FileManager};
 use fxhash::FxHashSet;
 use lsp_types::CodeLens;
-use nargo::{parse_all, workspace::Workspace};
+use nargo::{
+    package::{Package, PackageType},
+    parse_all,
+    workspace::Workspace,
+};
 use nargo_toml::{find_file_manifest, resolve_workspace_from_toml, PackageSelection};
 use noirc_driver::{file_manager_with_stdlib, prepare_crate, NOIR_ARTIFACT_VERSION_STRING};
 use noirc_frontend::{
@@ -209,23 +214,38 @@ fn byte_span_to_range<'a, F: files::Files<'a> + ?Sized>(
 }
 
 pub(crate) fn resolve_workspace_for_source_path(file_path: &Path) -> Result<Workspace, LspError> {
-    let package_root = find_file_manifest(file_path);
-
-    let toml_path = package_root.ok_or_else(|| {
-        LspError::WorkspaceResolutionError(format!(
-            "Nargo.toml not found for file: {:?}",
-            file_path
-        ))
-    })?;
-
-    let workspace = resolve_workspace_from_toml(
-        &toml_path,
-        PackageSelection::All,
-        Some(NOIR_ARTIFACT_VERSION_STRING.to_string()),
-    )
-    .map_err(|err| LspError::WorkspaceResolutionError(err.to_string()))?;
-
-    Ok(workspace)
+    if let Some(toml_path) = find_file_manifest(file_path) {
+        resolve_workspace_from_toml(
+            &toml_path,
+            PackageSelection::All,
+            Some(NOIR_ARTIFACT_VERSION_STRING.to_string()),
+        )
+        .map_err(|err| LspError::WorkspaceResolutionError(err.to_string()))
+    } else {
+        let Some(parent_folder) = file_path.parent().and_then(|f| f.file_name()).and_then(|file_name_os_str| file_name_os_str.to_str()) else {
+            return Err(LspError::WorkspaceResolutionError(format!(
+                "Could not resolve parent folder for file: {:?}",
+                file_path
+            )))
+        };
+        let assumed_package = Package {
+            version: None,
+            compiler_required_version: Some(NOIR_ARTIFACT_VERSION_STRING.to_string()),
+            root_dir: PathBuf::from(parent_folder),
+            package_type: PackageType::Binary,
+            entry_path: PathBuf::from(file_path),
+            name: CrateName::from_str(parent_folder)
+                .map_err(|err| LspError::WorkspaceResolutionError(err.to_string()))?,
+            dependencies: BTreeMap::new(),
+        };
+        let workspace = Workspace {
+            root_dir: PathBuf::from(parent_folder),
+            members: vec![assumed_package],
+            selected_package_index: Some(0),
+            is_assumed: true,
+        };
+        Ok(workspace)
+    }
 }
 
 /// Prepares a package from a source string
```

### tooling/nargo/src/workspace.rs
```diff
@@ -20,6 +20,8 @@ pub struct Workspace {
     pub members: Vec<Package>,
     // If `Some()`, the `selected_package_index` is used to select the only `Package` when iterating a Workspace
     pub selected_package_index: Option<usize>,
+    /// If we could not resolve the workspace we would inform the user we have assumed it (ie. from lsp file path given)
+    pub is_assumed: bool,
 }
 
 impl Workspace {
```

### tooling/nargo_toml/src/lib.rs
```diff
@@ -345,6 +345,7 @@ fn toml_to_workspace(
                     root_dir: nargo_toml.root_dir,
                     selected_package_index: Some(0),
                     members: vec![member],
+                    is_assumed: false,
                 },
             }
         }
@@ -392,7 +393,12 @@ fn toml_to_workspace(
                 PackageSelection::All => (),
             }
 
-            Workspace { root_dir: nargo_toml.root_dir, members, selected_package_index }
+            Workspace {
+                root_dir: nargo_toml.root_dir,
+                members,
+                selected_package_index,
+                is_assumed: false,
+            }
         }
     };
 
```
