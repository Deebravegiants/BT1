# [?] Orizi/prevent inline macro panic (#3394)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-06-13
Source: https://github.com/starkware-libs/cairo/commit/c86ac3218f19b9cab2e9a3255bb3fbc40393186e
Type: security-commit

## Details
Orizi/prevent inline macro panic (#3394)

## Patch
### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -243,13 +243,10 @@ pub fn maybe_compute_expr_semantic(
         ast::Expr::If(expr_if) => compute_expr_if_semantic(ctx, expr_if),
         ast::Expr::Loop(expr_loop) => compute_expr_loop_semantic(ctx, expr_loop),
         ast::Expr::ErrorPropagate(expr) => compute_expr_error_propagate_semantic(ctx, expr),
-        ast::Expr::Missing(_) | ast::Expr::FieldInitShorthand(_) => {
+        ast::Expr::Missing(_) | ast::Expr::FieldInitShorthand(_) | ast::Expr::InlineMacro(_) => {
             Err(ctx.diagnostics.report(syntax, Unsupported))
         }
         ast::Expr::Indexed(expr) => compute_expr_indexed_semantic(ctx, expr),
-        ast::Expr::InlineMacro(_) => {
-            unreachable!("Inline marcos must be expanded before the semantic pass")
-        }
     }
 }
 
```
