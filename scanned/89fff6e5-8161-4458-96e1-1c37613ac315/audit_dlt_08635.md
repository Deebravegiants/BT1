# [?] fix: don't panic when the state-root is missing

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2022-01-04
Source: https://github.com/filecoin-project/ref-fvm/commit/c8030f05330159e88c7e8546cd3811e699e30f69
Type: security-commit

## Details
fix: don't panic when the state-root is missing

## Patch
### fvm/src/machine/default.rs
```diff
@@ -1,4 +1,4 @@
-use anyhow::anyhow;
+use anyhow::{anyhow, Context as _};
 use cid::Cid;
 use log::Level::Trace;
 use log::{debug, log_enabled, trace};
@@ -77,7 +77,16 @@ where
         // Initialize the WASM engine.
         let engine = Engine::new(&config.engine)?;
 
-        assert!(blockstore.has(&context.initial_state_root).unwrap());
+        if !blockstore
+            .has(&context.initial_state_root)
+            .context("failed to load initial state-root")?
+        {
+            return Err(anyhow!(
+                "blockstore doesn't have the initial state-root {}",
+                &context.initial_state_root
+            ));
+        }
+
         let bstore = BufferedBlockstore::new(blockstore);
 
         let state_tree = StateTree::new_from_root(bstore, &context.initial_state_root)?;
```
