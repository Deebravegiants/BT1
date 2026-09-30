# [?] Rare fd overflow fix with utxoindex (#726)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2025-08-27
Source: https://github.com/kaspanet/rusty-kaspa/commit/8ae5597077c4ad17bfd5e3f28209e4d29c2ab492
Type: security-commit

## Details
Rare fd overflow fix with utxoindex (#726)

## Patch
### kaspad/src/daemon.rs
```diff
@@ -223,7 +223,7 @@ pub fn create_core_with_runtime(runtime: &Runtime, args: &Args, fd_total_budget:
     let network = args.network();
     let mut fd_remaining = fd_total_budget;
     let utxo_files_limit = if args.utxoindex {
-        let utxo_files_limit = fd_remaining * 10 / 100;
+        let utxo_files_limit = fd_remaining / 10;
         fd_remaining -= utxo_files_limit;
         utxo_files_limit
     } else {
```
