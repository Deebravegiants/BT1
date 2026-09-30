# [?] fix(fuzz): Avoid overflow in `gen_unary` (#9024)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-26
Source: https://github.com/noir-lang/noir/commit/301d86ead94835841e0fc14781a37c28c5afd926
Type: security-commit

## Details
fix(fuzz): Avoid overflow in `gen_unary` (#9024)

## Patch
### tooling/ast_fuzzer/src/program/func.rs
```diff
@@ -715,12 +715,17 @@ impl<'a> FunctionContext<'a> {
         typ: &Type,
         max_depth: usize,
     ) -> arbitrary::Result<Option<TrackedExpression>> {
+        // Negation can cause overflow: for example `-1*i8::MIN` does not fit into `i8`, because `i8` is [-128, 127].
+        let avoid_overflow = self.ctx.config.avoid_overflow || self.in_no_dynamic;
+
         let mut make_unary = |op| {
             self.gen_expr(u, typ, max_depth.saturating_sub(1), Flags::NESTED)
                 .map(|(rhs, is_dyn)| Some((expr::unary(op, rhs, typ.clone()), is_dyn)))
         };
-        if types::is_numeric(typ) {
-            // Assume we already checked with `can_unary_return` that it's signed.
+
+        if matches!(typ, Type::Field)
+            || matches!(typ, Type::Integer(Signedness::Signed, _)) && !avoid_overflow
+        {
             make_unary(UnaryOp::Minus)
         } else if types::is_bool(typ) {
             make_unary(UnaryOp::Not)
```
