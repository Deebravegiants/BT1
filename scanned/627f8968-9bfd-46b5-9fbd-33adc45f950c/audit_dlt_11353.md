# [?] fix: Fix panic when returning a zeroed unit value (#4797)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-04-12
Source: https://github.com/noir-lang/noir/commit/2ea92926956658ea99d8fb97734831eba00d3a4b
Type: security-commit

## Details
fix: Fix panic when returning a zeroed unit value (#4797)

# Description

## Problem\*

Resolves #4791

## Summary\*

Zeroed used boolean values since we didn't have true unit values before.
These were meant to be filtered out by the type but as shown in the
issue, they'd still be used if they were directly returned.

## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -241,6 +241,7 @@ impl<'a> FunctionContext<'a> {
 
                 Ok(Tree::Branch(vec![string, field_count.into(), fields]))
             }
+            ast::Literal::Unit => Ok(Self::unit_value()),
         }
     }
 
```

### compiler/noirc_frontend/src/monomorphization/ast.rs
```diff
@@ -92,6 +92,7 @@ pub enum Literal {
     Slice(ArrayLiteral),
     Integer(FieldElement, Type, Location),
     Bool(bool),
+    Unit,
     Str(String),
     FmtStr(String, u64, Box<Expression>),
 }
```

### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -1553,9 +1553,7 @@ impl<'interner> Monomorphizer<'interner> {
                 ast::Expression::Literal(ast::Literal::Integer(0_u128.into(), typ, location))
             }
             ast::Type::Bool => ast::Expression::Literal(ast::Literal::Bool(false)),
-            // There is no unit literal currently. Replace it with 'false' since it should be ignored
-            // anyway.
-            ast::Type::Unit => ast::Expression::Literal(ast::Literal::Bool(false)),
+            ast::Type::Unit => ast::Expression::Literal(ast::Literal::Unit),
             ast::Type::Array(length, element_type) => {
                 let element = self.zeroed_value_of_type(element_type.as_ref(), location);
                 ast::Expression::Literal(ast::Literal::Array(ast::ArrayLiteral {
```

### compiler/noirc_frontend/src/monomorphization/printer.rs
```diff
@@ -110,6 +110,9 @@ impl AstPrinter {
                 s.fmt(f)?;
                 write!(f, "\"")
             }
+            super::ast::Literal::Unit => {
+                write!(f, "()")
+            }
         }
     }
 
```

### test_programs/execution_success/unit_value/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "short"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.23.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/unit_value/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn get_transaction() {
+    dep::std::unsafe::zeroed()
+}
+
+fn main() {
+    get_transaction();
+}
```
