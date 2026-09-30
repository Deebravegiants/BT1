# [?] fix: prevent stack overflow on deeply nested blocks (#13184)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-26
Source: https://github.com/noir-lang/noir/commit/f212af7085032e3022900637ad29eef7b323e39c
Type: security-commit

## Details
fix: prevent stack overflow on deeply nested blocks (#13184)

## Patch
### compiler/noirc_frontend/src/parser/parser/expression.rs
```diff
@@ -1122,7 +1122,10 @@ impl Parser<'_> {
             return None;
         }
 
-        Some(self.parse_block_after_left_brace())
+        // Guard against deeply nested blocks overflowing the stack. On overflow this
+        // emits a recursion-depth error and skips to a recovery point, so `None` here
+        // means the block was abandoned rather than absent.
+        self.with_max_recursion_depth_guard(|this| Some(this.parse_block_after_left_brace()))
     }
 
     fn parse_block_after_left_brace(&mut self) -> BlockExpression {
```

### compiler/noirc_frontend/src/tests/deeply_nested.rs
```diff
@@ -256,3 +256,21 @@ fn deeply_nested_expression_parser_overflow() {
 
     assert_parser_max_recursion_depth(&src, Some(1));
 }
+
+// stack overflow in the parser
+#[test]
+fn deeply_nested_blocks() {
+    // Creates: { { { ... { 0 } ... } } }
+    const DEPTH: usize = 2000;
+    let src = format!(
+        r#"
+    pub fn main() {{
+        {open}0{close}
+    }}
+    "#,
+        open = "{".repeat(DEPTH),
+        close = "}".repeat(DEPTH),
+    );
+
+    assert_parser_max_recursion_depth(&src, None);
+}
```
