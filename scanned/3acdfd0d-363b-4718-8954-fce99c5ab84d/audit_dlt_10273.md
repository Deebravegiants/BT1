# [?] Avoid panic when `SystemOverrides` not set.

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-04-26
Source: https://github.com/radixdlt/babylon-node/commit/18320bf34752c381d66a8b105abc6c74921b4679
Type: security-commit

## Details
Avoid panic when `SystemOverrides` not set.

## Patch
### core-rust/state-manager/src/transaction/executable_logic.rs
```diff
@@ -269,7 +269,8 @@ impl CustomizedExecutionConfig for ExecutionConfig {
             execution_trace,
             system_overrides: Some(SystemOverrides {
                 disable_costing: no_fees,
-                ..system_overrides.expect("all ExecutionConfig's constructors set this field")
+                // Note: In practice, all ExecutionConfig's constructors set the system_overrides.
+                ..system_overrides.unwrap_or_default()
             }),
         }
     }
```
