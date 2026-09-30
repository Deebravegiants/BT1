# [?] fix: don't crash on untyped global used as array length (#6076)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-09-18
Source: https://github.com/noir-lang/noir/commit/426f2955cbe4f086581d05eea7d06c47e0491195
Type: security-commit

## Details
fix: don't crash on untyped global used as array length (#6076)

# Description

## Problem

Resolves #6046

## Summary

Another case of an unhandled`DefinitionId::dummy()`.

## Additional Context


## Documentation

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/elaborator/types.rs
```diff
@@ -655,18 +655,21 @@ impl<'context> Elaborator<'context> {
                 int.try_into_u128().ok_or(Some(ResolverError::IntegerTooLarge { span }))
             }
             HirExpression::Ident(ident, _) => {
-                let definition = self.interner.definition(ident.id);
-                match definition.kind {
-                    DefinitionKind::Global(global_id) => {
-                        let let_statement = self.interner.get_global_let_statement(global_id);
-                        if let Some(let_statement) = let_statement {
-                            let expression = let_statement.expression;
-                            self.try_eval_array_length_id_with_fuel(expression, span, fuel - 1)
-                        } else {
-                            Err(Some(ResolverError::InvalidArrayLengthExpr { span }))
+                if let Some(definition) = self.interner.try_definition(ident.id) {
+                    match definition.kind {
+                        DefinitionKind::Global(global_id) => {
+                            let let_statement = self.interner.get_global_let_statement(global_id);
+                            if let Some(let_statement) = let_statement {
+                                let expression = let_statement.expression;
+                                self.try_eval_array_length_id_with_fuel(expression, span, fuel - 1)
+                            } else {
+                                Err(Some(ResolverError::InvalidArrayLengthExpr { span }))
+                            }
                         }
+                        _ => Err(Some(ResolverError::InvalidArrayLengthExpr { span })),
                     }
-                    _ => Err(Some(ResolverError::InvalidArrayLengthExpr { span })),
+                } else {
+                    Err(Some(ResolverError::InvalidArrayLengthExpr { span }))
                 }
             }
             HirExpression::Infix(infix) => {
```

### test_programs/compile_failure/global_without_a_type_used_as_array_length/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "global_without_a_type_used_as_array_length"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.33.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/global_without_a_type_used_as_array_length/src/main.nr
```diff
@@ -0,0 +1,2 @@
+global BAR = OOPS;
+global X: [Field; BAR] = [];
```
