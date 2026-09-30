# [?] Fix const folding of panic_with_byte_array not to assume the return t… (#8366)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-09-09
Source: https://github.com/starkware-libs/cairo/commit/a88686e6609f1278170b2088bf005c2ec10b183b
Type: security-commit

## Details
Fix const folding of panic_with_byte_array not to assume the return t… (#8366)

## Patch
### crates/cairo-lang-lowering/src/optimizations/const_folding.rs
```diff
@@ -5,6 +5,7 @@ mod test;
 use std::sync::Arc;
 
 use cairo_lang_defs::ids::{ExternFunctionId, FreeFunctionId};
+use cairo_lang_filesystem::flag::flag_unsafe_panic;
 use cairo_lang_semantic::corelib::try_extract_nz_wrapped_type;
 use cairo_lang_semantic::helper::ModuleHelper;
 use cairo_lang_semantic::items::constant::{ConstCalcInfo, ConstValue};
@@ -386,7 +387,7 @@ impl<'a> ConstFoldingContext<'a> {
                 .concretize(db, vec![GenericArgumentId::Constant(val.clone().intern(db))])
                 .lowered(db);
             return None;
-        } else if stmt.function == self.panic_with_byte_array {
+        } else if stmt.function == self.panic_with_byte_array && !flag_unsafe_panic(db) {
             let snap = self.var_info.get(&stmt.inputs[0].var_id)?;
             let bytearray = try_extract_matches!(snap, VarInfo::Snapshot)?;
             let [
```
