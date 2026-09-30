# [?] fix: handle missing struct field in const evaluation instead of panicking (#9812)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-05
Source: https://github.com/starkware-libs/cairo/commit/4cc281bafb75f9d8c5e48c8daf0ab63ffde1bd27
Type: security-commit

## Details
fix: handle missing struct field in const evaluation instead of panicking (#9812)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/constant
```diff
@@ -729,3 +729,35 @@ error[E2127]: This expression is not supported as constant.
  --> lib.cairo:2:20
 const X: felt252 = f();
                    ^^^
+
+//! > ==========================================================================
+
+//! > Statement-level const struct literal with missing field.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {
+    const X: S = S { a: 1 };
+}
+
+//! > function_name
+foo
+
+//! > module_code
+struct S {
+    a: felt252,
+    b: felt252,
+}
+
+//! > expected_diagnostics
+error[E0003]: Missing member "b".
+ --> lib.cairo:6:18
+    const X: S = S { a: 1 };
+                 ^^^^^^^^^^
+
+warning[E2070]: Unused constant. Consider ignoring by prefixing with `_`.
+ --> lib.cairo:6:11
+    const X: S = S { a: 1 };
+          ^
```

### crates/cairo-lang-semantic/src/items/constant.rs
```diff
@@ -725,7 +725,9 @@ impl<'a, 'r, 'mt> ConstantEvaluateContext<'a, 'r, 'mt> {
                                 .iter()
                                 .find(|(_, member_id)| m.id == *member_id)
                                 .map(|(expr_id, _)| self.evaluate(*expr_id))
-                                .expect("Should have been caught by semantic validation")
+                                // Semantic validation already reported an error, suppress cascading
+                                // errors from const evaluation.
+                                .unwrap_or_else(|| ConstValue::Missing(skip_diagnostic()).intern(db))
                         })
                         .collect(),
                     *ty,
```
