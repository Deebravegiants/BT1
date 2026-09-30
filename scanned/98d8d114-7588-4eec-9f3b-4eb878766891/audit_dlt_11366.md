# [?] fix: apply predicate to over/underflow checks (#3494)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-11-15
Source: https://github.com/noir-lang/noir/commit/fc3edf7aa5da9074614fa900bbcb57e512e3d56b
Type: security-commit

## Details
fix: apply predicate to over/underflow checks (#3494)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/printer.rs
```diff
@@ -173,7 +173,7 @@ pub(crate) fn display_instruction(
             )
         }
         Instruction::RangeCheck { value, max_bit_size, .. } => {
-            write!(f, "range_check {} to {} bits", show(*value), *max_bit_size,)
+            writeln!(f, "range_check {} to {} bits", show(*value), *max_bit_size,)
         }
     }
 }
```

### compiler/noirc_evaluator/src/ssa/opt/flatten_cfg.rs
```diff
@@ -662,6 +662,22 @@ impl<'f> Context<'f> {
                     self.remember_store(address, value);
                     Instruction::Store { address, value }
                 }
+                Instruction::RangeCheck { value, max_bit_size, assert_message } => {
+                    // Replace value with `value * predicate` to zero out value when predicate is inactive.
+
+                    // Condition needs to be cast to argument type in order to multiply them together.
+                    let argument_type = self.inserter.function.dfg.type_of_value(value);
+                    let casted_condition = self.insert_instruction(
+                        Instruction::Cast(condition, argument_type),
+                        call_stack.clone(),
+                    );
+
+                    let value = self.insert_instruction(
+                        Instruction::binary(BinaryOp::Mul, value, casted_condition),
+                        call_stack.clone(),
+                    );
+                    Instruction::RangeCheck { value, max_bit_size, assert_message }
+                }
                 other => other,
             }
         } else {
```

### tooling/nargo_cli/tests/execution_success/conditional_regression_underflow/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "conditional_underflow"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### tooling/nargo_cli/tests/execution_success/conditional_regression_underflow/Prover.toml
```diff
@@ -0,0 +1 @@
+x = "4"
\ No newline at end of file
```

### tooling/nargo_cli/tests/execution_success/conditional_regression_underflow/src/main.nr
```diff
@@ -0,0 +1,15 @@
+// Regression test for https://github.com/noir-lang/noir/issues/3493
+fn main(x: u4) {
+    if x == 10 {
+        x + 15;
+    }
+    if x == 9 {
+        x << 3;
+    }
+    if x == 8 {
+        x * 3;
+    }
+    if x == 7 {
+        x - 8;
+    }
+}
\ No newline at end of file
```
