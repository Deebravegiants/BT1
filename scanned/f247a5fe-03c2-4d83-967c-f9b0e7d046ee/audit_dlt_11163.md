# [?] fix(utils-core-derive): correct derive macro panic message (#3175)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-05-22
Source: https://github.com/0xMiden/miden-vm/commit/e4e8743bb9d2f0b6f2b9d56ebf472af94b192d6a
Type: security-commit

## Details
fix(utils-core-derive): correct derive macro panic message (#3175)

Signed-off-by: sashaphmn <sashaphmn@gmail.com>

## Patch
### crates/utils-core-derive/src/lib.rs
```diff
@@ -274,7 +274,7 @@ pub fn derive_mast_forest_contributor(input: TokenStream) -> TokenStream {
     // Parse the data to ensure it's an enum
     let enum_data = match &input.data {
         Data::Enum(data) => data,
-        _ => panic!("EnumThispatch can only be derived for enums"),
+        _ => panic!("MastForestContributor can only be derived for enums"),
     };
 
     // Extract variant information
```
