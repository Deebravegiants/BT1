# [?] fix: use enable_side_effects for u128 multiplication overflow checks (#9115)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-07-04
Source: https://github.com/noir-lang/noir/commit/3beb8f5456df2ecc9dbf6a415ba47663fa100dfc
Type: security-commit

## Details
fix: use enable_side_effects for u128 multiplication overflow checks (#9115)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/check_u128_mul_overflow.rs
```diff
@@ -90,6 +90,7 @@ fn check_u128_mul_overflow(
 
     let u128 = NumericType::unsigned(128);
     let two_pow_64 = dfg.make_constant(two_pow_64.into(), u128);
+    let mul = BinaryOp::Mul { unchecked: true };
 
     let res = if lhs_value.is_some() && rhs_value.is_some() {
         // If both values are known at compile time, at this point we know it overflows
@@ -118,13 +119,17 @@ fn check_u128_mul_overflow(
             dfg.insert_instruction_and_results(instruction, block, None, call_stack).first();
 
         // Unchecked as operands are restricted to be less than 2^64 so multiplying them cannot overflow.
-        let mul = BinaryOp::Mul { unchecked: true };
         let instruction =
             Instruction::Binary(Binary { lhs: divided_lhs, rhs: divided_rhs, operator: mul });
         dfg.insert_instruction_and_results(instruction, block, None, call_stack).first()
     };
 
     let zero = dfg.make_constant(FieldElement::zero(), u128);
+    let instruction = Instruction::Cast(context.enable_side_effects, u128);
+    let predicate =
+        dfg.insert_instruction_and_results(instruction, block, None, call_stack).first();
+    let instruction = Instruction::Binary(Binary { lhs: res, rhs: predicate, operator: mul });
+    let res = dfg.insert_instruction_and_results(instruction, block, None, call_stack).first();
     let instruction = Instruction::Constrain(
         res,
         zero,
@@ -278,4 +283,34 @@ mod tests {
         let ssa = ssa.check_u128_mul_overflow();
         assert_normalized_ssa_equals(ssa, src);
     }
+    #[test]
+    fn predicate_overflow() {
+        // This code performs a u128 multiplication that overflows, under a condition.
+        let src = "
+        acir(inline) fn main f0 {
+        b0(v0: u1):
+            jmpif v0 then: b1, else: b2
+        b1():
+            v2 = mul u128 340282366920938463463374607431768211455, u128 340282366920938463463374607431768211455	// src/main.nr:17:13
+            jmp b2()
+        b2():
+            return v0
+        }
+        ";
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.flatten_cfg().check_u128_mul_overflow();
+        // Below, the overflow check takes the 'enable_side_effects' value into account
+        assert_ssa_snapshot!(ssa, @r#"
+        acir(inline) fn main f0 {
+          b0(v0: u1):
+            enable_side_effects v0
+            v2 = mul u128 340282366920938463463374607431768211455, u128 340282366920938463463374607431768211455
+            v3 = cast v0 as u128
+            constrain v3 == u128 0, "attempt to multiply with overflow"
+            v5 = not v0
+            enable_side_effects u1 1
+            return v0
+        }
+        "#);
+    }
 }
```

### compiler/noirc_evaluator/src/ssa/opt/simple_optimization.rs
```diff
@@ -1,10 +1,13 @@
+use acvm::FieldElement;
+
 use crate::{
     errors::RtResult,
     ssa::ir::{
         basic_block::BasicBlockId,
         dfg::DataFlowGraph,
         function::Function,
         instruction::{Instruction, InstructionId},
+        types::NumericType,
         value::{ValueId, ValueMapping},
     },
 };
@@ -56,24 +59,27 @@ impl Function {
         F: FnMut(&mut SimpleOptimizationContext<'_, '_>) -> RtResult<()>,
     {
         let mut values_to_replace = ValueMapping::default();
-
+        let mut enable_side_effects =
+            self.dfg.make_constant(FieldElement::from(1_u128), NumericType::bool());
         for block_id in self.reachable_blocks() {
             let instruction_ids = self.dfg[block_id].take_instructions();
             self.dfg[block_id].instructions_mut().reserve(instruction_ids.len());
             for instruction_id in &instruction_ids {
                 let instruction_id = *instruction_id;
-
+                let instruction = &mut self.dfg[instruction_id];
                 if !values_to_replace.is_empty() {
-                    let instruction = &mut self.dfg[instruction_id];
                     instruction.replace_values(&values_to_replace);
                 }
-
+                if let Instruction::EnableSideEffectsIf { condition } = instruction {
+                    enable_side_effects = *condition;
+                }
                 let mut context = SimpleOptimizationContext {
                     block_id,
                     instruction_id,
                     dfg: &mut self.dfg,
                     values_to_replace: &mut values_to_replace,
                     insert_current_instruction_at_callback_end: true,
+                    enable_side_effects,
                 };
                 f(&mut context)?;
 
@@ -95,6 +101,7 @@ pub(crate) struct SimpleOptimizationContext<'dfg, 'mapping> {
     pub(crate) block_id: BasicBlockId,
     pub(crate) instruction_id: InstructionId,
     pub(crate) dfg: &'dfg mut DataFlowGraph,
+    pub(crate) enable_side_effects: ValueId,
     values_to_replace: &'mapping mut ValueMapping,
     insert_current_instruction_at_callback_end: bool,
 }
```
