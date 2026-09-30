# [?] Avoid panic when an item-scope inline macro lacks an arg-list bracket (#9961)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-05-19
Source: https://github.com/starkware-libs/cairo/commit/adf04c14281084d7ef7d383c8418888a5d49d992
Type: security-commit

## Details
Avoid panic when an item-scope inline macro lacks an arg-list bracket (#9961)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/inline_macros
```diff
@@ -2730,3 +2730,39 @@ error[E2158]: No matching rule found in inline macro `mymac`.
  --> lib.cairo:6:5
     mymac!(0)
     ^^^^^^^^^
+
+//! > ==========================================================================
+
+//! > Regression for #9938: item-scope macro invocation without arg brackets does not ICE.
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
+#[feature("user_defined_inline_macros")]
+macro m {
+    ($x:ident) => { 1 };
+}
+m!
+
+//! > expected_diagnostics
+error[E1006]: Missing tokens. Expected an argument list wrapped in either parentheses, brackets, or braces.
+ --> lib.cairo:5:3
+m!
+  ^
+
+error[E1001]: Missing token ';'.
+ --> lib.cairo:5:3
+m!
+  ^
+
+error[E2158]: No matching rule found in inline macro `m`.
+ --> lib.cairo:5:1
+m!
+^^
```

### crates/cairo-lang-semantic/src/items/macro_declaration.rs
```diff
@@ -331,7 +331,7 @@ pub fn is_macro_rule_match<'db>(
         ast::WrappedTokenTree::Parenthesized(tt) => tt.tokens(db),
         ast::WrappedTokenTree::Braced(tt) => tt.tokens(db),
         ast::WrappedTokenTree::Bracketed(tt) => tt.tokens(db),
-        ast::WrappedTokenTree::Missing(_) => unreachable!(),
+        ast::WrappedTokenTree::Missing(_) => return None,
     }
     .elements(db)
     .peekable();
```
