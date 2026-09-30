# [?] fix: panic in nested closure. (#7967)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-07-15
Source: https://github.com/starkware-libs/cairo/commit/dc4ef5708139fd38d99e6b4dec529775c54c65d7
Type: security-commit

## Details
fix: panic in nested closure. (#7967)

## Patch
### crates/cairo-lang-lowering/src/lower/context.rs
```diff
@@ -272,6 +272,12 @@ impl LoweredExpr {
                 Ok(builder.get_ref(ctx, &member_path).unwrap())
             }
             LoweredExpr::Snapshot { expr, location } => {
+                if let LoweredExpr::Member(member_path, _location) = &*expr {
+                    if let Some(var_usage) = builder.get_snap_ref(ctx, member_path) {
+                        return Ok(VarUsage { var_id: var_usage.var_id, location });
+                    }
+                }
+
                 let input = expr.clone().as_var_usage(ctx, builder)?;
                 let (original, snapshot) =
                     generators::Snapshot { input, location }.add(ctx, &mut builder.statements);
```

### crates/cairo-lang-lowering/src/lower/mod.rs
```diff
@@ -1174,31 +1174,8 @@ fn lower_expr_snapshot(
     builder: &mut BlockBuilder,
 ) -> LoweringResult<LoweredExpr> {
     log::trace!("Lowering a snapshot: {:?}", expr.debug(&ctx.expr_formatter));
-    // If the inner expression is a variable, or a member access, and we already have a snapshot var
-    // we can use it without creating a new one.
-    // Note that in a closure we might only have a snapshot of the variable and not the original.
-    match &ctx.function_body.arenas.exprs[expr.inner] {
-        semantic::Expr::Var(expr_var) => {
-            let member_path = ExprVarMemberPath::Var(expr_var.clone());
-            if let Some(var) = builder.get_snap_ref(ctx, &member_path) {
-                return Ok(LoweredExpr::AtVariable(var));
-            }
-        }
-        semantic::Expr::MemberAccess(expr) => {
-            if let Some(var) = expr
-                .member_path
-                .clone()
-                .and_then(|member_path| builder.get_snap_ref(ctx, &member_path))
-            {
-                return Ok(LoweredExpr::AtVariable(var));
-            }
-        }
-        _ => {}
-    }
-    let lowered = lower_expr(ctx, builder, expr.inner)?;
-
     let location = ctx.get_location(expr.stable_ptr.untyped());
-    let expr = Box::new(lowered);
+    let expr = Box::new(lower_expr(ctx, builder, expr.inner)?);
     Ok(LoweredExpr::Snapshot { expr, location })
 }
 
```

### crates/cairo-lang-lowering/src/lower/test_data/closure
```diff
@@ -597,3 +597,206 @@ Statements:
   (v27: core::felt252) <- core::felt252_add(v22, v26)
 End:
   Return(v27)
+
+//! > ==========================================================================
+
+//! > Test Nested closure
+
+//! > test_runner_name
+test_generated_function
+
+//! > function
+fn foo(a: Array<felt252>) -> u32 {
+    let inner = |x| {
+        let nested = |y| {
+            y + a.len()
+        };
+        nested(x)
+    };
+    inner(42)
+}
+
+//! > function_name
+foo
+
+//! > module_code
+
+//! > semantic_diagnostics
+
+//! > lowering_diagnostics
+
+//! > lowering
+Main:
+Parameters: v0: core::array::Array::<core::felt252>
+blk0 (root):
+Statements:
+  (v1: core::array::Array::<core::felt252>, v2: @core::array::Array::<core::felt252>) <- snapshot(v0)
+  (v3: {closure@lib.cairo:2:17: 2:20}) <- struct_construct(v2)
+  (v4: {closure@lib.cairo:2:17: 2:20}, v5: @{closure@lib.cairo:2:17: 2:20}) <- snapshot(v3)
+  (v6: core::integer::u32) <- 42
+  (v7: (core::integer::u32,)) <- struct_construct(v6)
+  (v8: core::integer::u32) <- Generated `core::ops::function::Fn::call` for {closure@lib.cairo:2:17: 2:20}(v5, v7)
+End:
+  Return(v8)
+
+
+Final lowering:
+Parameters: v0: core::RangeCheck, v1: core::array::Array::<core::felt252>
+blk0 (root):
+Statements:
+  (v2: core::array::Array::<core::felt252>, v3: @core::array::Array::<core::felt252>) <- snapshot(v1)
+  (v4: core::integer::u32) <- core::array::array_len::<core::felt252>(v3)
+  (v5: core::integer::u32) <- 42
+End:
+  Match(match core::integer::u32_overflowing_add(v0, v5, v4) {
+    Result::Ok(v6, v7) => blk1,
+    Result::Err(v8, v9) => blk2,
+  })
+
+blk1:
+Statements:
+  (v10: (core::integer::u32,)) <- struct_construct(v7)
+  (v11: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Ok(v10)
+End:
+  Return(v6, v11)
+
+blk2:
+Statements:
+  (v12: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<155785504323917466144735657540098748279>()
+  (v13: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v12)
+End:
+  Return(v8, v13)
+
+
+Generated core::traits::Destruct::destruct lowering for source location:
+    let inner = |x| {
+                ^^^
+
+Parameters: v0: {closure@lib.cairo:2:17: 2:20}
+blk0 (root):
+Statements:
+  (v1: @core::array::Array::<core::felt252>) <- struct_destructure(v0)
+  (v2: ()) <- struct_construct()
+End:
+  Return(v2)
+
+
+Final lowering:
+Parameters: v0: {closure@lib.cairo:2:17: 2:20}
+blk0 (root):
+Statements:
+End:
+  Return()
+
+
+Generated core::traits::Destruct::destruct lowering for source location:
+        let nested = |y| {
+                     ^^^
+
+Parameters: v0: {closure@lib.cairo:3:22: 3:25}
+blk0 (root):
+Statements:
+  (v1: @core::array::Array::<core::felt252>) <- struct_destructure(v0)
+  (v2: ()) <- struct_construct()
+End:
+  Return(v2)
+
+
+Final lowering:
+Parameters: v0: {closure@lib.cairo:3:22: 3:25}
+blk0 (root):
+Statements:
+End:
+  Return()
+
+
+Generated core::ops::function::Fn::call lowering for source location:
+        let nested = |y| {
+                     ^^^
+
+Parameters: v0: @{closure@lib.cairo:3:22: 3:25}, v2: (core::integer::u32,)
+blk0 (root):
+Statements:
+  (v1: {closure@lib.cairo:3:22: 3:25}) <- desnap(v0)
+  (v3: @core::array::Array::<core::felt252>) <- struct_destructure(v1)
+  (v4: core::integer::u32) <- struct_destructure(v2)
+  (v5: core::integer::u32) <- core::array::ArrayImpl::<core::felt252>::len(v3)
+  (v6: core::integer::u32) <- core::integer::U32Add::add(v4, v5)
+End:
+  Return(v6)
+
+
+Final lowering:
+Parameters: v0: core::RangeCheck, v1: @{closure@lib.cairo:3:22: 3:25}, v2: (core::integer::u32,)
+blk0 (root):
+Statements:
+  (v3: {closure@lib.cairo:3:22: 3:25}) <- desnap(v1)
+  (v4: @core::array::Array::<core::felt252>) <- struct_destructure(v3)
+  (v5: core::integer::u32) <- core::array::array_len::<core::felt252>(v4)
+  (v6: core::integer::u32) <- struct_destructure(v2)
+End:
+  Match(match core::integer::u32_overflowing_add(v0, v6, v5) {
+    Result::Ok(v7, v8) => blk1,
+    Result::Err(v9, v10) => blk2,
+  })
+
+blk1:
+Statements:
+  (v11: (core::integer::u32,)) <- struct_construct(v8)
+  (v12: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Ok(v11)
+End:
+  Return(v7, v12)
+
+blk2:
+Statements:
+  (v13: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<155785504323917466144735657540098748279>()
+  (v14: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v13)
+End:
+  Return(v9, v14)
+
+
+Generated core::ops::function::Fn::call lowering for source location:
+    let inner = |x| {
+                ^^^
+
+Parameters: v0: @{closure@lib.cairo:2:17: 2:20}, v2: (core::integer::u32,)
+blk0 (root):
+Statements:
+  (v1: {closure@lib.cairo:2:17: 2:20}) <- desnap(v0)
+  (v3: @core::array::Array::<core::felt252>) <- struct_destructure(v1)
+  (v4: core::integer::u32) <- struct_destructure(v2)
+  (v5: {closure@lib.cairo:3:22: 3:25}) <- struct_construct(v3)
+  (v6: {closure@lib.cairo:3:22: 3:25}, v7: @{closure@lib.cairo:3:22: 3:25}) <- snapshot(v5)
+  (v8: (core::integer::u32,)) <- struct_construct(v4)
+  (v9: core::integer::u32) <- Generated `core::ops::function::Fn::call` for {closure@lib.cairo:3:22: 3:25}(v7, v8)
+End:
+  Return(v9)
+
+
+Final lowering:
+Parameters: v0: core::RangeCheck, v1: @{closure@lib.cairo:2:17: 2:20}, v2: (core::integer::u32,)
+blk0 (root):
+Statements:
+  (v3: {closure@lib.cairo:2:17: 2:20}) <- desnap(v1)
+  (v4: @core::array::Array::<core::felt252>) <- struct_destructure(v3)
+  (v5: core::integer::u32) <- core::array::array_len::<core::felt252>(v4)
+  (v6: core::integer::u32) <- struct_destructure(v2)
+End:
+  Match(match core::integer::u32_overflowing_add(v0, v6, v5) {
+    Result::Ok(v7, v8) => blk1,
+    Result::Err(v9, v10) => blk2,
+  })
+
+blk1:
+Statements:
+  (v11: (core::integer::u32,)) <- struct_construct(v8)
+  (v12: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Ok(v11)
+End:
+  Return(v7, v12)
+
+blk2:
+Statements:
+  (v13: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<155785504323917466144735657540098748279>()
+  (v14: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v13)
+End:
+  Return(v9, v14)
```
