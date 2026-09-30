# [?] fix: allow statement-level consts in named argument shorthand instead of panicking (#9814)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-06
Source: https://github.com/starkware-libs/cairo/commit/5b0ef0b0840f5275f711ed1ad7fd19359cc671bf
Type: security-commit

## Details
fix: allow statement-level consts in named argument shorthand instead of panicking (#9814)

## Patch
### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -4120,27 +4120,7 @@ fn resolve_expr_path<'db>(
             is_callsite_prefixed,
             path.stable_ptr(ctx.db).into(),
         ) {
-            match res.clone() {
-                Expr::Var(expr_var) => {
-                    let item = ResolvedGenericItem::Variable(expr_var.var);
-                    ctx.resolver
-                        .data
-                        .resolved_items
-                        .generic
-                        .insert(identifier.stable_ptr(db), item);
-                }
-                Expr::Constant(expr_const) => {
-                    let item = ResolvedConcreteItem::Constant(expr_const.const_value_id);
-                    ctx.resolver
-                        .data
-                        .resolved_items
-                        .concrete
-                        .insert(identifier.stable_ptr(db), item);
-                }
-                _ => unreachable!(
-                    "get_binded_expr_by_name should only return variables or constants"
-                ),
-            };
+            mark_binded_expr_in_resolved_items(ctx, &identifier, &res);
             return Ok(res);
         }
     }
@@ -4193,11 +4173,30 @@ pub fn resolve_variable_by_name<'db>(
     let res = get_binded_expr_by_name(ctx, variable_name, false, stable_ptr).ok_or_else(|| {
         ctx.diagnostics.report(identifier.stable_ptr(ctx.db), VariableNotFound(variable_name))
     })?;
-    let item = ResolvedGenericItem::Variable(extract_matches!(&res, Expr::Var).var);
-    ctx.resolver.data.resolved_items.generic.insert(identifier.stable_ptr(ctx.db), item);
+    mark_binded_expr_in_resolved_items(ctx, identifier, &res);
     Ok(res)
 }
 
+/// Marks a resolved binding expression in the resolved items map for tooling (e.g.,
+/// go-to-definition).
+fn mark_binded_expr_in_resolved_items<'db>(
+    ctx: &mut ComputationContext<'db, '_>,
+    identifier: &ast::TerminalIdentifier<'db>,
+    expr: &Expr<'db>,
+) {
+    let ptr = identifier.stable_ptr(ctx.db);
+    let resolved = &mut ctx.resolver.data.resolved_items;
+    match expr {
+        Expr::Var(expr) => {
+            resolved.generic.insert(ptr, ResolvedGenericItem::Variable(expr.var));
+        }
+        Expr::Constant(expr) => {
+            resolved.concrete.insert(ptr, ResolvedConcreteItem::Constant(expr.const_value_id));
+        }
+        _ => unreachable!("`get_binded_expr_by_name` should only return variables or constants"),
+    }
+}
+
 /// Returns the requested variable from the environment if it exists. Returns None otherwise.
 pub fn get_binded_expr_by_name<'db>(
     ctx: &mut ComputationContext<'db, '_>,
```

### crates/cairo-lang-semantic/src/expr/test_data/function_call
```diff
@@ -300,3 +300,26 @@ error[E2042]: Unexpected return type. Expected: "core::integer::u8", found: "cor
  --> lib.cairo:2:11
     || -> u8 {
           ^^
+
+//! > ==========================================================================
+
+//! > Statement-level const used in named argument shorthand.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: false)
+
+//! > function_code
+fn foo() -> felt252 {
+    const x: felt252 = 42;
+    takes_val(:x)
+}
+
+//! > function_name
+foo
+
+//! > module_code
+fn takes_val(x: felt252) -> felt252 {
+    x
+}
+
+//! > expected_diagnostics
```
