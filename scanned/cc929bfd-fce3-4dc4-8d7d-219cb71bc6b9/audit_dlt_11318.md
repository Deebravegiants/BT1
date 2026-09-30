# [?] fix: Do not panic if RHS constant in division has more bits than the operand (#8197)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-04-24
Source: https://github.com/noir-lang/noir/commit/bddf22d2f0e2b26c81a6856a41c245137f7dfc1c
Type: security-commit

## Details
fix: Do not panic if RHS constant in division has more bits than the operand (#8197)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/mod.rs
```diff
@@ -830,12 +830,16 @@ impl<F: AcirField, B: BlackBoxFunctionSolver<F>> AcirContext<F, B> {
         let (max_q_bits, max_rhs_bits) = if let Some(rhs_const) = rhs_expr.to_const() {
             // when rhs is constant, we can better estimate the maximum bit sizes
             let max_rhs_bits = rhs_const.num_bits();
-            assert!(
-                max_rhs_bits <= bit_size,
-                "attempted to divide by constant larger than operand type"
-            );
 
-            let max_q_bits = bit_size - max_rhs_bits + 1;
+            // It is possible that we have an AcirVar which is a result of a multiplication of constants
+            // which resulted in an overflow, but that check will only happen at runtime, and here we
+            // can't assume that the RHS will never have more bits than the operand.
+            let max_q_bits = if max_rhs_bits > bit_size {
+                // Ignore what we know about the constant and let the runtime handle it.
+                bit_size
+            } else {
+                bit_size - max_rhs_bits + 1
+            };
             (max_q_bits, max_rhs_bits)
         } else {
             (bit_size, bit_size)
```

### test_programs/execution_failure/regression_8195/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_8195"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/regression_8195/Prover.toml
```diff
@@ -0,0 +1 @@
+a = 0
```

### test_programs/execution_failure/regression_8195/src/main.nr
```diff
@@ -0,0 +1,4 @@
+global G_A: u16 = 41618;
+fn main(a: u16) -> pub u16 {
+    ((13834 - a) % (G_A * G_A))
+}
```
