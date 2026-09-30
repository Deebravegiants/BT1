# [?] fix: handle missing return type context in loop body instead of panicking (#9808)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-01
Source: https://github.com/starkware-libs/cairo/commit/8dd877910133ff8f13a23d50bc7a1a7351705818
Type: security-commit

## Details
fix: handle missing return type context in loop body instead of panicking (#9808)

## Patch
### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -2329,7 +2329,12 @@ fn compute_loop_body_semantic<'db>(
 ) -> (ExprId, InnerContext<'db>) {
     let db: &dyn Database = ctx.db;
     ctx.run_in_subscope(|new_ctx| {
-        let return_type = new_ctx.get_return_type().unwrap();
+        // `None` means we're outside a function/loop context (e.g. a loop in array size position).
+        // The invalid usage will be caught by the caller; use `missing` to suppress cascading
+        // errors.
+        let return_type = new_ctx
+            .get_return_type()
+            .unwrap_or_else(|| TypeId::missing(new_ctx.db, skip_diagnostic()));
         let old_inner_ctx = new_ctx.inner_ctx.replace(InnerContext { return_type, kind });
         let (statements, tail) = statements_and_tail(ctx.db, syntax.statements(db));
         let mut statements_semantic = vec![];
```

### crates/cairo-lang-semantic/src/expr/test_data/fixed_size_array
```diff
@@ -299,3 +299,32 @@ fn foo() {
 foo
 
 //! > expected_diagnostics
+
+//! > ==========================================================================
+
+//! > Loop expression in fixed-size array size position.
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
+fn f() -> [felt252; for _ in 0..1_u32 {}] {
+    [0]
+}
+
+//! > expected_diagnostics
+error[E2302]: Type mismatch: `()` and `core::integer::u32`.
+ --> lib.cairo:1:21
+fn f() -> [felt252; for _ in 0..1_u32 {}] {
+                    ^^^^^^^^^^^^^^^^^^^^
+
+error[E2172]: Fixed size array type must have a positive integer size.
+ --> lib.cairo:1:11
+fn f() -> [felt252; for _ in 0..1_u32 {}] {
+          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```
