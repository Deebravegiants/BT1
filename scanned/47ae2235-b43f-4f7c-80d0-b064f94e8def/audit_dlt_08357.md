# [?] fix field native panic (#751)

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-12-16
Source: https://github.com/move-language/move/commit/f20e04d70f925e2a536a8e5e877517525279a831
Type: security-commit

## Details
fix field native panic (#751)

## Patch
### language/move-binary-format/src/normalized.rs
```diff
@@ -296,7 +296,10 @@ impl Struct {
     pub fn new(m: &CompiledModule, def: &StructDefinition) -> (Identifier, Self) {
         let handle = m.struct_handle_at(def.struct_handle);
         let fields = match &def.field_information {
-            StructFieldInformation::Native => panic!("Can't extract for native struct"),
+            StructFieldInformation::Native => {
+                // Pretend for compatibility checking no fields
+                vec![]
+            }
             StructFieldInformation::Declared(fields) => {
                 fields.iter().map(|f| Field::new(m, f)).collect()
             }
```
