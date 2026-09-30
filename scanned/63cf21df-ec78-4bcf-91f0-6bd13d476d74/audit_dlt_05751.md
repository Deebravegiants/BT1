# [?] [execution] Fix BlockExecutor panic during state sync abort (#19268)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-02
Source: https://github.com/aptos-labs/aptos-core/commit/4f190a1292b6d3c05a31a593d498c36306370ae5
Type: security-commit

## Details
[execution] Fix BlockExecutor panic during state sync abort (#19268)

When state sync aborts the consensus pipeline, `finish()` sets
`inner = None`. But `spawn_blocking` tasks that can't be cancelled
may still call `pre_commit_block` or `commit_ledger`, hitting
`.expect("BlockExecutor is not reset")` and panicking the validator.

Replace the two `.expect()` calls with `.ok_or_else()` to return
an error instead, consistent with how `ledger_update` already
handles this case.

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### execution/executor/src/block_executor/mod.rs
```diff
@@ -108,7 +108,9 @@ where
         self.inner
             .read()
             .as_ref()
-            .expect("BlockExecutor is not reset")
+            .ok_or_else(|| ExecutorError::InternalError {
+                error: "BlockExecutor is not reset".into(),
+            })?
             .execute_and_update_state(block, parent_block_id, onchain_config)
     }
 
@@ -134,7 +136,9 @@ where
         self.inner
             .read()
             .as_ref()
-            .expect("BlockExecutor is not reset")
+            .ok_or_else(|| ExecutorError::InternalError {
+                error: "BlockExecutor is not reset".into(),
+            })?
             .pre_commit_block(block_id)
     }
 
@@ -144,7 +148,9 @@ where
         self.inner
             .read()
             .as_ref()
-            .expect("BlockExecutor is not reset")
+            .ok_or_else(|| ExecutorError::InternalError {
+                error: "BlockExecutor is not reset".into(),
+            })?
             .commit_ledger(ledger_info_with_sigs)
     }
 
```
