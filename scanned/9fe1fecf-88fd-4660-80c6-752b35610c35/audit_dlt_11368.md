# [?] feat!: avoid integer overflows (#2713)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-10-31
Source: https://github.com/noir-lang/noir/commit/7d7d63291d712137f97e6d44a774acdf2bd20512
Type: security-commit

## Details
feat!: avoid integer overflows (#2713)

Co-authored-by: vezenovm <mvezenov@gmail.com>
Co-authored-by: kevaundray <kevtheappdev@gmail.com>
Co-authored-by: github-merge-queue[bot] <github-merge-queue[bot]@users.noreply.github.com>
Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>
Co-authored-by: kek kek kek <andriy.n@obox.systems>
Co-authored-by: Martin Verzilli <martin.verzilli@gmail.com>
Co-authored-by: Savio <72797635+Savio-Sou@users.noreply.github.com>
Co-authored-by: Alex Gherghisan <alexghr@users.noreply.github.com>
Co-authored-by: jfecher <jake@aztecprotocol.com>
Co-authored-by: José Pedro Sousa <jose@aztecprotocol.com>
Co-authored-by: jfecher <jfecher11@gmail.com>
Co-authored-by: Álvaro Rodríguez <sirasistant@gmail.com>
Co-authored-by: josh crites <jc@joshcrites.com>
Co-authored-by: Gustavo Giráldez <ggiraldez@manas.tech>
Co-authored-by: Jan Beneš <janbenes1234@gmail.com>
Co-authored-by: Maddiaa <47148561+Maddiaa0@users.noreply.github.com>
Co-authored-by: Tom French <tom@tomfren.ch>

## Patch
### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_block.rs
```diff
@@ -18,6 +18,7 @@ use acvm::brillig_vm::brillig::HeapVector;
 use acvm::FieldElement;
 use fxhash::{FxHashMap as HashMap, FxHashSet as HashSet};
 use iter_extended::vecmap;
+use num_bigint::BigUint;
 
 use super::brillig_black_box::convert_black_box_call;
 use super::brillig_block_variables::BlockVariables;
@@ -554,6 +555,25 @@ impl<'block> BrilligBlock<'block> {
                     value_variable,
                 );
             }
+            Instruction::RangeCheck { value, max_bit_size, assert_message } => {
+                let left = self.convert_ssa_register_value(*value, dfg);
+                let max = BigUint::from(2_u128).pow(*max_bit_size);
+                let right = self.brillig_context.allocate_register();
+                self.brillig_context.const_instruction(
+                    right,
+                    FieldElement::from_be_bytes_reduce(&max.to_bytes_be()).into(),
+                );
+
+                let brillig_binary_op = BrilligBinaryOp::Integer {
+                    op: BinaryIntOp::LessThan,
+                    bit_size: max_bit_size + 1,
+                };
+                let condition = self.brillig_context.allocate_register();
+                self.brillig_context.binary_instruction(left, right, condition, brillig_binary_op);
+                self.brillig_context.constrain_instruction(condition, assert_message.clone());
+                self.brillig_context.deallocate_register(condition);
+                self.brillig_context.deallocate_register(right);
+            }
             _ => todo!("ICE: Instruction not supported {instruction:?}"),
         };
 
```

### compiler/noirc_evaluator/src/ssa/acir_gen/acir_ir/acir_variable.rs
```diff
@@ -656,15 +656,23 @@ impl AcirContext {
         let remainder_var = r_value.into_var()?;
 
         // Constrain `q < 2^{max_q_bits}`.
-        self.range_constrain_var(quotient_var, &NumericType::Unsigned { bit_size: max_q_bits })?;
+        self.range_constrain_var(
+            quotient_var,
+            &NumericType::Unsigned { bit_size: max_q_bits },
+            None,
+        )?;
 
         // Constrain `r < 2^{max_rhs_bits}`.
         //
         // If `rhs` is a power of 2, then is just a looser version of the following bound constraint.
         // In the case where `rhs` isn't a power of 2 then this range constraint is required
         // as the bound constraint creates a new witness.
         // This opcode will be optimized out if it is redundant so we always add it for safety.
-        self.range_constrain_var(remainder_var, &NumericType::Unsigned { bit_size: max_rhs_bits })?;
+        self.range_constrain_var(
+            remainder_var,
+            &NumericType::Unsigned { bit_size: max_rhs_bits },
+            None,
+        )?;
 
         // Constrain `r < rhs`.
         self.bound_constraint_with_offset(remainder_var, rhs, predicate, max_rhs_bits)?;
@@ -768,12 +776,12 @@ impl AcirContext {
             let r_var = self.add_constant(r.into());
             let aor = self.add_var(lhs_offset, r_var)?;
             // lhs_offset<=rhs_offset <=> lhs_offset + r < rhs_offset + r = 2^bit_size <=> witness < 2^bit_size
-            self.range_constrain_var(aor, &NumericType::Unsigned { bit_size })?;
+            self.range_constrain_var(aor, &NumericType::Unsigned { bit_size }, None)?;
             return Ok(());
         }
         // General case:  lhs_offset<=rhs <=> rhs-lhs_offset>=0 <=> rhs-lhs_offset is a 'bits' bit integer
         let sub_expression = self.sub_var(rhs, lhs_offset)?; //rhs-lhs_offset
-        self.range_constrain_var(sub_expression, &NumericType::Unsigned { bit_size: bits })?;
+        self.range_constrain_var(sub_expression, &NumericType::Unsigned { bit_size: bits }, None)?;
 
         Ok(())
     }
@@ -874,6 +882,7 @@ impl AcirContext {
         &mut self,
         variable: AcirVar,
         numeric_type: &NumericType,
+        message: Option<String>,
     ) -> Result<AcirVar, RuntimeError> {
         match numeric_type {
             NumericType::Signed { bit_size } | NumericType::Unsigned { bit_size } => {
@@ -886,6 +895,11 @@ impl AcirContext {
                 }
                 let witness = self.var_to_witness(variable)?;
                 self.acir_ir.range_constraint(witness, *bit_size)?;
+                if let Some(message) = message {
+                    self.acir_ir
+                        .assert_messages
+                        .insert(self.acir_ir.last_acir_opcode_location(), message);
+                }
             }
             NumericType::NativeField => {
                 // Range constraining a Field is a no-op
```

### compiler/noirc_evaluator/src/ssa/acir_gen/mod.rs
```diff
@@ -347,7 +347,7 @@ impl Context {
     ) -> Result<AcirVar, RuntimeError> {
         let acir_var = self.acir_context.add_variable();
         if matches!(numeric_type, NumericType::Signed { .. } | NumericType::Unsigned { .. }) {
-            self.acir_context.range_constrain_var(acir_var, numeric_type)?;
+            self.acir_context.range_constrain_var(acir_var, numeric_type, None)?;
         }
         Ok(acir_var)
     }
@@ -529,6 +529,14 @@ impl Context {
             Instruction::Load { .. } => {
                 unreachable!("Expected all load instructions to be removed before acir_gen")
             }
+            Instruction::RangeCheck { value, max_bit_size, assert_message } => {
+                let acir_var = self.convert_numeric_value(*value, dfg)?;
+                self.acir_context.range_constrain_var(
+                    acir_var,
+                    &NumericType::Unsigned { bit_size: *max_bit_size },
+                    assert_message.clone(),
+                )?;
+            }
         }
         self.acir_context.set_call_stack(CallStack::new());
         Ok(())
```

### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -154,6 +154,9 @@ pub(crate) enum Instruction {
     /// Constrains two values to be equal to one another.
     Constrain(ValueId, ValueId, Option<String>),
 
+    /// Range constrain `value` to `max_bit_size`
+    RangeCheck { value: ValueId, max_bit_size: u32, assert_message: Option<String> },
+
     /// Performs a function call with a list of its arguments.
     Call { func: ValueId, arguments: Vec<ValueId> },
 
@@ -203,7 +206,8 @@ impl Instruction {
             Instruction::ArraySet { array, .. } => InstructionResultType::Operand(*array),
             Instruction::Constrain(..)
             | Instruction::Store { .. }
-            | Instruction::EnableSideEffects { .. } => InstructionResultType::None,
+            | Instruction::EnableSideEffects { .. }
+            | Instruction::RangeCheck { .. } => InstructionResultType::None,
             Instruction::Load { .. } | Instruction::ArrayGet { .. } | Instruction::Call { .. } => {
                 InstructionResultType::Unknown
             }
@@ -230,9 +234,12 @@ impl Instruction {
             Truncate { .. } => false,
 
             // These either have side-effects or interact with memory
-            Constrain(..) | EnableSideEffects { .. } | Allocate | Load { .. } | Store { .. } => {
-                false
-            }
+            Constrain(..)
+            | EnableSideEffects { .. }
+            | Allocate
+            | Load { .. }
+            | Store { .. }
+            | RangeCheck { .. } => false,
 
             Call { func, .. } => match dfg[*func] {
                 Value::Intrinsic(intrinsic) => !intrinsic.has_side_effects(),
@@ -263,7 +270,7 @@ impl Instruction {
             | ArrayGet { .. }
             | ArraySet { .. } => false,
 
-            Constrain(..) | Store { .. } | EnableSideEffects { .. } => true,
+            Constrain(..) | Store { .. } | EnableSideEffects { .. } | RangeCheck { .. } => true,
 
             // Some `Intrinsic`s have side effects so we must check what kind of `Call` this is.
             Call { func, .. } => match dfg[*func] {
@@ -320,6 +327,13 @@ impl Instruction {
             Instruction::ArraySet { array, index, value } => {
                 Instruction::ArraySet { array: f(*array), index: f(*index), value: f(*value) }
             }
+            Instruction::RangeCheck { value, max_bit_size, assert_message } => {
+                Instruction::RangeCheck {
+                    value: f(*value),
+                    max_bit_size: *max_bit_size,
+                    assert_message: assert_message.clone(),
+                }
+            }
         }
     }
 
@@ -364,6 +378,9 @@ impl Instruction {
             Instruction::EnableSideEffects { condition } => {
                 f(*condition);
             }
+            Instruction::RangeCheck { value, .. } => {
+                f(*value);
+            }
         }
     }
 
@@ -461,6 +478,14 @@ impl Instruction {
             Instruction::Allocate { .. } => None,
             Instruction::Load { .. } => None,
             Instruction::Store { .. } => None,
+            Instruction::RangeCheck { value, max_bit_size, .. } => {
+                if let Some(numeric_constant) = dfg.get_numeric_constant(*value) {
+                    if numeric_constant.num_bits() < *max_bit_size {
+                        return Remove;
+                    }
+                }
+                None
+            }
         }
     }
 }
@@ -484,7 +509,11 @@ fn simplify_cast(value: ValueId, dst_typ: &Type, dfg: &mut DataFlowGraph) -> Sim
                 SimplifiedTo(dfg.make_constant(constant, dst_typ.clone()))
             }
             (
-                Type::Numeric(NumericType::NativeField | NumericType::Unsigned { .. }),
+                Type::Numeric(
+                    NumericType::NativeField
+                    | NumericType::Unsigned { .. }
+                    | NumericType::Signed { .. },
+                ),
                 Type::Numeric(NumericType::Unsigned { bit_size }),
             ) => {
                 // Field/Unsigned -> unsigned: truncate
@@ -822,6 +851,29 @@ fn eval_constant_binary_op(
             let result = function(lhs, rhs);
             truncate(result, *bit_size).into()
         }
+        Type::Numeric(NumericType::Signed { bit_size }) => {
+            let function = operator.get_i128_function();
+
+            let lhs = truncate(lhs.try_into_u128()?, *bit_size);
+            let rhs = truncate(rhs.try_into_u128()?, *bit_size);
+            let l_pos = lhs < 2u128.pow(bit_size - 1);
+            let r_pos = rhs < 2u128.pow(bit_size - 1);
+            let lhs = if l_pos { lhs as i128 } else { -((2u128.pow(*bit_size) - lhs) as i128) };
+            let rhs = if r_pos { rhs as i128 } else { -((2u128.pow(*bit_size) - rhs) as i128) };
+            // The divisor is being truncated into the type of the operand, which can potentially
+            // lead to the rhs being zero.
+            // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
+            // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
+            // and the operation should be handled by ACIR generation.
+            if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == 0 {
+                return None;
+            }
+
+            let result = function(lhs, rhs);
+            let result =
+                if result >= 0 { result as u128 } else { (2i128.pow(*bit_size) + result) as u128 };
+            truncate(result, *bit_size).into()
+        }
         _ => return None,
     };
 
@@ -868,6 +920,21 @@ impl BinaryOp {
             BinaryOp::Lt => |x, y| (x < y) as u128,
         }
     }
+
+    fn get_i128_function(self) -> fn(i128, i128) -> i128 {
+        match self {
+            BinaryOp::Add => i128::wrapping_add,
+            BinaryOp::Sub => i128::wrapping_sub,
+            BinaryOp::Mul => i128::wrapping_mul,
+            BinaryOp::Div => i128::wrapping_div,
+            BinaryOp::Mod => i128::wrapping_rem,
+            BinaryOp::And => |x, y| x & y,
+            BinaryOp::Or => |x, y| x | y,
+            BinaryOp::Xor => |x, y| x ^ y,
+            BinaryOp::Eq => |x, y| (x == y) as i128,
+            BinaryOp::Lt => |x, y| (x < y) as i128,
+        }
+    }
 }
 
 /// Binary Operations allowed in the IR.
```

### compiler/noirc_evaluator/src/ssa/ir/printer.rs
```diff
@@ -172,5 +172,8 @@ pub(crate) fn display_instruction(
                 show(*value)
             )
         }
+        Instruction::RangeCheck { value, max_bit_size, .. } => {
+            write!(f, "range_check {} to {} bits", show(*value), *max_bit_size,)
+        }
     }
 }
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -14,6 +14,7 @@ use crate::ssa::ir::dfg::DataFlowGraph;
 use crate::ssa::ir::function::FunctionId as IrFunctionId;
 use crate::ssa::ir::function::{Function, RuntimeType};
 use crate::ssa::ir::instruction::BinaryOp;
+use crate::ssa::ir::instruction::Instruction;
 use crate::ssa::ir::map::AtomicCounter;
 use crate::ssa::ir::types::{NumericType, Type};
 use crate::ssa::ir::value::ValueId;
@@ -265,6 +266,190 @@ impl<'a> FunctionContext<'a> {
         Ok(self.builder.numeric_constant(value, typ))
     }
 
+    /// helper function which add instructions to the block computing the absolute value of the
+    /// given signed integer input. When the input is negative, we return its two complement, and itself when it is positive.
+    fn absolute_value_helper(&mut self, input: ValueId, sign: ValueId, bit_size: u32) -> ValueId {
+        // We compute the absolute value of lhs
+        let one = self.builder.numeric_constant(FieldElement::one(), Type::bool());
+        let bit_width =
+            self.builder.numeric_constant(FieldElement::from(2_i128.pow(bit_size)), Type::field());
+        let sign_not = self.builder.insert_binary(one, BinaryOp::Sub, sign);
+        let as_field =
+            self.builder.insert_instruction(Instruction::Cast(input, Type::field()), None).first();
+        let sign_field =
+            self.builder.insert_instruction(Instruction::Cast(sign, Type::field()), None).first();
+        let positive_predicate = self.builder.insert_binary(sign_field, BinaryOp::Mul, as_field);
+        let two_complement = self.builder.insert_binary(bit_width, BinaryOp::Sub, as_field);
+        let sign_not_field = self
+            .builder
+            .insert_instruction(Instruction::Cast(sign_not, Type::field()), None)
+            .first();
+        let negative_predicate =
+            self.builder.insert_binary(sign_not_field, BinaryOp::Mul, two_complement);
+        self.builder.insert_binary(positive_predicate, BinaryOp::Add, negative_predicate)
+    }
+
+    fn check_overflow(
+        &mut self,
+        result: ValueId,
+        lhs: ValueId,
+        rhs: ValueId,
+        operator: BinaryOpKind,
+        location: Location,
+    ) -> ValueId {
+        let result_type = self.builder.current_function.dfg.type_of_value(result);
+        match result_type {
+            Type::Numeric(NumericType::Signed { bit_size }) => {
+                match operator {
+                    BinaryOpKind::Add | BinaryOpKind::Subtract => {
+                        // Result is computed modulo the bit size
+                        let mut result = self
+                            .builder
+                            .insert_instruction(
+                                Instruction::Truncate {
+                                    value: result,
+                                    bit_size,
+                                    max_bit_size: bit_size + 1,
+                                },
+                                None,
+                            )
+                            .first();
+                        result = self.builder.insert_cast(result, Type::unsigned(bit_size));
+
+                        self.check_signed_overflow(result, lhs, rhs, operator, bit_size, location);
+                        self.builder.insert_cast(result, result_type)
+                    }
+                    BinaryOpKind::Multiply => {
+                        // Result is computed modulo the bit size
+                        let mut result =
+                            self.builder.insert_cast(result, Type::unsigned(2 * bit_size));
+                        result = self
+                            .builder
+                            .insert_instruction(
+                                Instruction::Truncate {
+                                    value: result,
+                                    bit_size,
+                                    max_bit_size: 2 * bit_size,
+                                },
+                                None,
+                            )
+                            .first();
+
+                        self.check_signed_overflow(result, lhs, rhs, operator, bit_size, location);
+                        self.builder.insert_cast(result, result_type)
+                    }
+                    BinaryOpKind::ShiftLeft => {
+                        unreachable!("shift is not supported for signed integer")
+                    }
+                    _ => unreachable!("operator {} should not overflow", operator),
+                }
+            }
+            Type::Numeric(NumericType::Unsigned { bit_size }) => {
+                let op_name = match operator {
+                    BinaryOpKind::Add => "add",
+                    BinaryOpKind::Subtract => "subtract",
+                    BinaryOpKind::Multiply => "multiply",
+                    BinaryOpKind::ShiftLeft => "left shift",
+                    _ => unreachable!("operator {} should not overflow", operator),
+                };
+                let message = format!("attempt to {} with overflow", op_name);
+                let range_constraint = Instruction::RangeCheck {
+                    value: result,
+                    max_bit_size: bit_size,
+                    assert_message: Some(message),
+                };
+                self.builder.set_location(location).insert_instruction(range_constraint, None);
+                if operator == BinaryOpKind::ShiftLeft {
+                    match result_type {
+                        Type::Numeric(NumericType::Signed { bit_size })
+                        | Type::Numeric(NumericType::Unsigned { bit_size }) => {
+                            self.builder.insert_truncate(result, bit_size, bit_size + 1)
+                        }
+                        _ => result,
+                    }
+                } else {
+                    result
+                }
+            }
+            _ => result,
+        }
+    }
+
+    fn check_signed_overflow(
+        &mut self,
+        result: ValueId,
+        lhs: ValueId,
+        rhs: ValueId,
+        operator: BinaryOpKind,
+        bit_size: u32,
+        location: Location,
+    ) {
+        let is_sub = operator == BinaryOpKind::Subtract;
+        let one = self.builder.numeric_constant(FieldElement::one(), Type::bool());
+        let half_width = self.builder.numeric_constant(
+            FieldElement::from(2_i128.pow(bit_size - 1)),
+            Type::unsigned(bit_size),
+        );
+        // We compute the sign of the operands. The overflow checks for signed integers depends on these signs
+        let lhs_as_unsigned = self.builder.insert_cast(lhs, Type::unsigned(bit_size));
+        let rhs_as_unsigned = self.builder.insert_cast(rhs, Type::unsigned(bit_size));
+        let lhs_sign = self.builder.insert_binary(lhs_as_unsigned, BinaryOp::Lt, half_width);
+        let mut rhs_sign = self.builder.insert_binary(rhs_as_unsigned, BinaryOp::Lt, half_width);
+        let message = if is_sub {
+            // lhs - rhs = lhs + (-rhs)
+            rhs_sign = self.builder.insert_binary(one, BinaryOp::Sub, rhs_sign);
+            "attempt to subtract with overflow".to_string()
+        } else {
+            "attempt to add with overflow".to_string()
+        };
+        // same_sign is true if both operands have the same sign
+        let same_sign = self.builder.insert_binary(lhs_sign, BinaryOp::Eq, rhs_sign);
+        match operator {
+            BinaryOpKind::Add | BinaryOpKind::Subtract => {
+                //Check the result has the same sign as its inputs
+                let result_sign = self.builder.insert_binary(result, BinaryOp::Lt, half_width);
+                let sign_diff = self.builder.insert_binary(result_sign, BinaryOp::Eq, lhs_sign);
+                let sign_diff_with_predicate =
+                    self.builder.insert_binary(sign_diff, BinaryOp::Mul, same_sign);
+                let overflow_check =
+                    Instruction::Constrain(sign_diff_with_predicate, same_sign, Some(message));
+                self.builder.set_location(location).insert_instruction(overflow_check, None);
+            }
+            BinaryOpKind::Multiply => {
+                // Overflow check for the multiplication:
+                // First we compute the absolute value of operands, and their product
+                let lhs_abs = self.absolute_value_helper(lhs, lhs_sign, bit_size);
+                let rhs_abs = self.absolute_value_helper(rhs, rhs_sign, bit_size);
+                let product_field = self.builder.insert_binary(lhs_abs, BinaryOp::Mul, rhs_abs);
+                // It must not already overflow the bit_size
+                let message = "attempt to multiply with overflow".to_string();
+                let size_overflow = Instruction::RangeCheck {
+                    value: product_field,
+                    max_bit_size: bit_size,
+                    assert_message: Some(message.clone()),
+                };
+                self.builder.set_location(location).insert_instruction(size_overflow, None);
+                let product = self.builder.insert_cast(product_field, Type::unsigned(bit_size));
+
+                // Then we check the signed product fits in a signed integer of bit_size-bits
+                let not_same = self.builder.insert_binary(one, BinaryOp::Sub, same_sign);
+                let not_same_sign_field = self
+                    .builder
+                    .insert_instruction(Instruction::Cast(not_same, Type::unsigned(bit_size)), None)
+                    .first();
+                let positive_maximum_with_offset =
+                    self.builder.insert_binary(half_width, BinaryOp::Add, not_same_sign_field);
+                let product_overflow_check =
+                    self.builder.insert_binary(product, BinaryOp::Lt, positive_maximum_with_offset);
+                self.builder.set_location(location).insert_instruction(
+                    Instruction::Constrain(product_overflow_check, one, Some(message)),
+                    None,
+                );
+            }
+            BinaryOpKind::ShiftLeft => unreachable!("shift is not supported for signed integer"),
+            _ => unreachable!("operator {} should not overflow", operator),
+        }
+    }
     /// Insert a binary instruction at the end of the current block.
     /// Converts the form of the binary instruction as necessary
     /// (e.g. swapping arguments, inserting a not) to represent it in the IR.
@@ -294,21 +479,15 @@ impl<'a> FunctionContext<'a> {
             }
         };
 
-        if let Some(max_bit_size) = operator_result_max_bit_size_to_truncate(
+        // Check for integer overflow
+        if matches!(
             operator,
-            lhs,
-            rhs,
-            &self.builder.current_function.dfg,
+            BinaryOpKind::Add
+                | BinaryOpKind::Subtract
+                | BinaryOpKind::Multiply
+                | BinaryOpKind::ShiftLeft
         ) {
-            let result_type = self.builder.current_function.dfg.type_of_value(result);
-            let bit_size = match result_type {
-                Type::Numeric(NumericType::Signed { bit_size })
-                | Type::Numeric(NumericType::Unsigned { bit_size }) => bit_size,
-                _ => {
-                    unreachable!("ICE: Truncation attempted on non-integer");
-                }
-            };
-            result = self.builder.insert_truncate(result, bit_size, max_bit_size);
+            result = self.check_overflow(result, lhs, rhs, operator, location);
         }
 
         if operator_requires_not(operator) {
```

### noir_stdlib/src/sha256.nr
```diff
@@ -52,7 +52,10 @@ fn sha_w(msg: [u32; 16]) -> [u32; 64] // Expanded message blocks
 
     for j in 16..64
     {
-        w[j] = sigma1(w[j-2]) + w[j-7] + sigma0(w[j-15]) + w[j-16];
+        w[j] = crate::wrapping_add(
+            crate::wrapping_add(sigma1(w[j-2]), w[j-7]), 
+            crate::wrapping_add(sigma0(w[j-15]), w[j-16]),
+        );
     };
     
     w
@@ -68,17 +71,22 @@ fn sha_c(msg: [u32; 16], hash: [u32; 8]) -> [u32; 8]
     let w = sha_w(msg);
     for j in 0..64
     {
-        let t1 = out_h[7] + bigma1(out_h[4]) + ch(out_h[4], out_h[5], out_h[6])
-            + K[j] + w[j];
-        let t2 = bigma0(out_h[0]) + maj(out_h[0], out_h[1], out_h[2]);
+        let t1 = crate::wrapping_add(
+            crate::wrapping_add(
+                crate::wrapping_add(out_h[7], bigma1(out_h[4])),
+                ch(out_h[4], out_h[5], out_h[6])
+            ),
+            crate::wrapping_add(K[j], w[j])
+         );
+        let t2 = crate::wrapping_add(bigma0(out_h[0]), maj(out_h[0], out_h[1], out_h[2]));
         out_h[7] = out_h[6];
         out_h[6] = out_h[5];
         out_h[5] = out_h[4];
-        out_h[4] = out_h[3] + t1;
+        out_h[4] = crate::wrapping_add(out_h[3], t1);
         out_h[3] = out_h[2];
         out_h[2] = out_h[1];
         out_h[1] = out_h[0];
-        out_h[0] = t1 + t2;
+        out_h[0] = crate::wrapping_add(t1, t2);
     };
     
     out_h
@@ -94,12 +102,13 @@ fn msg_u8_to_u32(msg: [u8; 64]) -> [u32; 16]
         for j in 0..4
         {
             msg32[15 - i] = (msg32[15 - i] << 8) + msg[64 - 4*(i + 1) + j] as u32;
-        };
-    };
-    
+        }
+    }
+        
     msg32
 }
 
+
 // SHA-256 hash function
 pub fn digest<N>(msg: [u8; N]) -> [u8; 32] {
     let mut msg_block: [u8; 64] = [0; 64];
@@ -115,7 +124,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 32] {
         if i == 64 { // Enough to hash block
             c = sha_c(msg_u8_to_u32(msg_block), h);
             for j in 0..8 {
-                h[j] = c[j] + h[j];
+                h[j] = crate::wrapping_add(c[j], h[j]);
             }
             
             i = 0;
@@ -141,7 +150,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 32] {
         c = h;
         c = sha_c(msg_u8_to_u32(msg_block), c);
         for j in 0..8 {
-            h[j] += c[j];
+            h[j] = crate::wrapping_add(h[j], c[j]);
         }
         
         i = 0;
@@ -165,7 +174,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 32] {
     c = h;
     c = sha_c(msg_u8_to_u32(msg_block), c);
     for j in 0..8 {
-        h[j] += c[j];
+        h[j] = crate::wrapping_add(h[j], c[j]);
     }
 
     // Return final hash as byte array
```

### noir_stdlib/src/sha512.nr
```diff
@@ -52,9 +52,11 @@ fn sha_w(msg: [u64; 16]) -> [u64; 80] // Expanded message blocks
 
     for j in 16..80
     {
-        w[j] = sha_sigma1(w[j-2]) + w[j-7] + sha_sigma0(w[j-15]) + w[j-16];
+       w[j] = crate::wrapping_add(
+            crate::wrapping_add(sha_sigma1(w[j-2]), w[j-7]), 
+            crate::wrapping_add(sha_sigma0(w[j-15]), w[j-16]),
+        );
     };
-    
     w
 }
 
@@ -67,17 +69,18 @@ fn sha_c(msg: [u64; 16], hash: [u64; 8]) -> [u64; 8]
     let w = sha_w(msg);
     for j in 0..80
     {
-        let t1 = out_h[7] + sha_bigma1(out_h[4]) + sha_ch(out_h[4], out_h[5], out_h[6])
-            + K[j] + w[j];
-        let t2 = sha_bigma0(out_h[0]) + sha_maj(out_h[0], out_h[1], out_h[2]);
+        let out1 = crate::wrapping_add(out_h[7] , sha_bigma1(out_h[4]));
+        let out2 = crate::wrapping_add(out1, sha_ch(out_h[4], out_h[5], out_h[6]));
+        let t1 = crate::wrapping_add(crate::wrapping_add(out2, K[j]), w[j]);
+        let t2 = crate::wrapping_add( sha_bigma0(out_h[0]) , sha_maj(out_h[0], out_h[1], out_h[2]));
         out_h[7] = out_h[6];
         out_h[6] = out_h[5];
         out_h[5] = out_h[4];
-        out_h[4] = out_h[3] + t1;
+        out_h[4] = crate::wrapping_add(out_h[3] , t1);
         out_h[3] = out_h[2];
         out_h[2] = out_h[1];
         out_h[1] = out_h[0];
-        out_h[0] = t1 + t2;
+        out_h[0] = crate::wrapping_add(t1, t2);
     };
     
     out_h
@@ -115,7 +118,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 64]
         if i == 128 { // Enough to hash block
             c = sha_c(msg_u8_to_u64(msg_block), h);
             for j in 0..8 {
-                h[j] += c[j];
+                h[j] = crate::wrapping_add(h[j], c[j]);
             }
             
             i = 0;
@@ -140,7 +143,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 64]
         }
         c = sha_c(msg_u8_to_u64(msg_block), h);
         for j in 0..8 {
-            h[j] += c[j];
+            h[j] = crate::wrapping_add(h[j], c[j]);
         }
         
         i = 0;
@@ -163,7 +166,7 @@ pub fn digest<N>(msg: [u8; N]) -> [u8; 64]
     // Hash final padded block
     c = sha_c(msg_u8_to_u64(msg_block), h);
     for j in 0..8 {
-        h[j] += c[j];
+        h[j] = crate::wrapping_add(h[j], c[j]);
     }
 
     // Return final hash as byte array
```

### tooling/nargo_cli/tests/execution_success/brillig_fns_as_values/src/main.nr
```diff
@@ -1,13 +1,15 @@
+use dep::std;
+
 struct MyStruct {
     operation: fn (u32) -> u32,
 }
 
 fn main(x: u32) {
     assert(wrapper(increment, x) == x + 1);
     assert(wrapper(increment_acir, x) == x + 1);
-    assert(wrapper(decrement, x) == x - 1);
+    assert(wrapper(decrement, x) ==  std::wrapping_sub(x, 1));
     assert(wrapper_with_struct(MyStruct { operation: increment }, x) == x + 1);
-    assert(wrapper_with_struct(MyStruct { operation: decrement }, x) == x - 1);
+    assert(wrapper_with_struct(MyStruct { operation: decrement }, x) == std::wrapping_sub(x, 1));
     // https://github.com/noir-lang/noir/issues/1975
     assert(increment(x) == x + 1);
 }
```
