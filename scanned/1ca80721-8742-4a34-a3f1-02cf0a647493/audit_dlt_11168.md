# [?] fix: reject @locals values that overflow word-alignment calculation (#2838)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-03-15
Source: https://github.com/0xMiden/miden-vm/commit/9d50a65411fab320189d8e63dd2104496d554bd6
Type: security-commit

## Details
fix: reject @locals values that overflow word-alignment calculation (#2838)

When @locals(65535) (or 65533/65534) is specified, the word-alignment
rounding `num_locals.next_multiple_of(4)` overflows u16, causing a
panic in debug builds or wrapping to 0 in release builds.

Add a bounds check in the parser that rejects @locals values above
65532 (the largest u16 value that can be safely rounded up to a
multiple of 4) with a descriptive error message.

## Patch
### crates/assembly-syntax/src/ast/tests.rs
```diff
@@ -961,6 +961,37 @@ fn test_ast_parsing_simple_docs() -> Result<(), Report> {
     Ok(())
 }
 
+#[test]
+fn locals_overflow_rejected() {
+    let context = SyntaxTestContext::new();
+    let source = source_file!(
+        &context,
+        r#"
+    @locals(65535)
+    pub proc foo
+        push.1
+    end"#
+    );
+
+    assert_parse_diagnostic!(source, "number of locals exceeds the maximum of 65532");
+}
+
+#[test]
+fn locals_max_valid_accepted() -> Result<(), Report> {
+    let context = SyntaxTestContext::new();
+    let source = source_file!(
+        &context,
+        r#"
+    @locals(65532)
+    pub proc foo
+        push.1
+    end"#
+    );
+
+    context.parse_forms(source)?;
+    Ok(())
+}
+
 #[test]
 fn test_ast_parsing_module_docs_valid() {
     let context = SyntaxTestContext::new();
```

### crates/assembly-syntax/src/parser/grammar.lalrpop
```diff
@@ -728,13 +728,27 @@ Proc: Form = {
                                     error: ParsingError::InvalidLocalsAttr { span: other.span(), message: "expected an integer literal".into() },
                                 }),
                             };
-                            if valid_num_locals.is_some() {
-                                num_locals = valid_num_locals;
-                                entry.insert(Attribute::List(list));
-                            } else {
-                                return Err(ParseError::User {
-                                    error: ParsingError::ImmediateOutOfRange { span: list.span(), range: 0..((u16::MAX as usize) + 1) },
-                                });
+                            match valid_num_locals {
+                                // Reject values that would overflow the word-alignment
+                                // rounding (next_multiple_of(4) exceeds u16::MAX for
+                                // values above 65532)
+                                Some(n) if n > (u16::MAX / 4) * 4 => {
+                                    return Err(ParseError::User {
+                                        error: ParsingError::InvalidLocalsAttr {
+                                            span: list.span(),
+                                            message: "number of locals exceeds the maximum of 65532".to_string(),
+                                        },
+                                    });
+                                }
+                                Some(_) => {
+                                    num_locals = valid_num_locals;
+                                    entry.insert(Attribute::List(list));
+                                }
+                                None => {
+                                    return Err(ParseError::User {
+                                        error: ParsingError::ImmediateOutOfRange { span: list.span(), range: 0..((u16::MAX as usize) + 1) },
+                                    });
+                                }
                             }
                         }
                         AttributeSetEntry::Occupied(entry) => {
```
