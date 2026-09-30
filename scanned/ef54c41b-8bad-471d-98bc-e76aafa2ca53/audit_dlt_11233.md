# [?] fix(ssa): keep checked overflow check when simplifying +0/-0/*1 on unfit operands (#12982)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-10
Source: https://github.com/noir-lang/noir/commit/18906e1adcfacc795ae88d47dabb4fa803faf074
Type: security-commit

## Details
fix(ssa): keep checked overflow check when simplifying +0/-0/*1 on unfit operands (#12982)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify/binary.rs
```diff
@@ -8,6 +8,7 @@ use crate::ssa::ir::{
         binary::{BinaryEvaluationResult, eval_constant_binary_op},
     },
     types::NumericType,
+    value::ValueId,
 };
 use noirc_errors::call_stack::CallStackId;
 
@@ -80,29 +81,29 @@ pub(super) fn simplify_binary(
         rhs_value.is_some_and(|rhs| rhs_type.max_value().is_ok_and(|max_value| rhs == max_value));
 
     match binary.operator {
-        BinaryOp::Add { .. } => {
-            if lhs_is_zero {
+        BinaryOp::Add { unchecked } => {
+            if lhs_is_zero && can_simplify_arithmetic_identity(dfg, rhs, lhs_type, unchecked) {
                 return SimplifyResult::SimplifiedTo(rhs);
             }
-            if rhs_is_zero {
+            if rhs_is_zero && can_simplify_arithmetic_identity(dfg, lhs, lhs_type, unchecked) {
                 return SimplifyResult::SimplifiedTo(lhs);
             }
         }
-        BinaryOp::Sub { .. } => {
+        BinaryOp::Sub { unchecked } => {
             if lhs == rhs {
                 let zero = dfg.make_constant(FieldElement::zero(), lhs_type);
                 return SimplifyResult::SimplifiedTo(zero);
             }
 
-            if rhs_is_zero {
+            if rhs_is_zero && can_simplify_arithmetic_identity(dfg, lhs, lhs_type, unchecked) {
                 return SimplifyResult::SimplifiedTo(lhs);
             }
         }
-        BinaryOp::Mul { .. } => {
-            if lhs_is_one {
+        BinaryOp::Mul { unchecked } => {
+            if lhs_is_one && can_simplify_arithmetic_identity(dfg, rhs, lhs_type, unchecked) {
                 return SimplifyResult::SimplifiedTo(rhs);
             }
-            if rhs_is_one {
+            if rhs_is_one && can_simplify_arithmetic_identity(dfg, lhs, lhs_type, unchecked) {
                 return SimplifyResult::SimplifiedTo(lhs);
             }
             if lhs_is_zero || rhs_is_zero {
@@ -314,6 +315,44 @@ pub(super) fn simplify_binary(
     SimplifyResult::SimplifiedToInstruction(simplified)
 }
 
+/// Whether a `+0`/`-0`/`*1` identity may be replaced by `operand` without dropping the
+/// operation's overflow semantics.
+///
+/// A checked integer operation range-constrains its result to the type's bit width, so rewriting
+/// it to an operand would silently drop that check. This is only safe when:
+/// - the operation is unchecked (it imposes no range constraint), or
+/// - the type cannot overflow (field arithmetic), or
+/// - `operand` is already known to fit its type.
+///
+/// The only values that can hold a magnitude outside their type's range are results of unchecked
+/// `add`/`sub`/`mul`. Every other value — numeric constants, block parameters, casts (which
+/// truncate/extend to the target type) and checked arithmetic (whose result is range-constrained)
+/// — is guaranteed to fit its type.
+fn can_simplify_arithmetic_identity(
+    dfg: &DataFlowGraph,
+    operand: ValueId,
+    operand_type: NumericType,
+    unchecked: bool,
+) -> bool {
+    if unchecked || operand_type == NumericType::NativeField {
+        return true;
+    }
+
+    if let super::Value::Instruction { instruction, .. } = &dfg[operand] {
+        !matches!(
+            dfg[*instruction],
+            Instruction::Binary(Binary {
+                operator: BinaryOp::Add { unchecked: true }
+                    | BinaryOp::Sub { unchecked: true }
+                    | BinaryOp::Mul { unchecked: true },
+                ..
+            })
+        )
+    } else {
+        true
+    }
+}
+
 #[cfg(test)]
 mod tests {
     use crate::{
@@ -399,6 +438,71 @@ mod tests {
         ");
     }
 
+    #[test]
+    fn does_not_drop_checked_overflow_on_add_zero_identity() {
+        // A checked `add v, 0` range-constrains its result to the type's bit width. When `v` is an
+        // unfit value (here produced by an unchecked overflowing add), simplifying the identity away
+        // would drop that overflow check and let an out-of-range value flow on, so the checked add
+        // is preserved.
+        let src = "
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = unchecked_add u8 255, u8 1
+            v4 = add v2, u8 0
+            return v4
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn does_not_drop_checked_overflow_on_sub_zero_identity() {
+        let src = "
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = unchecked_add u8 255, u8 1
+            v4 = sub v2, u8 0
+            return v4
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn does_not_drop_checked_overflow_on_mul_one_identity() {
+        let src = "
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = unchecked_add u8 255, u8 1
+            v4 = mul v2, u8 1
+            return v4
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn simplifies_add_zero_identity_for_fitting_operand() {
+        // A checked `add v, 0` whose operand is a normal (fit) value is still simplified away.
+        let src = "
+        acir(inline) pure fn main f0 {
+          b0(v0: u8):
+            v1 = add v0, u8 0
+            return v1
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_ssa_snapshot!(ssa, @"
+        acir(inline) pure fn main f0 {
+          b0(v0: u8):
+            return v0
+        }
+        ");
+    }
+
     #[test]
     fn does_not_simplify_signed_integer_or_max() {
         let src = "
```
