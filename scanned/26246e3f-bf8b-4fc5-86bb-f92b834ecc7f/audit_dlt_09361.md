# [?] fix: malformed suggestion in OwnedStateVariable storage panic message  (#22862)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-04-29
Source: https://github.com/AztecProtocol/aztec-packages/commit/bd33eadc238e3755dc8af1579683dedbfe6a46fc
Type: security-commit

## Details
fix: malformed suggestion in OwnedStateVariable storage panic message  (#22862)

This was just poor formatting on an error msg.

## Patch
### noir-projects/aztec-nr/aztec/src/macros/storage.nr
```diff
@@ -47,7 +47,7 @@ pub comptime fn storage(s: TypeDefinition) -> Quoted {
             if typ.implements(quote { crate::state_vars::OwnedStateVariable<$_maybe_owned_context> }
                 .as_trait_constraint()) {
                 panic(
-                    f"Type {typ} implements OwnedStateVariable and hence cannot be placed in Storage struct without being wrapped in Owned. Define the type in storage as Owned<{typ}<..., Context>>, Context>.",
+                    f"Type {typ} implements OwnedStateVariable and hence cannot be placed in Storage struct without being wrapped in Owned. Wrap the type in Owned<..., Context>.",
                 )
             }
 
```

### noir-projects/noir-contracts-comp-failures/contracts/panic_on_owned_state_var_in_storage/expected_error
```diff
@@ -1,3 +1,3 @@
-Type PrivateImmutable<Field, Context> implements OwnedStateVariable and hence cannot be placed in Storage struct without being wrapped in Owned. Define the type in storage as Owned<PrivateImmutable<Field, Context><..., Context>>, Context>.
+Type PrivateImmutable<Field, Context> implements OwnedStateVariable and hence cannot be placed in Storage struct without being wrapped in Owned. Wrap the type in Owned<..., Context>.
 Could not resolve 'init' in path
 Type annotation needed
```
