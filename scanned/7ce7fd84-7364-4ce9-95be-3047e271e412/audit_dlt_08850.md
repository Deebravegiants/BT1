# [?] fix: use Terminal::text() for modifier text to avoid panic on malformed attribute args (#9813)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-01
Source: https://github.com/starkware-libs/cairo/commit/7360a155838a3cc03a3fed08c2a0abd24cd99ca3
Type: security-commit

## Details
fix: use Terminal::text() for modifier text to avoid panic on malformed attribute args (#9813)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/attributes
```diff
@@ -31,3 +31,22 @@ error[E2019]: Can not create instances of phantom types.
  --> lib.cairo:10:5
     MyEnum::a(3);
     ^^^^^^^^^^^^
+
+//! > ==========================================================================
+
+//! > Attribute argument with modifier keyword.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: false)
+
+//! > function_code
+fn foo() {}
+
+//! > function_name
+foo
+
+//! > module_code
+#[cfg(ref x)]
+fn f() {}
+
+//! > expected_diagnostics
```

### crates/cairo-lang-syntax/src/attribute/structured.rs
```diff
@@ -167,12 +167,10 @@ impl<'a> AttributeArg<'a> {
 impl<'a> Modifier<'a> {
     /// Builds [`Modifier`] from [`ast::Modifier`].
     fn from(modifier: ast::Modifier<'a>, db: &'a dyn Database) -> Modifier<'a> {
-        Modifier {
-            stable_ptr: modifier.stable_ptr(db),
-            text: modifier
-                .as_syntax_node()
-                .text(db)
-                .expect("Modifier should always have underlying text"),
-        }
+        let text = match &modifier {
+            ast::Modifier::Ref(r) => r.text(db),
+            ast::Modifier::Mut(m) => m.text(db),
+        };
+        Modifier { stable_ptr: modifier.stable_ptr(db), text }
     }
 }
```
