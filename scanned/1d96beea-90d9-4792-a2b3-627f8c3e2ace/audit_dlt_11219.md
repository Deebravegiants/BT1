# [?] fix(nargo_fmt): format `&&` as two reference layers instead of panicking (#13762)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-09-17
Source: https://github.com/noir-lang/noir/commit/92ec619cd769974d542a39b86735aea3f132fcc9
Type: security-commit

## Details
fix(nargo_fmt): format `&&` as two reference layers instead of panicking (#13762)

## Patch
### tooling/nargo_fmt/src/formatter/expression.rs
```diff
@@ -784,17 +784,35 @@ impl ChunkFormatter<'_, '_> {
 
     fn format_prefix(&mut self, prefix: PrefixExpression) -> ChunkGroup {
         let mut group = ChunkGroup::new();
+
+        // `&&x` lexes as a single `LogicalAnd`, which the parser reads back as two nested
+        // reference prefixes (`parse_unary`). That one token carries both ampersands, so
+        // write it once and continue with the inner prefix, whose own ampersand it covered.
+        let (prefix, operator_written) = if matches!(prefix.operator, UnaryOp::Reference { .. })
+            && self.is_at(Token::LogicalAnd)
+        {
+            group.text(self.chunk(|formatter| {
+                formatter.write_current_token();
+                formatter.bump();
+            }));
+            let ExpressionKind::Prefix(inner) = prefix.rhs.kind else {
+                unreachable!("`&&` parses as two nested reference prefixes")
+            };
+            (*inner, true)
+        } else {
+            (prefix, false)
+        };
+
         group.text(self.chunk(|formatter| {
-            if let UnaryOp::Reference { mutable: true } = prefix.operator {
+            if !operator_written {
                 formatter.write_current_token();
                 formatter.bump();
+            }
+            if let UnaryOp::Reference { mutable: true } = prefix.operator {
                 formatter.skip_comments_and_whitespace();
                 formatter.write_current_token();
                 formatter.bump();
                 formatter.write_space();
-            } else {
-                formatter.write_current_token();
-                formatter.bump();
             }
         }));
         self.format_expression(prefix.rhs, &mut group);
@@ -1790,6 +1808,27 @@ global y = 1;
         assert_format(src, expected);
     }
 
+    #[test]
+    fn format_double_reference_prefix() {
+        let src = "global x = & & a ;";
+        let expected = "global x = &&a;\n";
+        assert_format(src, expected);
+    }
+
+    #[test]
+    fn format_double_reference_prefix_written_as_one_token() {
+        let src = "global x = &&a ;";
+        let expected = "global x = &&a;\n";
+        assert_format(src, expected);
+    }
+
+    #[test]
+    fn format_reference_to_mutable_reference_prefix() {
+        let src = "global x = &&  mut  a ;";
+        let expected = "global x = &&mut a;\n";
+        assert_format(src, expected);
+    }
+
     #[test]
     fn format_infix() {
         let src = "global x =  a  +  b  ;";
```

### tooling/nargo_fmt/src/formatter/types.rs
```diff
@@ -69,12 +69,20 @@ impl Formatter<'_> {
                 self.format_generic_type_args(generic_type_args);
             }
             UnresolvedTypeData::Reference(typ, mutable) => {
-                self.write_token(Token::Ampersand);
-                if mutable {
-                    self.write_keyword(Keyword::Mut);
-                    self.write_space();
+                // `&&T` lexes as a single `LogicalAnd`, which the parser reads back as two
+                // reference layers (`parse_reference_type`). That one token carries both
+                // ampersands, so write it once and continue with the inner layer rather
+                // than letting it ask for an ampersand that is no longer in the stream.
+                if self.is_at(Token::LogicalAnd) {
+                    self.write_token(Token::LogicalAnd);
+                    let UnresolvedTypeData::Reference(inner, inner_mutable) = typ.typ else {
+                        unreachable!("`&&` parses as two reference layers")
+                    };
+                    self.format_reference_target(*inner, inner_mutable);
+                } else {
+                    self.write_token(Token::Ampersand);
+                    self.format_reference_target(*typ, mutable);
                 }
-                self.format_type(*typ);
             }
             UnresolvedTypeData::Tuple(types) => {
                 let types_len = types.len();
@@ -147,6 +155,15 @@ impl Formatter<'_> {
         }
     }
 
+    /// Write what follows a reference's `&`: an optional `mut`, then the referenced type.
+    fn format_reference_target(&mut self, typ: UnresolvedType, mutable: bool) {
+        if mutable {
+            self.write_keyword(Keyword::Mut);
+            self.write_space();
+        }
+        self.format_type(typ);
+    }
+
     pub(super) fn format_as_trait_path(&mut self, as_trait_path: AsTraitPath) {
         self.write_token(Token::Less);
         self.format_type(as_trait_path.typ);
@@ -276,6 +293,34 @@ mod tests {
         assert_format_type(src, expected);
     }
 
+    #[test]
+    fn format_double_reference_type() {
+        let src = " & & Field ";
+        let expected = "&&Field";
+        assert_format_type(src, expected);
+    }
+
+    #[test]
+    fn format_double_reference_type_written_as_one_token() {
+        let src = " &&Field ";
+        let expected = "&&Field";
+        assert_format_type(src, expected);
+    }
+
+    #[test]
+    fn format_reference_to_mutable_reference_type() {
+        let src = " &&  mut  Field ";
+        let expected = "&&mut Field";
+        assert_format_type(src, expected);
+    }
+
+    #[test]
+    fn format_triple_reference_type() {
+        let src = " &&&mut Field ";
+        let expected = "&&&mut Field";
+        assert_format_type(src, expected);
+    }
+
     #[test]
     fn format_array_reference_type() {
         let src = " &[ Field ; 3 ]";
```
