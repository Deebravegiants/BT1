# [?] fix: inconsistent Brillig failure message on modulo overflow (#12482)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-29
Source: https://github.com/noir-lang/noir/commit/dd2b758da04b0a87235d54343710c22f028a8bb0
Type: security-commit

## Details
fix: inconsistent Brillig failure message on modulo overflow (#12482)

## Patch
### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_instructions/brillig_binary.rs
```diff
@@ -4,7 +4,7 @@ use crate::brillig::brillig_gen::brillig_block::{BrilligBlock, type_of_binary_op
 use crate::brillig::brillig_gen::brillig_fn::FunctionContext;
 use crate::brillig::brillig_ir::brillig_variable::SingleAddrVariable;
 use crate::brillig::brillig_ir::registers::{Allocated, RegisterAllocator};
-use crate::brillig::brillig_ir::{BrilligBinaryOp, BrilligContext};
+use crate::brillig::brillig_ir::{BrilligBinaryOp, BrilligContext, SignedDivisionOperator};
 use crate::ssa::ir::instruction::{BinaryOp, InstructionId, binary::Binary};
 use crate::ssa::ir::printer::try_to_extract_string_from_error_payload;
 use crate::ssa::ir::types::{NumericType, Type};
@@ -42,7 +42,12 @@ impl<Registers: RegisterAllocator> BrilligBlock<'_, Registers> {
         let brillig_binary_op = match binary.operator {
             BinaryOp::Div => {
                 if is_signed {
-                    self.brillig_context.convert_signed_division(left, right, result_variable);
+                    self.brillig_context.convert_signed_division(
+                        left,
+                        right,
+                        result_variable,
+                        SignedDivisionOperator::Div,
+                    );
                     return;
                 } else if is_field {
                     BrilligBinaryOp::FieldDiv
@@ -103,7 +108,12 @@ impl<Registers: RegisterAllocator> BrilligBlock<'_, Registers> {
         let scratch_var_j = self.brillig_context.allocate_single_addr(left.bit_size);
 
         // i = left / right
-        self.brillig_context.convert_signed_division(left, right, *scratch_var_i);
+        self.brillig_context.convert_signed_division(
+            left,
+            right,
+            *scratch_var_i,
+            SignedDivisionOperator::Mod,
+        );
 
         // j = i * right
         self.brillig_context.binary_instruction(
@@ -164,7 +174,12 @@ impl<Registers: RegisterAllocator> BrilligBlock<'_, Registers> {
 
                 // Right shift using division on 1-complement
                 ctx.binary_instruction(left, *one, result, BrilligBinaryOp::Add);
-                ctx.convert_signed_division(result, *two_pow, result);
+                ctx.convert_signed_division(
+                    result,
+                    *two_pow,
+                    result,
+                    SignedDivisionOperator::Shift,
+                );
                 ctx.binary_instruction(result, *one, result, BrilligBinaryOp::Sub);
             } else {
                 ctx.binary_instruction(left, right, result, BrilligBinaryOp::Shr);
```

### compiler/noirc_evaluator/src/brillig/brillig_ir.rs
```diff
@@ -286,6 +286,7 @@ impl<F: AcirField + DebugToString, Registers: RegisterAllocator> BrilligContext<
         left: SingleAddrVariable,
         right: SingleAddrVariable,
         result: SingleAddrVariable,
+        operator: SignedDivisionOperator,
     ) {
         let left_is_negative = self.allocate_single_addr_bool();
         let left_abs_value = self.allocate_single_addr(left.bit_size);
@@ -327,16 +328,27 @@ impl<F: AcirField + DebugToString, Registers: RegisterAllocator> BrilligContext<
                 let no_overflow = ctx.allocate_single_addr_bool();
                 ctx.binary_instruction(result, *max, *no_overflow, BrilligBinaryOp::LessThan);
                 ctx.codegen_if_not(no_overflow.address, |ctx2| {
-                    ctx2.codegen_constrain(
-                        *no_overflow,
-                        Some("Attempt to divide with overflow".to_string()),
-                    );
+                    let message = match operator {
+                        SignedDivisionOperator::Mod => {
+                            "Attempt to calculate the remainder with overflow"
+                        }
+                        SignedDivisionOperator::Div => "Attempt to divide with overflow",
+                        SignedDivisionOperator::Shift => "Attempt to bit-shift with overflow",
+                    };
+                    ctx2.codegen_constrain(*no_overflow, Some(message.to_string()));
                 });
             }
         });
     }
 }
 
+#[derive(Copy, Clone)]
+pub(crate) enum SignedDivisionOperator {
+    Div,
+    Mod,
+    Shift,
+}
+
 /// Special brillig context to codegen compiler intrinsic shared procedures
 impl<F: AcirField + DebugToString> BrilligContext<F, ScratchSpace> {
     /// Create a [BrilligContext] with a [ScratchSpace] for passing procedure arguments.
```

### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -626,6 +626,8 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                     "+" => "add",
                     "-" => "subtract",
                     "*" => "multiply",
+                    "/" => "divide",
+                    "%" => "calculate the remainder",
                     ">>" | "<<" => "bit-shift",
                     _ => operator,
                 };
```

### test_programs/execution_failure/regression_12469/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "regression_12469"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.23.0"
+
+[dependencies]
```

### test_programs/execution_failure/regression_12469/Prover.toml
```diff
@@ -0,0 +1,2 @@
+a = "-2147483648"
+b = "-1"
```

### test_programs/execution_failure/regression_12469/src/main.nr
```diff
@@ -0,0 +1,3 @@
+fn main(a: pub i32, b: pub i32) -> pub i32 {
+    a % b
+}
```

### tooling/nargo_cli/tests/snapshots/compile_failure/comptime_signed_division_by_minus_one_overflow/execute__tests__stderr.snap
```diff
@@ -2,7 +2,7 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-error: Attempt to / with overflow
+error: Attempt to divide with overflow
   ┌─ src/main.nr:2:24
   │
 2 │     let _ = comptime { -128_i8 / -1 };
```

### tooling/nargo_cli/tests/snapshots/compile_failure/comptime_signed_modulo_by_minus_one_overflow/execute__tests__stderr.snap
```diff
@@ -2,7 +2,7 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-error: Attempt to % with overflow
+error: Attempt to calculate the remainder with overflow
   ┌─ src/main.nr:2:24
   │
 2 │     let _ = comptime { -128_i8 % -1 };
```

### tooling/nargo_cli/tests/snapshots/compile_failure/div_signed/execute__tests__stderr.snap
```diff
@@ -16,7 +16,7 @@ warning: Unsafe block must have a safety comment above it
   │         ------ The comment must start with the "Safety: " word
   │
 
-error: Attempt to / with overflow
+error: Attempt to divide with overflow
    ┌─ src/main.nr:12:6
    │
 12 │     (a / -1)
```

### tooling/nargo_cli/tests/snapshots/execution_failure/div_signed/execute__tests__comptime_stderr.snap
```diff
@@ -9,7 +9,7 @@ warning: Unsafe block must have a safety comment above it
   │             ------ The comment must start with the "Safety: " word
   │
 
-error: Attempt to / with overflow
+error: Attempt to divide with overflow
    ┌─ src/main.nr:11:6
    │
 11 │     (a / -1)
```

### tooling/nargo_cli/tests/snapshots/execution_failure/regression_12469/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Attempt to calculate the remainder with overflow
+  ┌─ src/main.nr:2:5
+  │
+2 │     a % b
+  │     -----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:2:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/regression_12469/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Attempt to calculate the remainder with overflow
+  ┌─ src/main.nr:2:5
+  │
+2 │     a % b
+  │     -----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:2:5
+
+Failed assertion
```
