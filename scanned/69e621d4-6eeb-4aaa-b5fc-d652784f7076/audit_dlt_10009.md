# [?] Use saturating_add to prevent possible overflow in migrations (#1199)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2022-01-20
Source: https://github.com/moonbeam-foundation/moonbeam/commit/d182d72504a7f8fe8166bffa026037cdb05658fe
Type: security-commit

## Details
Use saturating_add to prevent possible overflow in migrations (#1199)

## Patch
### pallets/migrations/src/lib.rs
```diff
@@ -292,7 +292,7 @@ pub mod pallet {
 				));
 				<MigrationState<T>>::insert(migration_name_as_bytes, true);
 
-				weight += consumed_weight;
+				weight = weight.saturating_add(consumed_weight);
 				if weight > available_weight {
 					log::error!(
 						"Migration {} consumed more weight than it was given! ({} > {})",
```
