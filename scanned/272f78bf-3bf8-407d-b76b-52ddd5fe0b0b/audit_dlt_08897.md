# [?] fix(state/repair): entire repair loop is aborted if a panic occurs when storing classes

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-04-01
Source: https://github.com/software-mansion/pathfinder/commit/8133c7a56945628ebaf5b39a18c96811e14c3990
Type: security-commit

## Details
fix(state/repair): entire repair loop is aborted if a panic occurs when storing classes

## Patch
### crates/pathfinder/src/state/sync/repair.rs
```diff
@@ -82,15 +82,18 @@ where
                     let storage = storage.clone();
                     move || store_repaired_class(&storage, declared_hash, downloaded)
                 })
-                .await
-                .context("Joining database task")?;
+                .await;
 
                 match store_result {
                     Err(e) => {
                         tracing::warn!(hash=%declared_hash, error=%e, "Failed to store repaired class definition");
                         failed += 1;
                     }
-                    Ok(()) => {
+                    Ok(Err(e)) => {
+                        tracing::warn!(hash=%declared_hash, error=%e, "Failed to store repaired class definition");
+                        failed += 1;
+                    }
+                    Ok(Ok(())) => {
                         repaired += 1;
                     }
                 }
```
