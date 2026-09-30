# [?] fix: don't remove signed min int division overflow in DIE (#10506)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-17
Source: https://github.com/noir-lang/noir/commit/50d5c0b4c9ca70f3ca49e13786048d1bb15b155e
Type: security-commit

## Details
fix: don't remove signed min int division overflow in DIE (#10506)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/die.rs
```diff
@@ -52,7 +52,9 @@ use crate::ssa::{
         dfg::DataFlowGraph,
         function::{Function, FunctionId},
         instruction::{BinaryOp, Instruction, InstructionId, Intrinsic, TerminatorInstruction},
+        integer::IntegerConstant,
         post_order::PostOrder,
+        types::NumericType,
         value::{Value, ValueId},
     },
     opt::{die::array_oob_checks::should_insert_oob_check, pure::Purity},
@@ -447,7 +449,23 @@ fn can_be_eliminated_if_unused(
         Binary(binary) => {
             if matches!(binary.operator, BinaryOp::Div | BinaryOp::Mod) {
                 if let Some(rhs) = function.dfg.get_numeric_constant(binary.rhs) {
-                    rhs != FieldElement::zero()
+                    // Division by zero must remain
+                    if rhs == FieldElement::zero() {
+                        return false;
+                    }
+
+                    // There's one more case: signed division that does MIN / -1
+                    let typ = function.dfg.type_of_value(binary.lhs).unwrap_numeric();
+                    if let NumericType::Signed { bit_size } = typ {
+                        if let Some(rhs) = IntegerConstant::from_numeric_constant(rhs, typ) {
+                            let minus_one = IntegerConstant::Signed { value: -1, bit_size };
+                            if rhs == minus_one {
+                                return false;
+                            }
+                        }
+                    }
+
+                    true
                 } else {
                     false
                 }
```

### test_programs/compile_success_with_bug/regression_10498/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_10498"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/compile_success_with_bug/regression_10498/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn main() -> pub bool {
+    foo().0
+}
+
+fn foo() -> (bool, i8) {
+    (true, (-128_i8 / -1_i8))
+}
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_10498/execute__tests__expanded.snap
```diff
@@ -0,0 +1,11 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main() -> pub bool {
+    foo().0
+}
+
+fn foo() -> (bool, i8) {
+    (true, -128_i8 / -1_i8)
+}
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_10498/execute__tests__stderr.snap
```diff
@@ -0,0 +1,13 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+bug: Assertion is always false: Attempt to divide with overflow
+  ┌─ src/main.nr:6:13
+  │
+6 │     (true, (-128_i8 / -1_i8))
+  │             --------------- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
+  │
+  = Call stack:
+    1. src/main.nr:2:5
+    2. src/main.nr:6:13
```
