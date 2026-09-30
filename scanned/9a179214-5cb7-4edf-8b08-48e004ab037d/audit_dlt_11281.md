# [?] fix(parser): don't crash on incomplete type alias (#10421)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-07
Source: https://github.com/noir-lang/noir/commit/9336ae61814f3f480cf5f30ba4cb5e2c3f80edc2
Type: security-commit

## Details
fix(parser): don't crash on incomplete type alias (#10421)

## Patch
### compiler/noirc_frontend/src/parser/parser/type_alias.rs
```diff
@@ -47,7 +47,10 @@ impl Parser<'_> {
             }
         } else {
             expr_location = self.current_token_location;
-            let typ = self.parse_type_or_type_expression().unwrap();
+            let typ = self.parse_type_or_type_expression().unwrap_or(UnresolvedType {
+                typ: UnresolvedTypeData::Error,
+                location: expr_location,
+            });
             location = self.location_since(start_location);
             self.eat_semicolon_or_error();
             typ
@@ -69,7 +72,7 @@ impl Parser<'_> {
 #[cfg(test)]
 mod tests {
     use crate::{
-        ast::TypeAlias,
+        ast::{TypeAlias, UnresolvedType, UnresolvedTypeData},
         parse_program_with_dummy_file,
         parser::{ItemKind, parser::tests::expect_no_errors},
     };
@@ -109,4 +112,18 @@ mod tests {
         assert_eq!("Double", alias.name.to_string());
         assert_eq!(alias.generics.len(), 1);
     }
+
+    #[test]
+    fn parse_incomplete_type_alias() {
+        let src = "type Foo = ";
+        let (mut module, errors) = parse_program_with_dummy_file(src);
+        assert!(!errors.is_empty());
+        assert_eq!(module.items.len(), 1);
+        let item = module.items.remove(0);
+        let ItemKind::TypeAlias(alias) = item.kind else {
+            panic!("Expected global");
+        };
+        assert_eq!(alias.name.to_string(), "Foo");
+        assert!(matches!(alias.typ, UnresolvedType { typ: UnresolvedTypeData::Error, .. }));
+    }
 }
```
