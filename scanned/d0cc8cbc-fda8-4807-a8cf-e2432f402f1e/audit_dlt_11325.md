# [?] fix: avoid stack overflow on many comments in a row (#7325)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-02-07
Source: https://github.com/noir-lang/noir/commit/ac1da8f4b57290a67240973a7d6172cfbf5680a8
Type: security-commit

## Details
fix: avoid stack overflow on many comments in a row (#7325)

## Patch
### compiler/noirc_frontend/src/lexer/lexer.rs
```diff
@@ -103,11 +103,28 @@ impl<'a> Lexer<'a> {
     }
 
     fn next_token(&mut self) -> SpannedTokenResult {
+        if !self.skip_comments {
+            return self.next_token_without_checking_comments();
+        }
+
+        // Read tokens and skip comments. This is done like this to avoid recursion
+        // and hitting stack overflow when there are many comments in a row.
+        loop {
+            let token = self.next_token_without_checking_comments()?;
+            if matches!(token.token(), Token::LineComment(_, None) | Token::BlockComment(_, None)) {
+                continue;
+            }
+            return Ok(token);
+        }
+    }
+
+    /// Reads the next token, which might be a comment token (these aren't skipped in this method)
+    fn next_token_without_checking_comments(&mut self) -> SpannedTokenResult {
         match self.next_char() {
             Some(x) if Self::is_code_whitespace(x) => {
                 let spanned = self.eat_whitespace(x);
                 if self.skip_whitespaces {
-                    self.next_token()
+                    self.next_token_without_checking_comments()
                 } else {
                     Ok(spanned)
                 }
@@ -755,10 +772,6 @@ impl<'a> Lexer<'a> {
             return Err(LexerErrorKind::NonAsciiComment { span });
         }
 
-        if doc_style.is_none() && self.skip_comments {
-            return self.next_token();
-        }
-
         Ok(Token::LineComment(comment, doc_style).into_span(start, self.position))
     }
 
@@ -804,9 +817,6 @@ impl<'a> Lexer<'a> {
                 return Err(LexerErrorKind::NonAsciiComment { span });
             }
 
-            if doc_style.is_none() && self.skip_comments {
-                return self.next_token();
-            }
             Ok(Token::BlockComment(content, doc_style).into_span(start, self.position))
         } else {
             let span = Span::inclusive(start, self.position);
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -4364,3 +4364,9 @@ fn errors_on_if_without_else_type_mismatch() {
     };
     assert!(matches!(**err, TypeCheckError::TypeMismatch { .. }));
 }
+
+#[test]
+fn does_not_stack_overflow_on_many_comments_in_a_row() {
+    let src = "//\n".repeat(10_000);
+    assert_no_errors(&src);
+}
```
