# [?] fix: avoid indent underflow panic when pretty-printing an unmatched right brace (#13177)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-25
Source: https://github.com/noir-lang/noir/commit/45e4c76f1fda00e5c5a9880a9baf095f2cbba627
Type: security-commit

## Details
fix: avoid indent underflow panic when pretty-printing an unmatched right brace (#13177)

## Patch
### compiler/noirc_frontend/src/hir/comptime/display.rs
```diff
@@ -284,7 +284,10 @@ impl<'interner> TokenPrettyPrinter<'interner> {
             Token::RightBrace => {
                 self.last_was_right_brace = true;
                 writeln!(f)?;
-                self.indent -= 1;
+                // Saturate the decrement so an unmatched right brace (e.g. a malformed quoted
+                // token stream being formatted for a recoverable parse-error diagnostic) does not
+                // underflow the `usize` indent counter and panic the compiler.
+                self.indent = self.indent.saturating_sub(1);
                 self.write_indent(f)?;
                 write!(f, "}}")
             }
@@ -1105,3 +1108,26 @@ fn remove_interned_in_pattern(interner: &NodeInterner, pattern: Pattern) -> Patt
         Pattern::Interned(id, _) => interner.get_pattern(id).clone(),
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use fm::FileMap;
+    use noirc_errors::Location;
+
+    use crate::node_interner::NodeInterner;
+    use crate::token::{LocatedToken, Token};
+
+    use super::tokens_to_string;
+
+    #[test]
+    fn tokens_to_string_handles_unmatched_right_brace() {
+        let interner = NodeInterner::default();
+        let files = FileMap::default();
+        let tokens = [LocatedToken::new(Token::RightBrace, Location::dummy())];
+
+        // An unmatched right brace must not underflow the indent counter and panic; it should
+        // simply be rendered as a closing brace.
+        let result = tokens_to_string(&tokens, &interner, &files);
+        assert_eq!(result.trim(), "}");
+    }
+}
```
