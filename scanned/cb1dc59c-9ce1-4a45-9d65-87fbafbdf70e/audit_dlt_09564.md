# [?] Fix Panic in Historical Replay Test Due to Incorrect Assertion for eSpace Killed Address

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2023-12-26
Source: https://github.com/Conflux-Chain/conflux-rust/commit/b7837ea3d3d09b10373372512ba5646fc19a46d1
Type: security-commit

## Details
Fix Panic in Historical Replay Test Due to Incorrect Assertion for eSpace Killed Address

## Patch
### core/executor/src/executive/pre_checked_executive.rs
```diff
@@ -347,27 +347,26 @@ impl<'a, O: ExecutiveObserver> PreCheckedExecutive<'a, O> {
         let mut tracer = self.observer.as_tracer();
 
         let mut substate = Substate::new();
-        for address in &parent_substate.suicides {
+        for address in parent_substate
+            .suicides
+            .iter()
+            .filter(|x| x.space == Space::Native)
+        {
             let code_size = state.code_size(address)?;
             if code_size > 0 {
                 // Only refund the code collateral when code exists.
                 // If a contract suicides during creation, the code will be
                 // empty.
-                if address.space == Space::Native {
-                    let code_owner = state.code_owner(address)?;
-                    substate.record_storage_release(
-                        &code_owner,
-                        code_collateral_units(code_size),
-                    );
-                }
-            }
-
-            if address.space == Space::Native {
-                state.record_storage_and_whitelist_entries_release(
-                    &address.address,
-                    &mut substate,
-                )?;
+                let code_owner = state.code_owner(address)?;
+                substate.record_storage_release(
+                    &code_owner,
+                    code_collateral_units(code_size),
+                );
             }
+            state.record_storage_and_whitelist_entries_release(
+                &address.address,
+                &mut substate,
+            )?;
 
             assert!(state.is_fresh_storage(address)?);
         }
```
