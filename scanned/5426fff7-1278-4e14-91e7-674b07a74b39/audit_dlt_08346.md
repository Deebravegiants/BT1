# [?] Fixing a panic when parsing move code containing `/**/`

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2023-11-23
Source: https://github.com/aptos-labs/aptos-core/commit/52fe311802670284ad13957876f6db700b3a4025
Type: security-commit

## Details
Fixing a panic when parsing move code containing `/**/`

## Patch
### third_party/move/move-compiler/src/parser/lexer.rs
```diff
@@ -212,7 +212,7 @@ impl<'input> Lexer<'input> {
     /// Block comments can be nested.
     ///
     /// Documentation comments are comments which start with
-    /// `///` or `/**`, but not `////` or `/***`. The actually comment delimiters
+    /// `///` or `/**`, but not `////` or `/***`. The actual comment delimiters
     /// (`/// .. <newline>` and `/** .. */`) will be not included in extracted comment string. The
     /// span in the returned map, however, covers the whole region of the comment, including the
     /// delimiters.
@@ -257,10 +257,12 @@ impl<'input> Lexer<'input> {
                         let start = get_offset(text);
                         text = &text[2..];
 
-                        // Check if this is a documentation comment: '/**', but not '/***'.
+                        // Check if this is a documentation comment: '/**', but neither '/***' nor '/**/'.
                         // A documentation comment cannot be nested within another comment.
-                        let is_doc =
-                            text.starts_with('*') && !text.starts_with("**") && locs.is_empty();
+                        let is_doc = text.starts_with('*')
+                            && !text.starts_with("**")
+                            && !text.starts_with("*/")
+                            && locs.is_empty();
 
                         locs.push((start, is_doc));
                     } else if text.starts_with("*/") {
```

### third_party/move/move-compiler/tests/move_check/parser/not_doc_comment.move
```diff
@@ -0,0 +1,5 @@
+module 0xdecafbad::m {
+    /**/
+    fun /**/foo() { }
+    /* /**/ */
+}
```
