# [?] [aptos-debugger] Fix aptos debugger crash (#16121)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-03-13
Source: https://github.com/aptos-labs/aptos-core/commit/3d6b4fad2acdd09a56227feb9444d98d6939696e
Type: security-commit

## Details
[aptos-debugger] Fix aptos debugger crash (#16121)

## Patch
### aptos-move/aptos-debugger/src/aptos_debugger.rs
```diff
@@ -74,7 +74,10 @@ impl AptosDebugger {
         print_transaction_stats(txn_provider.get_txns(), version);
 
         let mut result = None;
-
+        assert!(
+            !concurrency_levels.is_empty(),
+            "concurrency_levels cannot be empty"
+        );
         for concurrency_level in concurrency_levels {
             for i in 0..repeat_execution_times {
                 let start_time = Instant::now();
```

### aptos-move/aptos-debugger/src/common.rs
```diff
@@ -27,7 +27,7 @@ pub struct Opts {
     #[clap(flatten)]
     pub(crate) target: Target,
 
-    #[clap(long, num_args = 0..)]
+    #[clap(long, num_args = 0.., default_values_t = [1])]
     pub(crate) concurrency_level: Vec<usize>,
 }
 
```
