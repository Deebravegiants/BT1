# [?] Prevented crashing the test plugin by available gas diag change. (#4483)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-11-27
Source: https://github.com/starkware-libs/cairo/commit/32eefb4d386380098c7c3442960e432597e27aab
Type: security-commit

## Details
Prevented crashing the test plugin by available gas diag change. (#4483)

## Patch
### crates/cairo-lang-test-plugin/src/test_config.rs
```diff
@@ -133,32 +133,29 @@ fn extract_available_gas(
         // loops will run out of gas.
         return Some(u32::MAX as usize);
     };
-    let mut add_malformed_attr_diag = || {
+    match &attr.args[..] {
+        [AttributeArg { variant: AttributeArgVariant::Unnamed { value, .. }, .. }] => match value {
+            ast::Expr::Path(path)
+                if path.as_syntax_node().get_text_without_trivia(db) == STATIC_GAS_ARG =>
+            {
+                return None;
+            }
+            ast::Expr::Literal(literal) => {
+                literal.numeric_value(db).and_then(|v| v.to_i64()).and_then(|v| v.to_usize())
+            }
+            _ => None,
+        },
+        _ => None,
+    }
+    .on_none(|| {
         diagnostics.push(PluginDiagnostic::error(
             attr.args_stable_ptr.untyped(),
             format!(
-                "Attribute should have a single numeric literal argument or `{STATIC_GAS_ARG}`."
+                "Attribute should have a single non-negative literal in `i64` range or \
+                 `{STATIC_GAS_ARG}`."
             ),
         ))
-    };
-    match &attr.args[..] {
-        [
-            AttributeArg {
-                variant: AttributeArgVariant::Unnamed { value: ast::Expr::Literal(literal), .. },
-                ..
-            },
-        ] => literal.numeric_value(db).and_then(|v| v.to_usize()).on_none(add_malformed_attr_diag),
-        [
-            AttributeArg {
-                variant: AttributeArgVariant::Unnamed { value: ast::Expr::Path(path), .. },
-                ..
-            },
-        ] if path.as_syntax_node().get_text_without_trivia(db) == STATIC_GAS_ARG => None,
-        _ => {
-            add_malformed_attr_diag();
-            None
-        }
-    }
+    })
 }
 
 /// Tries to extract the expected panic bytes out of the given `should_panic` attribute.
```
