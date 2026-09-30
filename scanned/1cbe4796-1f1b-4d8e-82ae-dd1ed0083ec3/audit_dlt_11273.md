# [?] fix: Fix no numeric generic given leading to panic (#10725)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-12-02
Source: https://github.com/noir-lang/noir/commit/131f9bc7bdd53b7b529ea7868bb5b5605baccf8d
Type: security-commit

## Details
fix: Fix no numeric generic given leading to panic (#10725)

## Patch
### EXTERNAL_NOIR_LIBRARIES.yml
```diff
@@ -95,7 +95,7 @@ libraries:
     repo: AztecProtocol/aztec-packages
     ref: *AZ_COMMIT
     path: noir-projects/noir-protocol-circuits/crates/private-kernel-lib
-    timeout: 330
+    timeout: 335
     critical: false
   protocol_circuits_types:
     repo: AztecProtocol/aztec-packages
```

### compiler/noirc_frontend/src/parser/parser/generics.rs
```diff
@@ -1,7 +1,7 @@
 use crate::{
     ast::{
-        GenericTypeArg, GenericTypeArgs, IdentOrQuotedType, IntegerBitSize, UnresolvedGeneric,
-        UnresolvedGenerics, UnresolvedType, UnresolvedTypeData,
+        GenericTypeArg, GenericTypeArgs, IdentOrQuotedType, IntegerBitSize, Path,
+        UnresolvedGeneric, UnresolvedGenerics, UnresolvedType, UnresolvedTypeData,
     },
     parser::{ParserErrorReason, labels::ParsingRuleLabel},
     shared::Signedness,
@@ -114,7 +114,14 @@ impl Parser<'_> {
             return Some(UnresolvedGeneric::Numeric { ident, typ });
         }
 
-        let typ = self.parse_type_or_error();
+        let mut typ = self.parse_type_or_error();
+
+        // If we failed to parse a type, default to u32 instead of Type::Error
+        // to prevent more type errors down the line
+        if typ.typ == UnresolvedTypeData::Error {
+            let path = Path::from_single("u32".to_string(), self.location_at_previous_token_end());
+            typ.typ = UnresolvedTypeData::Named(path, GenericTypeArgs::default(), true);
+        }
 
         Some(UnresolvedGeneric::Numeric { ident, typ })
     }
```

### compiler/noirc_frontend/src/tests/numeric_generics.rs
```diff
@@ -610,3 +610,17 @@ fn integer_with_suffix_used_as_tuple_index() {
     ";
     assert_no_errors(src);
 }
+
+// Regression for https://github.com/noir-lang/noir/issues/10711
+#[test]
+fn no_panic_on_numeric_generic_parse_error() {
+    let src = "
+        fn foo<let N: >() {
+                      ^ Expected a type but found '>'
+            let _ = N;
+        }
+
+        fn main() { foo::<3>(); }
+    ";
+    check_errors(src);
+}
```
