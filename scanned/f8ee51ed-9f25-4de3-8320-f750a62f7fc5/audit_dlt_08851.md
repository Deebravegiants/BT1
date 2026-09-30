# [?] fix: emit diagnostic for unsupported extern fn in const evaluation instead of panicking (#9811)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-01
Source: https://github.com/starkware-libs/cairo/commit/524847535f7891258ff067d91e8405c2e0747153
Type: security-commit

## Details
fix: emit diagnostic for unsupported extern fn in const evaluation instead of panicking (#9811)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/constant
```diff
@@ -706,3 +706,26 @@ impl AnotherFoo<impl F: Foo> of Foo {
 }
 
 //! > expected_diagnostics
+
+//! > ==========================================================================
+
+//! > User-defined extern const fn in constant expression.
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
+extern const fn f() -> felt252 nopanic;
+const X: felt252 = f();
+
+//! > expected_diagnostics
+error[E2127]: This expression is not supported as constant.
+ --> lib.cairo:2:20
+const X: felt252 = f();
+                   ^^^
```

### crates/cairo-lang-semantic/src/items/constant.rs
```diff
@@ -5,7 +5,7 @@ use cairo_lang_debug::DebugWithDb;
 use cairo_lang_defs::db::DefsGroup;
 use cairo_lang_defs::ids::{
     ConstantId, ExternFunctionId, GenericParamId, LanguageElementId, LookupItemId, ModuleItemId,
-    NamedLanguageElementId, TopLevelLanguageElementId, TraitConstantId, TraitId, VarId,
+    NamedLanguageElementId, TraitConstantId, TraitId, VarId,
 };
 use cairo_lang_diagnostics::{
     DiagnosticAdded, DiagnosticEntry, DiagnosticNote, Diagnostics, Maybe, MaybeAsRef,
@@ -1085,9 +1085,12 @@ impl<'a, 'r, 'mt> ConstantEvaluateContext<'a, 'r, 'mt> {
                     .intern(db),
                 );
             } else {
-                unreachable!(
-                    "Unexpected extern function in constant lowering: `{}`",
-                    extern_fn.full_path(db)
+                return Some(
+                    ConstValue::Missing(self.diagnostics.report(
+                        expr.stable_ptr.untyped(),
+                        SemanticDiagnosticKind::UnsupportedConstant,
+                    ))
+                    .intern(db),
                 );
             }
         }
```
