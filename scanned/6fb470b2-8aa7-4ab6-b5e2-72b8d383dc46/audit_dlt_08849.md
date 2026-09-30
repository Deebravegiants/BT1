# [?] fix: handle mismatched generic param kinds in substitution rewriter instead of panicking (#9815)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-01
Source: https://github.com/starkware-libs/cairo/commit/3855e3f4c5543870743635da458f3d5546a19e17
Type: security-commit

## Details
fix: handle mismatched generic param kinds in substitution rewriter instead of panicking (#9815)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/generics
```diff
@@ -712,3 +712,35 @@ error[E2041]: Unexpected argument type. Expected: "test::MyStruct::<2>", found:
  --> lib.cairo:11:10
     bar2(s);
          ^
+
+//! > ==========================================================================
+
+//! > Impl function with mismatched generic param kind (impl vs type).
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {}
+
+//! > function_name
+foo
+
+//! > module_code
+trait Foo {
+    fn bar<T>(self: T);
+}
+impl FooImpl of Foo {
+    fn bar<+Drop<felt252>>(self: felt252) {}
+}
+
+//! > expected_diagnostics
+error[E2036]: Parameter name of impl function FooImpl::bar is incompatible with Foo::bar parameter `T`.
+ --> lib.cairo:5:12
+    fn bar<+Drop<felt252>>(self: felt252) {}
+           ^^^^^^^^^^^^^^
+
+error[E2038]: Generic parameter kind of impl function `FooImpl::bar` is incompatible with `Foo::bar`. Expected: `Type`, actual: `Impl`.
+ --> lib.cairo:5:12
+    fn bar<+Drop<felt252>>(self: felt252) {}
+           ^^^^^^^^^^^^^^
```

### crates/cairo-lang-semantic/src/substitution.rs
```diff
@@ -6,7 +6,7 @@ use cairo_lang_defs::ids::{
     ImplFunctionId, ImplImplDefId, LanguageElementId, LocalVarId, MemberId, ParamId, StructId,
     TraitConstantId, TraitFunctionId, TraitId, TraitImplId, TraitTypeId, VariantId,
 };
-use cairo_lang_diagnostics::{DiagnosticAdded, Maybe};
+use cairo_lang_diagnostics::{DiagnosticAdded, Maybe, skip_diagnostic};
 use cairo_lang_utils::deque::Deque;
 use cairo_lang_utils::extract_matches;
 use cairo_lang_utils::ordered_hash_map::OrderedHashMap;
@@ -514,7 +514,11 @@ impl<'db> SemanticRewriter<TypeLongId<'db>, DiagnosticAdded> for SubstitutionRew
         match value {
             TypeLongId::GenericParameter(generic_param) => {
                 if let Some(generic_arg) = self.substitution.get(generic_param) {
-                    let type_id = *extract_matches!(generic_arg, GenericArgumentId::Type);
+                    let GenericArgumentId::Type(type_id) = generic_arg else {
+                        // The generic arg kind doesn't match the type parameter; a diagnostic
+                        // (WrongGenericParamKindForImplFunction) was already reported.
+                        return Err(skip_diagnostic());
+                    };
                     // return self.rewrite(type_id.long(self.db));
                     *value = type_id.long(self.db).clone();
                     return Ok(RewriteResult::Modified);
```
