# [?] fix: maybe overflow

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-02-07
Source: https://github.com/succinctlabs/sp1/commit/2f467248aa36d84e9b82e310837a3370ab735c66
Type: security-commit

## Details
fix: maybe overflow

## Patch
### patch-testing/sp1-test/src/utils.rs
```diff
@@ -111,7 +111,7 @@ pub fn pretty_comparison(
             name,
             old,
             new,
-            ((old - new) as f64 / old as f64) * 100.0
+            ((old as f64 - new as f64) / old as f64) * 100.0
         )?;
     }
 
```
