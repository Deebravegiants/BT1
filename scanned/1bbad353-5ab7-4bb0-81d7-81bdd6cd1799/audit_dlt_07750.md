# [?] fix: prevent integer underflow in pipeline unwind target calculation (#18743)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-09-29
Source: https://github.com/paradigmxyz/reth/commit/b940d0a9fb2587625ba972831b17ceb92f8dea71
Type: security-commit

## Details
fix: prevent integer underflow in pipeline unwind target calculation (#18743)

## Patch
### crates/stages/api/src/pipeline/mod.rs
```diff
@@ -617,7 +617,10 @@ impl<N: ProviderNodeTypes> Pipeline<N> {
                 "Stage is missing static file data."
             );
 
-            Ok(Some(ControlFlow::Unwind { target: block.block.number - 1, bad_block: block }))
+            Ok(Some(ControlFlow::Unwind {
+                target: block.block.number.saturating_sub(1),
+                bad_block: block,
+            }))
         } else if err.is_fatal() {
             error!(target: "sync::pipeline", stage = %stage_id, "Stage encountered a fatal error: {err}");
             Err(err.into())
```
