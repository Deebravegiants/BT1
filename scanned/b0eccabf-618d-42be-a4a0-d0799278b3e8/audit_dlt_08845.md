# [?] fix: emit diagnostic for member access on unreduced impl type instead of panicking (#9807)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-05
Source: https://github.com/starkware-libs/cairo/commit/26de58883584662320343afc3ec072b1c9d07444
Type: security-commit

## Details
fix: emit diagnostic for member access on unreduced impl type instead of panicking (#9807)

## Patch
### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -7,7 +7,6 @@ use std::ops::Deref;
 use std::sync::Arc;
 
 use ast::PathSegment;
-use cairo_lang_debug::DebugWithDb;
 use cairo_lang_defs::db::{DefsGroup, get_all_path_leaves, validate_attributes_flat};
 use cairo_lang_defs::diagnostic_utils::StableLocation;
 use cairo_lang_defs::ids::{
@@ -3961,17 +3960,16 @@ fn member_access_expr<'db>(
         TypeLongId::Closure(_) => {
             Err(ctx.diagnostics.report(rhs_syntax.stable_ptr(db), Unsupported))
         }
-        TypeLongId::ImplType(impl_type_id) => {
-            unreachable!("Impl type should've been reduced {:?}.", impl_type_id.debug(ctx.db))
-        }
         TypeLongId::Var(_) => Err(ctx.diagnostics.report(
             rhs_syntax.stable_ptr(db),
             InternalInferenceError(InferenceError::TypeNotInferred(long_ty.intern(ctx.db))),
         )),
-        TypeLongId::GenericParameter(_) | TypeLongId::Coupon(_) => Err(ctx.diagnostics.report(
-            rhs_syntax.stable_ptr(db),
-            TypeHasNoMembers { ty: long_ty.intern(ctx.db), member_name },
-        )),
+        TypeLongId::ImplType(_) | TypeLongId::GenericParameter(_) | TypeLongId::Coupon(_) => {
+            Err(ctx.diagnostics.report(
+                rhs_syntax.stable_ptr(db),
+                TypeHasNoMembers { ty: long_ty.intern(ctx.db), member_name },
+            ))
+        }
         TypeLongId::Missing(diag_added) => Err(*diag_added),
     }
 }
```

### crates/cairo-lang-semantic/src/expr/test_data/structure
```diff
@@ -127,3 +127,43 @@ error[E2023]: Base struct has no effect, all the fields in the struct have alrea
  --> lib.cairo:5:15
     A { a: 4, ..a }
               ^^^
+
+//! > ==========================================================================
+
+//! > Member access on unreduced impl associated type.
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
+struct S {
+    val: felt252,
+}
+
+trait T<X> {
+    type A;
+    fn f(self: @X) -> Self::A;
+}
+
+impl I of T<S> {
+    type A = S;
+    fn f(self: @S) -> S {
+        S { val: 0 }
+    }
+}
+
+fn g<X, impl H: T<X>>(x: @X) -> felt252 {
+    H::f(x).val
+}
+
+//! > expected_diagnostics
+error[E2057]: Type "H::A" has no members.
+ --> lib.cairo:18:13
+    H::f(x).val
+            ^^^
```
