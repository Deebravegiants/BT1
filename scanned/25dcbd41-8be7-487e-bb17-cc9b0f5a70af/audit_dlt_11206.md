# [?] fix(blockifier): have sierra_gas_to_steps_gas log err instead of panic (#7531)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2025-06-23
Source: https://github.com/starkware-libs/sequencer/commit/906baf5f654dac0b4ad5060ee9d2d56e53759e6b
Type: security-commit

## Details
fix(blockifier): have sierra_gas_to_steps_gas log err instead of panic (#7531)

## Patch
### crates/blockifier/src/bouncer.rs
```diff
@@ -542,11 +542,14 @@ pub fn sierra_gas_to_steps_gas(
     let builtins_gas_cost = builtins_to_sierra_gas(builtin_counters, versioned_constants);
 
     sierra_gas.checked_sub(builtins_gas_cost).unwrap_or_else(|| {
-        panic!(
-            "Invalid gas subtraction: builtins gas exceeds total sierra gas. Sierra gas: {:?}, \
-             Builtins gas: {:?}, Builtins: {:?}",
-            sierra_gas, builtins_gas_cost, builtin_counters
-        )
+        log::debug!(
+            "Sierra gas underflow: builtins gas exceeds total. Sierra gas: {:?}, Builtins gas: \
+             {:?}, Builtins: {:?}",
+            sierra_gas,
+            builtins_gas_cost,
+            builtin_counters
+        );
+        GasAmount::ZERO
     })
 }
 
```
