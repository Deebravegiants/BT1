# [?] fix(rpc): prevent u64 underflow when re-executing genesis block (#22532)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-27
Source: https://github.com/paradigmxyz/reth/commit/3fddefbd38c185136d6994cfb04e924442808ca3
Type: security-commit

## Details
fix(rpc): prevent u64 underflow when re-executing genesis block (#22532)

## Patch
### crates/rpc/rpc/src/reth.rs
```diff
@@ -155,6 +155,10 @@ where
             return Ok(None)
         };
 
+        if start_block == 0 {
+            return Ok(Some(ExecutionOutcome::default()))
+        }
+
         let state_provider = self.provider().history_by_block_number(start_block - 1)?;
         let db = reth_revm::database::StateProviderDatabase::new(&state_provider);
 
```
