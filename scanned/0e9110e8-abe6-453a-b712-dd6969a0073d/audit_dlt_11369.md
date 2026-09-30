# [?] fix: Fix panic when using repeated arrays which define variables (#3221)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-10-18
Source: https://github.com/noir-lang/noir/commit/c4faf3a0a40eea1ee02e11dfe08b48c6b4438bbf
Type: security-commit

## Details
fix: Fix panic when using repeated arrays which define variables (#3221)

## Patch
### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -412,12 +412,11 @@ impl<'interner> Monomorphizer<'interner> {
     ) -> ast::Expression {
         let typ = self.convert_type(&self.interner.id_type(array));
 
-        let contents = self.expr(repeated_element);
         let length = length
             .evaluate_to_u64()
             .expect("Length of array is unknown when evaluating numeric generic");
 
-        let contents = vec![contents; length as usize];
+        let contents = vecmap(0..length, |_| self.expr(repeated_element));
         ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral { contents, typ }))
     }
 
```

### tooling/nargo_cli/tests/compile_success_empty/let_stmt/src/main.nr
```diff
@@ -7,4 +7,5 @@ fn main() {
     let _ = 42;
 
     let Foo { a: _ } = Foo { a: 42 };
+    let _regression_2786 = [Foo { a: 1 }; 8];
 }
```
