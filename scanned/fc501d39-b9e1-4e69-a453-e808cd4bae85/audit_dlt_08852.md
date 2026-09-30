# [?] fix: return None for macro rule with missing param kind instead of panicking (#9809)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-01
Source: https://github.com/starkware-libs/cairo/commit/8c8cbafd76c387b40667fb4a34a697a89d21249a
Type: security-commit

## Details
fix: return None for macro rule with missing param kind instead of panicking (#9809)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/statements
```diff
@@ -216,3 +216,35 @@ fn unstable_function_with_note() -> felt252 {
 //! > function_body
 
 //! > expected_diagnostics
+
+//! > ==========================================================================
+
+//! > Declarative macro with parameter missing kind specifier.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {
+    m!(1);
+}
+
+//! > function_name
+foo
+
+//! > module_code
+macro m {
+    ($x) => { 0 };
+}
+
+//! > expected_diagnostics
+error[E1010]: Macro parameter must have a kind.
+ --> lib.cairo:2:7
+    ($x) => { 0 };
+      ^
+
+error[E2158]: No matching rule found in inline macro `m`.
+ --> lib.cairo:5:5
+    m!(1);
+    ^^^^^
+
```

### crates/cairo-lang-semantic/src/items/macro_declaration.rs
```diff
@@ -295,10 +295,7 @@ fn is_macro_rule_match_ex<'db>(
                     if let ast::OptionParamKind::ParamKind(param_kind) = param.kind(db) {
                         param_kind.kind(db).into()
                     } else {
-                        unreachable!(
-                            "Missing macro rule param kind, should have been handled by the \
-                             parser."
-                        )
+                        return None;
                     };
                 let placeholder_name = param.name(db).as_syntax_node().get_text_without_trivia(db);
                 match placeholder_kind {
```
