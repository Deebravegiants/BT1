# [?] fix: defer overflow checks for unsigned integers to acir-gen (#4832)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-05-08
Source: https://github.com/noir-lang/noir/commit/b5777613c51f26fb4f580b9168c4190b1f4bd8f7
Type: security-commit

## Details
fix: defer overflow checks for unsigned integers to acir-gen (#4832)

# Description

## Problem\*

Resolves #4456

## Summary\*

Overflow checks for unsigned integers are done in acir-gen, when
converting arithmetic operations into field arithmetic. That way the
semantic of the ssa unsigned operations is preserved.

## Additional Context

As indicated in the issue, I did not touch signed integers, but it could
be cleaner to convert them into unsigned operations (and have the signed
overflow checks done with additional ssa instructions, like we do
currently)

## Documentation\*

Check one:
- [X] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [X] I have tested the changes locally.
- [X] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

---------

Co-authored-by: Tom French <tom@tomfren.ch>

## Patch
### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_block.rs
```diff
@@ -1340,7 +1340,15 @@ impl<'block> BrilligBlock<'block> {
 
         self.brillig_context.binary_instruction(left, right, result_variable, brillig_binary_op);
 
-        self.add_overflow_check(brillig_binary_op, left, right, result_variable, is_signed);
+        self.add_overflow_check(
+            brillig_binary_op,
+            left,
+            right,
+            result_variable,
+            binary,
+            dfg,
+            is_signed,
+        );
     }
 
     /// Splits a two's complement signed integer in the sign bit and the absolute value.
@@ -1493,22 +1501,32 @@ impl<'block> BrilligBlock<'block> {
         self.brillig_context.deallocate_single_addr(bias);
     }
 
+    #[allow(clippy::too_many_arguments)]
     fn add_overflow_check(
         &mut self,
         binary_operation: BrilligBinaryOp,
         left: SingleAddrVariable,
         right: SingleAddrVariable,
         result: SingleAddrVariable,
+        binary: &Binary,
+        dfg: &DataFlowGraph,
         is_signed: bool,
     ) {
         let bit_size = left.bit_size;
+        let max_lhs_bits = dfg.get_value_max_num_bits(binary.lhs);
+        let max_rhs_bits = dfg.get_value_max_num_bits(binary.rhs);
 
         if bit_size == FieldElement::max_num_bits() {
             return;
         }
 
         match (binary_operation, is_signed) {
             (BrilligBinaryOp::Add, false) => {
+                if std::cmp::max(max_lhs_bits, max_rhs_bits) < bit_size {
+                    // `left` and `right` have both been casted up from smaller types and so cannot overflow.
+                    return;
+                }
+
                 let condition =
                     SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
                 // Check that lhs <= result
@@ -1523,6 +1541,12 @@ impl<'block> BrilligBlock<'block> {
                 self.brillig_context.deallocate_single_addr(condition);
             }
             (BrilligBinaryOp::Sub, false) => {
+                if dfg.is_constant(binary.lhs) && max_lhs_bits > max_rhs_bits {
+                    // `left` is a fixed constant and `right` is restricted such that `left - right > 0`
+                    // Note strict inequality as `right > left` while `max_lhs_bits == max_rhs_bits` is possible.
+                    return;
+                }
+
                 let condition =
                     SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
                 // Check that rhs <= lhs
@@ -1539,39 +1563,36 @@ impl<'block> BrilligBlock<'block> {
                 self.brillig_context.deallocate_single_addr(condition);
             }
             (BrilligBinaryOp::Mul, false) => {
-                // Multiplication overflow is only possible for bit sizes > 1
-                if bit_size > 1 {
-                    let is_right_zero =
-                        SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
-                    let zero =
-                        self.brillig_context.make_constant_instruction(0_usize.into(), bit_size);
-                    self.brillig_context.binary_instruction(
-                        zero,
-                        right,
-                        is_right_zero,
-                        BrilligBinaryOp::Equals,
-                    );
-                    self.brillig_context.codegen_if_not(is_right_zero.address, |ctx| {
-                        let condition = SingleAddrVariable::new(ctx.allocate_register(), 1);
-                        let division = SingleAddrVariable::new(ctx.allocate_register(), bit_size);
-                        // Check that result / rhs == lhs
-                        ctx.binary_instruction(
-                            result,
-                            right,
-                            division,
-                            BrilligBinaryOp::UnsignedDiv,
-                        );
-                        ctx.binary_instruction(division, left, condition, BrilligBinaryOp::Equals);
-                        ctx.codegen_constrain(
-                            condition,
-                            Some("attempt to multiply with overflow".to_string()),
-                        );
-                        ctx.deallocate_single_addr(condition);
-                        ctx.deallocate_single_addr(division);
-                    });
-                    self.brillig_context.deallocate_single_addr(is_right_zero);
-                    self.brillig_context.deallocate_single_addr(zero);
+                if bit_size == 1 || max_lhs_bits + max_rhs_bits <= bit_size {
+                    // Either performing boolean multiplication (which cannot overflow),
+                    // or `left` and `right` have both been casted up from smaller types and so cannot overflow.
+                    return;
                 }
+
+                let is_right_zero =
+                    SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
+                let zero = self.brillig_context.make_constant_instruction(0_usize.into(), bit_size);
+                self.brillig_context.binary_instruction(
+                    zero,
+                    right,
+                    is_right_zero,
+                    BrilligBinaryOp::Equals,
+                );
+                self.brillig_context.codegen_if_not(is_right_zero.address, |ctx| {
+                    let condition = SingleAddrVariable::new(ctx.allocate_register(), 1);
+                    let division = SingleAddrVariable::new(ctx.allocate_register(), bit_size);
+                    // Check that result / rhs == lhs
+                    ctx.binary_instruction(result, right, division, BrilligBinaryOp::UnsignedDiv);
+                    ctx.binary_instruction(division, left, condition, BrilligBinaryOp::Equals);
+                    ctx.codegen_constrain(
+                        condition,
+                        Some("attempt to multiply with overflow".to_string()),
+                    );
+                    ctx.deallocate_single_addr(condition);
+                    ctx.deallocate_single_addr(division);
+                });
+                self.brillig_context.deallocate_single_addr(is_right_zero);
+                self.brillig_context.deallocate_single_addr(zero);
             }
             _ => {}
         }
```

### compiler/noirc_evaluator/src/ssa/acir_gen/mod.rs
```diff
@@ -1818,15 +1818,15 @@ impl<'a> Context<'a> {
 
         let binary_type = AcirType::from(binary_type);
         let bit_count = binary_type.bit_size();
-
-        match binary.operator {
+        let num_type = binary_type.to_numeric_type();
+        let result = match binary.operator {
             BinaryOp::Add => self.acir_context.add_var(lhs, rhs),
             BinaryOp::Sub => self.acir_context.sub_var(lhs, rhs),
             BinaryOp::Mul => self.acir_context.mul_var(lhs, rhs),
             BinaryOp::Div => self.acir_context.div_var(
                 lhs,
                 rhs,
-                binary_type,
+                binary_type.clone(),
                 self.current_side_effects_enabled_var,
             ),
             // Note: that this produces unnecessary constraints when
@@ -1850,7 +1850,71 @@ impl<'a> Context<'a> {
             BinaryOp::Shl | BinaryOp::Shr => unreachable!(
                 "ICE - bit shift operators do not exist in ACIR and should have been replaced"
             ),
+        }?;
+
+        if let NumericType::Unsigned { bit_size } = &num_type {
+            // Check for integer overflow
+            self.check_unsigned_overflow(
+                result,
+                *bit_size,
+                binary.lhs,
+                binary.rhs,
+                dfg,
+                binary.operator,
+            )?;
         }
+
+        Ok(result)
+    }
+
+    /// Adds a range check against the bit size of the result of addition, subtraction or multiplication
+    fn check_unsigned_overflow(
+        &mut self,
+        result: AcirVar,
+        bit_size: u32,
+        lhs: ValueId,
+        rhs: ValueId,
+        dfg: &DataFlowGraph,
+        op: BinaryOp,
+    ) -> Result<(), RuntimeError> {
+        // We try to optimize away operations that are guaranteed not to overflow
+        let max_lhs_bits = dfg.get_value_max_num_bits(lhs);
+        let max_rhs_bits = dfg.get_value_max_num_bits(rhs);
+
+        let msg = match op {
+            BinaryOp::Add => {
+                if std::cmp::max(max_lhs_bits, max_rhs_bits) < bit_size {
+                    // `lhs` and `rhs` have both been casted up from smaller types and so cannot overflow.
+                    return Ok(());
+                }
+                "attempt to add with overflow".to_string()
+            }
+            BinaryOp::Sub => {
+                if dfg.is_constant(lhs) && max_lhs_bits > max_rhs_bits {
+                    // `lhs` is a fixed constant and `rhs` is restricted such that `lhs - rhs > 0`
+                    // Note strict inequality as `rhs > lhs` while `max_lhs_bits == max_rhs_bits` is possible.
+                    return Ok(());
+                }
+                "attempt to subtract with overflow".to_string()
+            }
+            BinaryOp::Mul => {
+                if bit_size == 1 || max_lhs_bits + max_rhs_bits <= bit_size {
+                    // Either performing boolean multiplication (which cannot overflow),
+                    // or `lhs` and `rhs` have both been casted up from smaller types and so cannot overflow.
+                    return Ok(());
+                }
+                "attempt to multiply with overflow".to_string()
+            }
+            _ => return Ok(()),
+        };
+
+        let with_pred = self.acir_context.mul_var(result, self.current_side_effects_enabled_var)?;
+        self.acir_context.range_constrain_var(
+            with_pred,
+            &NumericType::Unsigned { bit_size },
+            Some(msg),
+        )?;
+        Ok(())
     }
 
     /// Operands in a binary operation are checked to have the same type.
```

### compiler/noirc_evaluator/src/ssa/opt/remove_bit_shifts.rs
```diff
@@ -109,7 +109,7 @@ impl Context<'_> {
                     return InsertInstructionResult::SimplifiedTo(zero).first();
                 }
             }
-            let pow = self.numeric_constant(FieldElement::from(rhs_bit_size_pow_2), typ);
+            let pow = self.numeric_constant(FieldElement::from(rhs_bit_size_pow_2), typ.clone());
 
             let max_lhs_bits = self.function.dfg.get_value_max_num_bits(lhs);
 
@@ -123,15 +123,18 @@ impl Context<'_> {
             // we can safely cast to unsigned because overflow_checks prevent bit-shift with a negative value
             let rhs_unsigned = self.insert_cast(rhs, Type::unsigned(bit_size));
             let pow = self.pow(base, rhs_unsigned);
-            let pow = self.insert_cast(pow, typ);
+            let pow = self.insert_cast(pow, typ.clone());
             (FieldElement::max_num_bits(), self.insert_binary(predicate, BinaryOp::Mul, pow))
         };
 
         if max_bit <= bit_size {
             self.insert_binary(lhs, BinaryOp::Mul, pow)
         } else {
-            let result = self.insert_binary(lhs, BinaryOp::Mul, pow);
-            self.insert_truncate(result, bit_size, max_bit)
+            let lhs_field = self.insert_cast(lhs, Type::field());
+            let pow_field = self.insert_cast(pow, Type::field());
+            let result = self.insert_binary(lhs_field, BinaryOp::Mul, pow_field);
+            let result = self.insert_truncate(result, bit_size, max_bit);
+            self.insert_cast(result, typ)
         }
     }
 
```

### compiler/noirc_evaluator/src/ssa/opt/remove_enable_side_effects.rs
```diff
@@ -108,17 +108,19 @@ impl Context {
     fn responds_to_side_effects_var(dfg: &DataFlowGraph, instruction: &Instruction) -> bool {
         use Instruction::*;
         match instruction {
-            Binary(binary) => {
-                if matches!(binary.operator, BinaryOp::Div | BinaryOp::Mod) {
+            Binary(binary) => match binary.operator {
+                BinaryOp::Add | BinaryOp::Sub | BinaryOp::Mul => {
+                    dfg.type_of_value(binary.lhs).is_unsigned()
+                }
+                BinaryOp::Div | BinaryOp::Mod => {
                     if let Some(rhs) = dfg.get_numeric_constant(binary.rhs) {
                         rhs == FieldElement::zero()
                     } else {
                         true
                     }
-                } else {
-                    false
                 }
-            }
+                _ => false,
+            },
 
             Cast(_, _)
             | Not(_)
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -304,7 +304,7 @@ impl<'a> FunctionContext<'a> {
 
     /// Insert constraints ensuring that the operation does not overflow the bit size of the result
     ///
-    /// If the result is unsigned, we simply range check against the bit size
+    /// If the result is unsigned, overflow will be checked during acir-gen (cf. issue #4456), except for bit-shifts, because we will convert them to field multiplication
     ///
     /// If the result is signed, we just prepare it for check_signed_overflow() by casting it to
     /// an unsigned value representing the signed integer.
@@ -351,51 +351,12 @@ impl<'a> FunctionContext<'a> {
             }
             Type::Numeric(NumericType::Unsigned { bit_size }) => {
                 let dfg = &self.builder.current_function.dfg;
-
-                let max_lhs_bits = self.builder.current_function.dfg.get_value_max_num_bits(lhs);
-                let max_rhs_bits = self.builder.current_function.dfg.get_value_max_num_bits(rhs);
+                let max_lhs_bits = dfg.get_value_max_num_bits(lhs);
 
                 match operator {
-                    BinaryOpKind::Add => {
-                        if std::cmp::max(max_lhs_bits, max_rhs_bits) < bit_size {
-                            // `lhs` and `rhs` have both been casted up from smaller types and so cannot overflow.
-                            return result;
-                        }
-
-                        let message = "attempt to add with overflow".to_string();
-                        self.builder.set_location(location).insert_range_check(
-                            result,
-                            bit_size,
-                            Some(message),
-                        );
-                    }
-                    BinaryOpKind::Subtract => {
-                        if dfg.is_constant(lhs) && max_lhs_bits > max_rhs_bits {
-                            // `lhs` is a fixed constant and `rhs` is restricted such that `lhs - rhs > 0`
-                            // Note strict inequality as `rhs > lhs` while `max_lhs_bits == max_rhs_bits` is possible.
-                            return result;
-                        }
-
-                        let message = "attempt to subtract with overflow".to_string();
-                        self.builder.set_location(location).insert_range_check(
-                            result,
-                            bit_size,
-                            Some(message),
-                        );
-                    }
-                    BinaryOpKind::Multiply => {
-                        if bit_size == 1 || max_lhs_bits + max_rhs_bits <= bit_size {
-                            // Either performing boolean multiplication (which cannot overflow),
-                            // or `lhs` and `rhs` have both been casted up from smaller types and so cannot overflow.
-                            return result;
-                        }
-
-                        let message = "attempt to multiply with overflow".to_string();
-                        self.builder.set_location(location).insert_range_check(
-                            result,
-                            bit_size,
-                            Some(message),
-                        );
+                    BinaryOpKind::Add | BinaryOpKind::Subtract | BinaryOpKind::Multiply => {
+                        // Overflow check is deferred to acir-gen
+                        return result;
                     }
                     BinaryOpKind::ShiftLeft => {
                         if let Some(rhs_const) = dfg.get_numeric_constant(rhs) {
```
