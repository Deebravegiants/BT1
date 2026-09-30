# [?] fix(ssa): avoid overflow incrementing u128::MAX (#12500)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-30
Source: https://github.com/noir-lang/noir/commit/6f8db13449779babc50bf20d2f79ce602d967b14
Type: security-commit

## Details
fix(ssa): avoid overflow incrementing u128::MAX (#12500)

Co-authored-by: jfecher <jfecher11@gmail.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ir/integer.rs
```diff
@@ -64,39 +64,27 @@ impl IntegerConstant {
         }
     }
 
-    /// Increment the value by 1
-    ///
-    /// # Panics
-    ///
-    /// Panics if the increment causes an overflow.
-    pub(crate) fn inc(self) -> Self {
+    /// Increment the value by 1. Returns None if the increment would cause an overflow.
+    pub(crate) fn inc(self) -> Option<Self> {
         match self {
-            Self::Signed { value, bit_size } => Self::Signed {
-                value: value.checked_add(1).expect("ICE: overflow while incrementing constant"),
-                bit_size,
-            },
-            Self::Unsigned { value, bit_size } => Self::Unsigned {
-                value: value.checked_add(1).expect("ICE: overflow while incrementing constant"),
-                bit_size,
-            },
+            Self::Signed { value, bit_size } => {
+                value.checked_add(1).map(|value| Self::Signed { value, bit_size })
+            }
+            Self::Unsigned { value, bit_size } => {
+                value.checked_add(1).map(|value| Self::Unsigned { value, bit_size })
+            }
         }
     }
 
-    /// Decrement the value by 1, saturating at the minimum value.
-    ///
-    /// # panics
-    ///
-    /// Panics if the decrement causes an overflow.
-    pub(crate) fn dec(self) -> Self {
+    /// Decrement the value by 1. Returns None if the decrement would cause an underflow.
+    pub(crate) fn dec(self) -> Option<Self> {
         match self {
-            Self::Signed { value, bit_size } => Self::Signed {
-                value: value.checked_sub(1).expect("ICE: overflow while decrementing constant"),
-                bit_size,
-            },
-            Self::Unsigned { value, bit_size } => Self::Unsigned {
-                value: value.checked_sub(1).expect("ICE: overflow while decrementing constant"),
-                bit_size,
-            },
+            Self::Signed { value, bit_size } => {
+                value.checked_sub(1).map(|value| Self::Signed { value, bit_size })
+            }
+            Self::Unsigned { value, bit_size } => {
+                value.checked_sub(1).map(|value| Self::Unsigned { value, bit_size })
+            }
         }
     }
 
```

### compiler/noirc_evaluator/src/ssa/opt/loop_invariant/simplify.rs
```diff
@@ -155,7 +155,7 @@ impl LoopInvariantContext<'_> {
             _ => None,
         }?;
 
-        let (upper_field, upper_type) = upper.dec().into_numeric_constant();
+        let (upper_field, upper_type) = upper.dec()?.into_numeric_constant();
         let (lower_field, lower_type) = lower.into_numeric_constant();
 
         let min_iter = self.inserter.function.dfg.make_constant(lower_field, lower_type);
@@ -322,7 +322,7 @@ impl LoopInvariantContext<'_> {
                 true if lower_bound >= constant => SimplifyResult::SimplifiedTo(self.false_value),
                 // `const < i`
                 false if lower_bound > constant => SimplifyResult::SimplifiedTo(self.true_value),
-                false if upper_bound <= constant.inc() => {
+                false if constant.inc().is_some_and(|constant| upper_bound <= constant) => {
                     // If `const >= upper_bound - 1` then it will never be less than `i`.
                     SimplifyResult::SimplifiedTo(self.false_value)
                 }
```

### compiler/noirc_evaluator/src/ssa/opt/unrolling.rs
```diff
@@ -769,7 +769,7 @@ impl Loop {
                 // If `b2` is the loop body: Loop exits when v == rhs; upper = rhs + 1.
                 // If `b3` is the loop body: Loop exits when v == rhs; upper = rhs.
                 let const_rhs = dfg.get_integer_constant(*rhs)?;
-                if then_branch_is_body { Some(const_rhs.inc()) } else { Some(const_rhs) }
+                if then_branch_is_body { const_rhs.inc() } else { Some(const_rhs) }
             }
             Instruction::Not(operand) => {
                 if *operand != induction_var {
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -702,7 +702,9 @@ impl FunctionContext<'_> {
             let max_value = if bit_size == 128 { u128::MAX } else { (1u128 << bit_size) - 1 };
 
             if end_constant.into_numeric_constant().0.to_u128() < max_value {
-                let end_constant_plus_one = end_constant.inc();
+                let end_constant_plus_one = end_constant.inc().expect(
+                    "Expected to be able to increment end_constant as it's less than max_value",
+                );
                 end_index = self
                     .builder
                     .numeric_constant(end_constant_plus_one.into_numeric_constant().0, index_type);
```

### test_programs/execution_success/regression_12494/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_12494"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/regression_12494/Prover.toml
```diff
@@ -0,0 +1 @@
+return = false
```

### test_programs/execution_success/regression_12494/src/main.nr
```diff
@@ -0,0 +1,9 @@
+fn main() -> pub bool {
+    let mut hit: bool = false;
+    for i in 0..3_u128 {
+        if 340282366920938463463374607431768211455 < i {
+            hit = true;
+        }
+    }
+    hit
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_12494/execute__tests__expanded.snap
```diff
@@ -0,0 +1,13 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main() -> pub bool {
+    let mut hit: bool = false;
+    for i in 0_u128..3_u128 {
+        if 340282366920938463463374607431768211455_u128 < i {
+            hit = true;
+        }
+    }
+    hit
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_12494/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+[regression_12494] Circuit output: false
```
