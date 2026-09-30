# [?] fix(cheatcodes): don't panic on a bare type name in parseJsonType/parseTomlType (#16564)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-04
Source: https://github.com/foundry-rs/foundry/commit/73c81fae56404889d9af182caf593db75338623e
Type: security-commit

## Details
fix(cheatcodes): don't panic on a bare type name in parseJsonType/parseTomlType (#16564)

* fix(cheatcodes): don't panic on a bare type name in parseJsonType/parseTomlType

EncodeType::parse returns Ok with an empty types vec (not Err) when the
input has no '(', so the intended bail! error path was dead code and
encoded.types[0] panicked instead. Since panic = "abort" in release
builds, this killed the whole forge process on the most natural user
mistake (passing a bare struct/type name instead of a full encodeType
string) across all cheatcodes routed through resolve_type.

* update comment

---------

Co-authored-by: stevencartavia <112043913+stevencartavia@users.noreply.github.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### .changelog/fix-parse-json-type-panic-on-bare-name.md
```diff
@@ -0,0 +1,6 @@
+---
+forge: patch
+foundry-cheatcodes: patch
+---
+
+Fixed `vm.parseJsonType`/`vm.parseTomlType` (and related type-resolving cheatcodes) panicking instead of returning the intended error when given a bare type/struct name.
```

### crates/cheatcodes/src/json.rs
```diff
@@ -814,8 +814,10 @@ pub(super) fn resolve_type(
         return ordered_ty(ty);
     };
 
-    if let Ok(encoded) = EncodeType::parse(type_description) {
-        let main_type = encoded.types[0].type_name;
+    if let Ok(encoded) = EncodeType::parse(type_description)
+        && let Some(main) = encoded.types.first()
+    {
+        let main_type = main.type_name;
         let mut resolver = Resolver::default();
         for t in &encoded.types {
             resolver.ingest(t.to_owned());
@@ -1133,6 +1135,16 @@ mod tests {
         panic!("Expected Person to be CustomStruct");
     }
 
+    #[test]
+    fn test_resolve_type_bare_struct_name_errors_instead_of_panicking() {
+        // `EncodeType::parse` succeeds with an empty type list for inputs without `(`.
+        let err = resolve_type("Foo", None).unwrap_err();
+        assert!(
+            err.to_string().contains("valid Solidity type or a EIP712 `encodeType` string"),
+            "unexpected error: {err}"
+        );
+    }
+
     #[test]
     fn test_parse_fixed_array() {
         let mut struct_defs = TypeDefMap::new();
```
