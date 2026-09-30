# [?] fix: align MAX_STACK_TRACE_DEPTH panic message (#8624)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-11-11
Source: https://github.com/starkware-libs/cairo/commit/53888fcf411df738090aceddf673b71af34929d0
Type: security-commit

## Details
fix: align MAX_STACK_TRACE_DEPTH panic message (#8624)

## Patch
### crates/cairo-lang-runner/src/lib.rs
```diff
@@ -548,8 +548,7 @@ impl Default for ProfilingInfoCollectionConfig {
                 if max.is_empty() {
                     MAX_STACK_TRACE_DEPTH_DEFAULT
                 } else {
-                    max.parse::<usize>()
-                        .expect("MAX_STACK_TRACE_DEPTH_DEFAULT env var is not numeric")
+                    max.parse::<usize>().expect("MAX_STACK_TRACE_DEPTH env var is not numeric")
                 }
             } else {
                 MAX_STACK_TRACE_DEPTH_DEFAULT
```
