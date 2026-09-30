# [?] (bug fix): preserve escapes in simple panic! macro expansion (#9980)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-05-24
Source: https://github.com/starkware-libs/cairo/commit/f53b0432de4a00451449457de770e7c74ce37122
Type: security-commit

## Details
(bug fix): preserve escapes in simple panic! macro expansion (#9980)

## Patch
### corelib/src/test/language_features/panics_test.cairo
```diff
@@ -142,6 +142,18 @@ fn test_panic_macro_with_input() {
     panic!("some_format({})", 1)
 }
 
+#[test]
+#[should_panic(expected: "has a \"quote\" inside")]
+fn test_panic_macro_with_escaped_quote() {
+    panic!("has a \"quote\" inside")
+}
+
+#[test]
+#[should_panic(expected: "backslash: \\end")]
+fn test_panic_macro_with_backslash() {
+    panic!("backslash: \\end")
+}
+
 
 #[test]
 #[should_panic(expected: 'PanicDestruct')]
```

### crates/cairo-lang-semantic/src/inline_macros/panic.rs
```diff
@@ -21,23 +21,23 @@ fn try_handle_simple_panic(
     builder: &mut PatchBuilder<'_>,
     arguments: &[Arg<'_>],
 ) -> Option<()> {
+    // Source text of the format-string literal — outer quotes and escape sequences as-typed.
+    // Using the source (not `string_value`, which decodes escapes) avoids breaking the
+    // surrounding `@"..."` when the literal contains `"` or `\`.
     let panic_str = match arguments {
-        [] => {
-            // Trivial panic!() with no arguments case.
-            "".to_string()
-        }
+        [] => "\"\"".to_string(),
         [arg] => {
             let unnamed_arg = try_extract_unnamed_arg(db, arg)?;
             let format_string_expr = try_extract_matches!(unnamed_arg, ast::Expr::String)?;
             let format_string = format_string_expr.string_value(db)?;
             require(format_string.find(['{', '}']).is_none())?;
-            format_string
+            format_string_expr.as_syntax_node().get_text_without_trivia(db).long(db).to_string()
         }
         // We have more than one argument, fallback to more generic handling.
         _ => return None,
     };
 
-    builder.add_str(&format!("core::panics::panic_with_byte_array(@\"{panic_str}\")"));
+    builder.add_str(&format!("core::panics::panic_with_byte_array(@{panic_str})"));
     Some(())
 }
 
```
