# [?] Fix panic in code_owner.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-01-25
Source: https://github.com/Conflux-Chain/conflux-rust/commit/5f7d0ef3921dc3cb19c74ec3c645b6f691350b22
Type: security-commit

## Details
Fix panic in code_owner.

## Patch
### core/src/executive/executive.rs
```diff
@@ -1516,9 +1516,11 @@ impl<
                 // Only refund the code collateral when code exists.
                 // If a contract suicides during creation, the code will be
                 // empty.
-                let code_owner =
-                    self.state.code_owner(address)?.expect("code owner exists");
                 if address.space == Space::Native {
+                    let code_owner = self
+                        .state
+                        .code_owner(address)?
+                        .expect("code owner exists");
                     substate.record_storage_release(
                         &code_owner,
                         code_collateral_units(code_size),
```
