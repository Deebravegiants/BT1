# [?] fix(fuzz): Avoid overflowing binary ops in "no dynamic" mode (#8996)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-24
Source: https://github.com/noir-lang/noir/commit/f9b66d65e74b6103a72c5caed33871c5394c904d
Type: security-commit

## Details
fix(fuzz): Avoid overflowing binary ops in "no dynamic" mode (#8996)

## Patch
### tooling/ast_fuzzer/src/program/func.rs
```diff
@@ -737,11 +737,14 @@ impl<'a> FunctionContext<'a> {
         max_depth: usize,
     ) -> arbitrary::Result<Option<TrackedExpression>> {
         // Collect the operations can return the expected type.
+        // Avoid operations that can fail in no-dynamic mode, otherwise they will be considered non-constant indexes.
         let ops = BinaryOp::iter()
             .filter(|op| {
                 types::can_binary_op_return(op, typ)
-                    && (!self.ctx.config.avoid_overflow || !types::can_binary_op_overflow(op))
-                    && (!self.ctx.config.avoid_err_by_zero || !types::can_binary_op_err_by_zero(op))
+                    && (!(self.ctx.config.avoid_overflow || self.in_no_dynamic)
+                        || !types::can_binary_op_overflow(op))
+                    && (!(self.ctx.config.avoid_err_by_zero || self.in_no_dynamic)
+                        || !types::can_binary_op_err_by_zero(op))
             })
             .collect::<Vec<_>>();
 
```
