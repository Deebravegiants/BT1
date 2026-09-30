# [?] fix(move-analyzer): fix crash if open a standalone Move file (#4791)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-01-16
Source: https://github.com/iotaledger/iota/commit/09f55658e07f43f5a8d362a1bc5795b2c2819154
Type: security-commit

## Details
fix(move-analyzer): fix crash if open a standalone Move file (#4791)

## Patch
### external-crates/move/crates/move-analyzer/src/symbols.rs
```diff
@@ -1199,20 +1199,21 @@ impl SymbolicatorRunner {
                     };
                     if let Some(starting_path) = starting_path_opt {
                         let root_dir = Self::root_dir(&starting_path);
-                        if root_dir.is_none() && !missing_manifests.contains(&starting_path) {
-                            eprintln!("reporting missing manifest");
-
-                            // report missing manifest file only once to avoid cluttering IDE's UI
-                            // in cases when developer indeed intended
-                            // to open a standalone file that was
-                            // not meant to compile
-                            missing_manifests.insert(starting_path);
-                            if let Err(err) = sender.send(Err(anyhow!(
-                                "Unable to find package manifest. Make sure that
-                            the source files are located in a sub-directory of a package containing
-                            a Move.toml file. "
-                            ))) {
-                                eprintln!("could not pass missing manifest error: {:?}", err);
+                        if root_dir.is_none() {
+                            if !missing_manifests.contains(&starting_path) {
+                                eprintln!("reporting missing manifest");
+
+                                // report missing manifest file only once to avoid cluttering IDE's UI in
+                                // cases when developer indeed intended to open a standalone file that was
+                                // not meant to compile
+                                missing_manifests.insert(starting_path);
+                                if let Err(err) = sender.send(Err(anyhow!(
+                                    "Unable to find package manifest. Make sure that
+                                    the source files are located in a sub-directory of a package containing
+                                    a Move.toml file. "
+                                ))) {
+                                    eprintln!("could not pass missing manifest error: {:?}", err);
+                                }
                             }
                             continue;
                         }
```
