# [?] fix: put constraint failure after binary operations that overflow (#9023)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-28
Source: https://github.com/noir-lang/noir/commit/f645c2892dff4b4a15d58cecfc4f7cc406424720
Type: security-commit

## Details
fix: put constraint failure after binary operations that overflow (#9023)

Co-authored-by: Akosh Farkash <aakoshh@gmail.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify/binary.rs
```diff
@@ -2,7 +2,10 @@ use acvm::{AcirField as _, FieldElement};
 
 use crate::ssa::ir::{
     dfg::DataFlowGraph,
-    instruction::{Binary, BinaryOp, Instruction, binary::eval_constant_binary_op},
+    instruction::{
+        Binary, BinaryOp, Instruction,
+        binary::{BinaryEvaluationResult, eval_constant_binary_op},
+    },
     types::NumericType,
 };
 
@@ -51,11 +54,13 @@ pub(super) fn simplify_binary(binary: &Binary, dfg: &mut DataFlowGraph) -> Simpl
 
     if let (Some(lhs), Some(rhs)) = (lhs_value, rhs_value) {
         return match eval_constant_binary_op(lhs, rhs, operator, lhs_type) {
-            Some((result, result_type)) => {
+            BinaryEvaluationResult::Success(result, result_type) => {
                 let value = dfg.make_constant(result, result_type);
                 SimplifyResult::SimplifiedTo(value)
             }
-            None => SimplifyResult::SimplifiedToInstruction(simplified),
+            BinaryEvaluationResult::CouldNotEvaluate | BinaryEvaluationResult::Failure(..) => {
+                SimplifyResult::SimplifiedToInstruction(simplified)
+            }
         };
     }
 
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -87,49 +87,102 @@ impl Binary {
     }
 }
 
+#[derive(Debug)]
+pub(crate) enum BinaryEvaluationResult {
+    /// The binary operation could not be evaluated
+    CouldNotEvaluate,
+    /// The binary operation could be evaluated and it was successful
+    Success(FieldElement, NumericType),
+    /// The binary operation could be evaluated but it is guaranteed to fail
+    /// (for example: overflow or division by zero).
+    Failure(String),
+}
+
 /// Evaluate a binary operation with constant arguments.
 pub(crate) fn eval_constant_binary_op(
     lhs: FieldElement,
     rhs: FieldElement,
     operator: BinaryOp,
     mut operand_type: NumericType,
-) -> Option<(FieldElement, NumericType)> {
+) -> BinaryEvaluationResult {
+    use BinaryEvaluationResult::{CouldNotEvaluate, Failure, Success};
+
     let value = match operand_type {
         NumericType::NativeField => {
             // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
             // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
             // and the operation should be handled by ACIR generation.
             if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == FieldElement::zero() {
-                return None;
+                return Failure("attempt to divide by zero".to_string());
             }
-            operator.get_field_function()?(lhs, rhs)
+            let Some(function) = operator.get_field_function() else {
+                return CouldNotEvaluate;
+            };
+            function(lhs, rhs)
         }
         NumericType::Unsigned { bit_size } => {
             let function = operator.get_u128_function();
 
-            let lhs = truncate(lhs.try_into_u128()?, bit_size);
-            let rhs = truncate(rhs.try_into_u128()?, bit_size);
+            let Some(lhs) = lhs.try_into_u128() else {
+                return CouldNotEvaluate;
+            };
+            let Some(rhs) = rhs.try_into_u128() else {
+                return CouldNotEvaluate;
+            };
+
+            let lhs = truncate(lhs, bit_size);
+            let rhs = truncate(rhs, bit_size);
 
             // The divisor is being truncated into the type of the operand, which can potentially
             // lead to the rhs being zero.
             // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
             // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
             // and the operation should be handled by ACIR generation.
             if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == 0 {
-                return None;
+                return Failure("attempt to divide by zero".to_string());
             }
-            let result = function(lhs, rhs)?;
+
+            let Some(result) = function(lhs, rhs) else {
+                if let BinaryOp::Shl = operator {
+                    return CouldNotEvaluate;
+                }
+
+                if let BinaryOp::Shr = operator {
+                    return Success(FieldElement::zero(), operand_type);
+                }
+
+                let op = binary_op_function_name(operator);
+                return Failure(format!("attempt to {op} with overflow"));
+            };
+
             // Check for overflow
             if result != 0 && result.ilog2() >= bit_size {
-                return None;
+                if let BinaryOp::Shl = operator {
+                    // Right now `shl` might return zero or overflow depending on its values
+                    // so don't assume the final value here.
+                    // See https://github.com/noir-lang/noir/issues/9022
+                    return CouldNotEvaluate;
+                }
+
+                if let BinaryOp::Shr = operator {
+                    return Success(FieldElement::zero(), operand_type);
+                }
+
+                let op = binary_op_function_name(operator);
+                return Failure(format!("attempt to {op} with overflow"));
             }
+
             result.into()
         }
         NumericType::Signed { bit_size } => {
             let function = operator.get_i128_function();
 
-            let lhs = try_convert_field_element_to_signed_integer(lhs, bit_size)?;
-            let rhs = try_convert_field_element_to_signed_integer(rhs, bit_size)?;
+            let Some(lhs) = try_convert_field_element_to_signed_integer(lhs, bit_size) else {
+                return CouldNotEvaluate;
+            };
+            let Some(rhs) = try_convert_field_element_to_signed_integer(rhs, bit_size) else {
+                return CouldNotEvaluate;
+            };
 
             let result = function(lhs, rhs);
             let result = match operator {
@@ -139,24 +192,41 @@ pub(crate) fn eval_constant_binary_op(
                     // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
                     // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
                     // and the operation should be handled by ACIR generation.
-                    return None;
+                    return Failure("attempt to divide by zero".to_string());
                 }
                 BinaryOp::Shr => {
                     if rhs >= bit_size as i128 {
                         if lhs >= 0 { 0 } else { -1 }
                     } else {
-                        result?
+                        let Some(result) = result else {
+                            return CouldNotEvaluate;
+                        };
+                        result
                     }
                 }
 
                 _ => {
                     // Check for overflow
                     let two_pow_bit_size_minus_one = 1i128 << (bit_size - 1);
-                    let result = result?;
+                    let Some(result) = result else {
+                        if let BinaryOp::Shl = operator {
+                            return CouldNotEvaluate;
+                        }
+
+                        let op = binary_op_function_name(operator);
+                        return Failure(format!("attempt to {op} with overflow"));
+                    };
+
                     if result >= two_pow_bit_size_minus_one || result < -two_pow_bit_size_minus_one
                     {
-                        return None;
+                        if let BinaryOp::Shl = operator {
+                            return CouldNotEvaluate;
+                        }
+
+                        let op = binary_op_function_name(operator);
+                        return Failure(format!("attempt to {op} with overflow"));
                     }
+
                     result
                 }
             };
@@ -168,7 +238,22 @@ pub(crate) fn eval_constant_binary_op(
         operand_type = NumericType::bool();
     }
 
-    Some((value, operand_type))
+    Success(value, operand_type)
+}
+
+fn binary_op_function_name(op: BinaryOp) -> &'static str {
+    match op {
+        BinaryOp::Add { .. } => "add",
+        BinaryOp::Sub { .. } => "subtract",
+        BinaryOp::Mul { .. } => "multiply",
+        BinaryOp::Div => "divide",
+        BinaryOp::Mod => "modulo",
+        BinaryOp::Shl => "shift left",
+        BinaryOp::Shr => "shift right",
+        BinaryOp::Eq | BinaryOp::Lt | BinaryOp::And | BinaryOp::Or | BinaryOp::Xor => {
+            panic!("Shouldn't need binary op function name of {op}")
+        }
+    }
 }
 
 /// Values in the range `[0, 2^(bit_size-1))` are interpreted as positive integers
```

### compiler/noirc_evaluator/src/ssa/opt/loop_invariant.rs
```diff
@@ -55,7 +55,7 @@ use crate::ssa::{
         function_inserter::FunctionInserter,
         instruction::{
             Binary, BinaryOp, ConstrainError, Instruction, InstructionId,
-            binary::eval_constant_binary_op,
+            binary::{BinaryEvaluationResult, eval_constant_binary_op},
         },
         integer::IntegerConstant,
         post_order::PostOrder,
@@ -847,20 +847,22 @@ impl<'f> LoopInvariantContext<'f> {
         } {
             // We evaluate this expression using the upper bounds (or lower in the case of sub)
             // of its inputs to check whether it will ever overflow.
-            // If so, this will cause `eval_constant_binary_op` to return `None`.
-            // Therefore a `Some` value shows that this operation is safe.
+            // If `eval_constant_binary_op` won't overflow we can simplify the instruction to an unchecked version.
             let lhs = lhs.into_numeric_constant().0;
             let rhs = rhs.into_numeric_constant().0;
-            if eval_constant_binary_op(lhs, rhs, binary.operator, operand_type).is_some() {
-                // Unchecked version of the binary operation
-                let unchecked = Instruction::Binary(Binary {
-                    operator: binary.operator.into_unchecked(),
-                    lhs: binary.lhs,
-                    rhs: binary.rhs,
-                });
-                return SimplifyResult::SimplifiedToInstruction(unchecked);
-            } else {
-                return SimplifyResult::None;
+            match eval_constant_binary_op(lhs, rhs, binary.operator, operand_type) {
+                BinaryEvaluationResult::Success(..) => {
+                    // Unchecked version of the binary operation
+                    let unchecked = Instruction::Binary(Binary {
+                        operator: binary.operator.into_unchecked(),
+                        lhs: binary.lhs,
+                        rhs: binary.rhs,
+                    });
+                    return SimplifyResult::SimplifiedToInstruction(unchecked);
+                }
+                BinaryEvaluationResult::CouldNotEvaluate | BinaryEvaluationResult::Failure(..) => {
+                    return SimplifyResult::None;
+                }
             }
         }
 
```

### compiler/noirc_evaluator/src/ssa/opt/remove_unreachable_instructions.rs
```diff
@@ -3,13 +3,22 @@
 //! any subsequent instructions in that block will never be executed. This pass
 //! then removes those subsequent instructions and replaces the block's terminator
 //! with a special `unreachable` value.
+//!
+//! This pass might also add constrain checks after existing instuctions,
+//! for example binary operations that are guaranteed to overflow.
+use acvm::AcirField;
 
 use crate::ssa::{
     ir::{
-        dfg::DataFlowGraph,
         function::Function,
-        instruction::{Instruction, TerminatorInstruction},
+        instruction::{
+            Binary, BinaryOp, ConstrainError, Instruction, TerminatorInstruction,
+            binary::{BinaryEvaluationResult, eval_constant_binary_op},
+        },
+        types::{NumericType, Type},
+        value::ValueId,
     },
+    opt::simple_optimization::SimpleOptimizationContext,
     ssa_gen::Ssa,
 };
 
@@ -31,20 +40,96 @@ impl Function {
         // after an always failing one was found.
         let mut current_block_instructions_are_unreachable = false;
 
+        let one = self.dfg.make_constant(1_u32.into(), NumericType::bool());
+        let mut side_effects_condition = one;
+
         self.simple_reachable_blocks_optimization(|context| {
             let block_id = context.block_id;
 
             if current_block_id != Some(block_id) {
                 current_block_id = Some(block_id);
                 current_block_instructions_are_unreachable = false;
+                side_effects_condition = one;
             }
 
             if current_block_instructions_are_unreachable {
                 context.remove_current_instruction();
                 return;
             }
 
-            if always_fails(context.dfg, context.instruction()) {
+            let instruction = context.instruction();
+            if let Instruction::EnableSideEffectsIf { condition } = instruction {
+                side_effects_condition = *condition;
+                return;
+            };
+
+            let always_fails = match instruction {
+                Instruction::Constrain(lhs, rhs, _) => {
+                    let Some(lhs_constant) = context.dfg.get_numeric_constant(*lhs) else {
+                        return;
+                    };
+                    let Some(rhs_constant) = context.dfg.get_numeric_constant(*rhs) else {
+                        return;
+                    };
+                    lhs_constant != rhs_constant
+                }
+                Instruction::ConstrainNotEqual(lhs, rhs, _) => {
+                    let Some(lhs_constant) = context.dfg.get_numeric_constant(*lhs) else {
+                        return;
+                    };
+                    let Some(rhs_constant) = context.dfg.get_numeric_constant(*rhs) else {
+                        return;
+                    };
+                    lhs_constant == rhs_constant
+                }
+                Instruction::Binary(binary @ Binary { lhs, operator, rhs }) => {
+                    let requires_acir_gen_predicate =
+                        binary.requires_acir_gen_predicate(context.dfg);
+                    if requires_acir_gen_predicate {
+                        // If performing the binary operation depends on the side effects condition, then
+                        // we can only simplify it if the condition is true: not when it's zero, and not when it's a variable.
+                        let predicate = context.dfg.get_numeric_constant(side_effects_condition);
+                        match predicate {
+                            Some(predicate) => {
+                                if predicate.is_zero() {
+                                    // The predicate is zero
+                                    return;
+                                }
+                            }
+                            None => {
+                                // The predicate is a variable
+                                return;
+                            }
+                        }
+                    }
+
+                    if let Some(message) =
+                        binary_operation_always_fails(*lhs, *operator, *rhs, context)
+                    {
+                        // Insert the instruction right away so we can add a constrain immediately after it
+                        context.insert_current_instruction();
+
+                        let zero = context.dfg.make_constant(0_u128.into(), NumericType::bool());
+                        let one = context.dfg.make_constant(1_u128.into(), NumericType::bool());
+                        let message = Some(ConstrainError::StaticString(message));
+                        let instruction = Instruction::Constrain(zero, one, message);
+                        let call_stack =
+                            context.dfg.get_instruction_call_stack_id(context.instruction_id);
+                        context.dfg.insert_instruction_and_results(
+                            instruction,
+                            block_id,
+                            None,
+                            call_stack,
+                        );
+                        true
+                    } else {
+                        false
+                    }
+                }
+                _ => false,
+            };
+
+            if always_fails {
                 current_block_instructions_are_unreachable = true;
 
                 let terminator = context.dfg[block_id].take_terminator();
@@ -56,34 +141,58 @@ impl Function {
     }
 }
 
-/// Returns `true` if the given instruction will always produce an asertion failure.
-fn always_fails(dfg: &DataFlowGraph, instruction: &Instruction) -> bool {
-    match instruction {
-        Instruction::Constrain(lhs, rhs, _) => {
-            let Some(lhs_constant) = dfg.get_numeric_constant(*lhs) else {
-                return false;
-            };
-            let Some(rhs_constant) = dfg.get_numeric_constant(*rhs) else {
-                return false;
-            };
-            lhs_constant != rhs_constant
-        }
-        Instruction::ConstrainNotEqual(lhs, rhs, _) => {
-            let Some(lhs_constant) = dfg.get_numeric_constant(*lhs) else {
-                return false;
-            };
-            let Some(rhs_constant) = dfg.get_numeric_constant(*rhs) else {
-                return false;
-            };
-            lhs_constant == rhs_constant
+fn binary_operation_always_fails(
+    lhs: ValueId,
+    operator: BinaryOp,
+    rhs: ValueId,
+    context: &mut SimpleOptimizationContext,
+) -> Option<String> {
+    // Unchecked operations can never fail
+    match operator {
+        BinaryOp::Add { unchecked } | BinaryOp::Sub { unchecked } | BinaryOp::Mul { unchecked } => {
+            if unchecked {
+                return None;
+            }
         }
-        _ => false,
+        BinaryOp::Div
+        | BinaryOp::Mod
+        | BinaryOp::Eq
+        | BinaryOp::Lt
+        | BinaryOp::And
+        | BinaryOp::Or
+        | BinaryOp::Xor
+        | BinaryOp::Shl
+        | BinaryOp::Shr => (),
+    };
+
+    let rhs_value = context.dfg.get_numeric_constant(rhs)?;
+
+    if matches!(operator, BinaryOp::Div) && rhs_value.is_zero() {
+        return Some("attempt to divide by zero".to_string());
+    }
+
+    if matches!(operator, BinaryOp::Mod) && rhs_value.is_zero() {
+        return Some("attempt to calculate the remainder with a divisor of zero".to_string());
+    }
+
+    let Type::Numeric(numeric_type) = context.dfg.type_of_value(lhs) else {
+        panic!("Expected numeric type for binary operation");
+    };
+
+    let lhs_value = context.dfg.get_numeric_constant(lhs)?;
+
+    match eval_constant_binary_op(lhs_value, rhs_value, operator, numeric_type) {
+        BinaryEvaluationResult::Failure(message) => Some(message),
+        BinaryEvaluationResult::CouldNotEvaluate | BinaryEvaluationResult::Success(..) => None,
     }
 }
 
 #[cfg(test)]
 mod test {
-    use crate::{assert_ssa_snapshot, ssa::ssa_gen::Ssa};
+    use crate::{
+        assert_ssa_snapshot,
+        ssa::{opt::assert_normalized_ssa_equals, ssa_gen::Ssa},
+    };
 
     #[test]
     fn removes_unreachable_instructions_in_block_for_constrain_equal() {
@@ -135,6 +244,101 @@ mod test {
         "#);
     }
 
+    #[test]
+    fn removes_unreachable_instructions_in_block_for_sub_that_overflows() {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v0 = sub u32 0, u32 1
+            v1 = add v0, u32 1
+            return v1
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = sub u32 0, u32 1
+            constrain u1 0 == u1 1, "attempt to subtract with overflow"
+            unreachable
+        }
+        "#);
+    }
+
+    #[test]
+    fn removes_unreachable_instructions_in_block_for_division_by_zero() {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v0 = div u32 1, u32 0
+            v1 = add v0, u32 1
+            return v1
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = div u32 1, u32 0
+            constrain u1 0 == u1 1, "attempt to divide by zero"
+            unreachable
+        }
+        "#);
+    }
+
+    #[test]
+    fn does_not_replace_unchecked_sub_that_overflows() {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v0 = unchecked_sub u32 0, u32 1
+            v1 = add v0, u32 1
+            return v1
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn does_not_replace_sub_that_overflows_but_is_disabled_because_of_unknown_side_effects_condition()
+     {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0(v0: u1):
+            enable_side_effects v0
+            v1 = sub u32 0, u32 1
+            v2 = add v1, u32 1
+            return v2
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn does_not_replace_sub_that_overflows_but_is_disabled_because_of_false_side_effects_condition()
+    {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            enable_side_effects u1 0
+            v0 = sub u32 0, u32 1
+            v1 = add v0, u32 1
+            return v1
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
     #[test]
     fn removes_unreachable_instructions_from_dominated_blocks_normal_order() {
         let src = r#"
```

### test_programs/compile_success_with_bug/regression_8995/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_8995"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/compile_success_with_bug/regression_8995/src/main.nr
```diff
@@ -0,0 +1,9 @@
+fn main() -> pub bool {
+    let b: [(bool, &mut u1); 2] = [(false, &mut 0), (true, &mut 1)];
+
+    let x: u32 = 0;
+    let y: u32 = 1;
+    let z: u32 = 2;
+
+    b[((x - y) % z)].0
+}
```

### tooling/ast_fuzzer/fuzz/src/lib.rs
```diff
@@ -197,7 +197,7 @@ pub fn compare_results_interpreted(
             "---\nSSA 1 after step {} ({}):\n{}",
             inputs.ssa1.step,
             inputs.ssa1.msg,
-            inputs.ssa2.ssa.print_without_locations()
+            inputs.ssa1.ssa.print_without_locations()
         );
         eprintln!(
             "---\nSSA 2 after step {} ({}):\n{}",
```

### tooling/ast_fuzzer/src/compare/compiled.rs
```diff
@@ -134,13 +134,26 @@ impl Comparable for NargoErrorWithTypes {
         // we consider equivalents, but that's really just to stay on the conservative
         // side and give us a chance to inspect new kinds of test failures.
 
+        fn both<F: Fn(&str) -> bool>(s1: &str, s2: &str, f: F) -> bool {
+            f(s1) && f(s2)
+        }
+
         let msg1 = e1.user_defined_failure_message();
         let msg2 = e2.user_defined_failure_message();
-        let equiv_msgs = if let (Some(msg1), Some(msg2)) = (msg1, msg2) {
-            msg1 == msg2 || msg1.contains("overflow") && msg2.contains("overflow")
+        let equiv_msgs = if let (Some(msg1), Some(msg2)) = (&msg1, &msg2) {
+            msg1 == msg2
+                || both(msg1, msg2, |msg| msg.contains("overflow"))
+                || both(msg1, msg2, |msg| {
+                    msg.contains("divide by zero") || msg.contains("divisor of zero")
+                })
         } else {
             false
         };
+
+        if equiv_msgs {
+            return true;
+        }
+
         match (ee1, ee2) {
             (
                 AssertionFailed(ResolvedAssertionPayload::String(c), _, _),
@@ -149,16 +162,17 @@ impl Comparable for NargoErrorWithTypes {
                 // Looks like the workaround we have for comptime failures originating from overflows and similar assertion failures.
                 true
             }
-            (AssertionFailed(p1, _, _), AssertionFailed(p2, _, _)) => p1 == p2 || equiv_msgs,
+            (AssertionFailed(p1, _, _), AssertionFailed(p2, _, _)) => p1 == p2,
             (SolvingError(s1, _), SolvingError(s2, _)) => format!("{s1}") == format!("{s2}"),
-            (SolvingError(s, _), AssertionFailed(p, _, _))
-            | (AssertionFailed(p, _, _), SolvingError(s, _)) => match (s, p) {
-                (
-                    OpcodeResolutionError::UnsatisfiedConstrain { .. },
-                    ResolvedAssertionPayload::String(s),
-                ) => s == "Attempted to divide by zero",
-                _ => equiv_msgs,
-            },
+            (
+                SolvingError(OpcodeResolutionError::UnsatisfiedConstrain { .. }, _),
+                AssertionFailed(_, _, _),
+            ) => msg2.is_some_and(|msg| msg.contains("divide by zero")),
+            (
+                AssertionFailed(_, _, _),
+                SolvingError(OpcodeResolutionError::UnsatisfiedConstrain { .. }, _),
+            ) => msg1.is_some_and(|msg| msg.contains("divide by zero")),
+            _ => false,
         }
     }
 }
```

### tooling/ast_fuzzer/src/compare/interpreted.rs
```diff
@@ -100,6 +100,12 @@ impl CompareInterpreted {
             self.ssa1.msg,
             self.ssa1.ssa.print_without_locations()
         );
+        log::debug!(
+            "SSA after step {} ({}):\n{}\n",
+            self.ssa2.step,
+            self.ssa2.msg,
+            self.ssa2.ssa.print_without_locations()
+        );
 
         // Interpret an SSA with a fresh copy of the input values.
         let interpret = |ssa: &Ssa| {
@@ -192,6 +198,17 @@ impl Comparable for ssa::interpreter::errors::InterpreterError {
                 // So instead of reasoning about the `lhs` and `rhs` formats, let's just compare the message so we know it's the same constraint:
                 msg1 == msg2
             }
+            (
+                RangeCheckFailedWithMessage { message: msg1, .. },
+                ConstrainEqFailed { msg: msg2, .. },
+            ) => {
+                // The removal of unreachable instructions evaluates constant binary operations and can replace
+                // e.g. a `mul` followed by a `range_check` with a `constrain true == false, "attempt to multiple with overflow"`
+                msg2.contains(msg1)
+            }
+            (DivisionByZero { .. }, ConstrainEqFailed { msg, .. }) => {
+                msg.contains("attempt to divide by zero")
+            }
             (e1, e2) => {
                 // The format strings contain SSA instructions,
                 // where the only difference might be the value ID.
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_8272/execute__tests__stderr.snap
```diff
@@ -2,12 +2,12 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-bug: Assertion is always false: attempted to divide by constant larger than operand type: 254 > 32
-  ┌─ src/main.nr:5:13
+bug: Assertion is always false: attempt to subtract with overflow
+  ┌─ src/main.nr:5:21
   │
 5 │     b[0] = (b[0] % (869374236 - a));
-  │             ---------------------- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
+  │                     ------------- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
   │
   = Call stack:
     1. src/main.nr:2:5
-    2. src/main.nr:5:13
+    2. src/main.nr:5:21
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_8274/execute__tests__stderr.snap
```diff
@@ -9,11 +9,11 @@ warning: unused variable h
   │         - unused variable
   │
 
-bug: Assertion is always false: attempted to divide by constant larger than operand type: 128 > 64
-  ┌─ src/main.nr:2:14
+bug: Assertion is always false: attempt to multiply with overflow
+  ┌─ src/main.nr:2:35
   │
 2 │     let h = (((a as u64) >> b) % (11912905567223247326 * 14329851068374824036));
-  │              ----------------------------------------------------------------- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
+  │                                   ------------------------------------------- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
   │
   = Call stack:
-    1. src/main.nr:2:14
+    1. src/main.nr:2:35
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_8995/execute__tests__expanded.snap
```diff
@@ -0,0 +1,11 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main() -> pub bool {
+    let b: [(bool, &mut u1); 2] = [(false, &mut 0_u1), (true, &mut 1_u1)];
+    let x: u32 = 0_u32;
+    let y: u32 = 1_u32;
+    let z: u32 = 2_u32;
+    b[(x - y) % z].0
+}
```
