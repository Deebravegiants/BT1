# [?] fix: match rust behaviour for left-shift overflow (#3518)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-11-22
Source: https://github.com/noir-lang/noir/commit/2d7ceb17edda1d9e70901cfd13f45cdc0df0d28d
Type: security-commit

## Details
fix: match rust behaviour for left-shift overflow (#3518)

## Patch
### compiler/noirc_evaluator/src/ssa/function_builder/mod.rs
```diff
@@ -260,22 +260,6 @@ impl FunctionBuilder {
         arguments: Vec<ValueId>,
         result_types: Vec<Type>,
     ) -> Cow<[ValueId]> {
-        if let Value::Intrinsic(intrinsic) = &self.current_function.dfg[func] {
-            if intrinsic == &Intrinsic::WrappingShiftLeft {
-                let result_type = self.current_function.dfg.type_of_value(arguments[0]);
-                let bit_size = match result_type {
-                    Type::Numeric(NumericType::Signed { bit_size })
-                    | Type::Numeric(NumericType::Unsigned { bit_size }) => bit_size,
-                    _ => {
-                        unreachable!("ICE: Truncation attempted on non-integer");
-                    }
-                };
-                return self
-                    .insert_wrapping_shift_left(arguments[0], arguments[1], bit_size)
-                    .results();
-            }
-        }
-
         self.insert_instruction(Instruction::Call { func, arguments }, Some(result_types)).results()
     }
 
@@ -290,12 +274,12 @@ impl FunctionBuilder {
 
     /// Insert ssa instructions which computes lhs << rhs by doing lhs*2^rhs
     /// and truncate the result to bit_size
-    fn insert_wrapping_shift_left(
+    pub(crate) fn insert_wrapping_shift_left(
         &mut self,
         lhs: ValueId,
         rhs: ValueId,
         bit_size: u32,
-    ) -> InsertInstructionResult {
+    ) -> ValueId {
         let base = self.field_constant(FieldElement::from(2_u128));
         let typ = self.current_function.dfg.type_of_value(lhs);
         let (max_bit, pow) = if let Some(rhs_constant) =
@@ -307,7 +291,7 @@ impl FunctionBuilder {
                 2_u32.overflowing_pow(rhs_constant.to_u128() as u32);
             if overflows {
                 let zero = self.numeric_constant(FieldElement::zero(), typ);
-                return InsertInstructionResult::SimplifiedTo(zero);
+                return InsertInstructionResult::SimplifiedTo(zero).first();
             }
             let pow = self.numeric_constant(FieldElement::from(rhs_bit_size_pow_2 as u128), typ);
             (bit_size + (rhs_constant.to_u128() as u32), pow)
@@ -327,13 +311,14 @@ impl FunctionBuilder {
 
         let instruction = Instruction::Binary(Binary { lhs, rhs: pow, operator: BinaryOp::Mul });
         if max_bit <= bit_size {
-            self.insert_instruction(instruction, None)
+            self.insert_instruction(instruction, None).first()
         } else {
             let result = self.insert_instruction(instruction, None).first();
             self.insert_instruction(
                 Instruction::Truncate { value: result, bit_size, max_bit_size: max_bit },
                 None,
             )
+            .first()
         }
     }
 
```

### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -46,7 +46,6 @@ pub(crate) enum Intrinsic {
     BlackBox(BlackBoxFunc),
     FromField,
     AsField,
-    WrappingShiftLeft,
 }
 
 impl std::fmt::Display for Intrinsic {
@@ -69,7 +68,6 @@ impl std::fmt::Display for Intrinsic {
             Intrinsic::BlackBox(function) => write!(f, "{function}"),
             Intrinsic::FromField => write!(f, "from_field"),
             Intrinsic::AsField => write!(f, "as_field"),
-            Intrinsic::WrappingShiftLeft => write!(f, "wrapping_shift_left"),
         }
     }
 }
@@ -94,8 +92,7 @@ impl Intrinsic {
             | Intrinsic::ToBits(_)
             | Intrinsic::ToRadix(_)
             | Intrinsic::FromField
-            | Intrinsic::AsField
-            | Intrinsic::WrappingShiftLeft => false,
+            | Intrinsic::AsField => false,
 
             // Some black box functions have side-effects
             Intrinsic::BlackBox(func) => matches!(func, BlackBoxFunc::RecursiveAggregation),
@@ -122,7 +119,6 @@ impl Intrinsic {
             "to_be_bits" => Some(Intrinsic::ToBits(Endian::Big)),
             "from_field" => Some(Intrinsic::FromField),
             "as_field" => Some(Intrinsic::AsField),
-            "wrapping_shift_left" => Some(Intrinsic::WrappingShiftLeft),
             other => BlackBoxFunc::lookup(other).map(Intrinsic::BlackBox),
         }
     }
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/call.rs
```diff
@@ -245,9 +245,6 @@ pub(super) fn simplify_call(
             let instruction = Instruction::Cast(arguments[0], ctrl_typevars.unwrap().remove(0));
             SimplifyResult::SimplifiedToInstruction(instruction)
         }
-        Intrinsic::WrappingShiftLeft => {
-            unreachable!("ICE - wrapping shift left should have been proccessed before")
-        }
     }
 }
 
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -363,29 +363,48 @@ impl<'a> FunctionContext<'a> {
                     BinaryOpKind::ShiftLeft => "left shift",
                     _ => unreachable!("operator {} should not overflow", operator),
                 };
-                let message = format!("attempt to {} with overflow", op_name);
-                let range_constraint = Instruction::RangeCheck {
-                    value: result,
-                    max_bit_size: bit_size,
-                    assert_message: Some(message),
-                };
-                self.builder.set_location(location).insert_instruction(range_constraint, None);
+
                 if operator == BinaryOpKind::ShiftLeft {
-                    match result_type {
-                        Type::Numeric(NumericType::Signed { bit_size })
-                        | Type::Numeric(NumericType::Unsigned { bit_size }) => {
-                            self.builder.insert_truncate(result, bit_size, bit_size + 1)
-                        }
-                        _ => result,
-                    }
+                    self.check_left_shift_overflow(result, rhs, bit_size, location)
                 } else {
+                    let message = format!("attempt to {} with overflow", op_name);
+                    let range_constraint = Instruction::RangeCheck {
+                        value: result,
+                        max_bit_size: bit_size,
+                        assert_message: Some(message),
+                    };
+                    self.builder.set_location(location).insert_instruction(range_constraint, None);
                     result
                 }
             }
             _ => result,
         }
     }
 
+    /// Overflow checks for shift-left
+    /// We use Rust behavior for shift left:
+    /// If rhs is more or equal than the bit size, then we overflow
+    /// If not, we do not overflow and shift left with 0 when bits are falling out of the bit size
+    fn check_left_shift_overflow(
+        &mut self,
+        result: ValueId,
+        rhs: ValueId,
+        bit_size: u32,
+        location: Location,
+    ) -> ValueId {
+        let max = self
+            .builder
+            .numeric_constant(FieldElement::from(bit_size as i128), Type::unsigned(bit_size));
+        let overflow = self.builder.insert_binary(rhs, BinaryOp::Lt, max);
+        let one = self.builder.numeric_constant(FieldElement::one(), Type::bool());
+        self.builder.set_location(location).insert_constrain(
+            overflow,
+            one,
+            Some("attempt to left shift with overflow".to_owned()),
+        );
+        self.builder.insert_truncate(result, bit_size, bit_size + 1)
+    }
+
     /// Insert constraints ensuring that the operation does not overflow the bit size of the result
     /// We assume that:
     /// lhs and rhs are signed integers of bit size bit_size
@@ -486,7 +505,15 @@ impl<'a> FunctionContext<'a> {
         location: Location,
     ) -> Values {
         let mut result = match operator {
-            BinaryOpKind::ShiftLeft => self.builder.insert_shift_left(lhs, rhs),
+            BinaryOpKind::ShiftLeft => {
+                let result_type = self.builder.current_function.dfg.type_of_value(lhs);
+                let bit_size = match result_type {
+                    Type::Numeric(NumericType::Signed { bit_size })
+                    | Type::Numeric(NumericType::Unsigned { bit_size }) => bit_size,
+                    _ => unreachable!("ICE: Truncation attempted on non-integer"),
+                };
+                self.builder.insert_wrapping_shift_left(lhs, rhs, bit_size)
+            }
             BinaryOpKind::ShiftRight => self.builder.insert_shift_right(lhs, rhs),
             BinaryOpKind::Equal | BinaryOpKind::NotEqual
                 if matches!(self.builder.type_of_value(lhs), Type::Array(..)) =>
```

### noir_stdlib/src/lib.nr
```diff
@@ -61,7 +61,3 @@ pub fn wrapping_sub<T>(x: T, y: T) -> T {
 pub fn wrapping_mul<T>(x: T, y: T) -> T {
     crate::from_field(crate::as_field(x) * crate::as_field(y))
 }
-/// Shift-left x by y bits
-/// If the result overflow the bitsize; it does not fail and returns 0 instead
-#[builtin(wrapping_shift_left)]
-pub fn wrapping_shift_left<T>(_x: T, _y: T) -> T {}
```

### noir_stdlib/src/sha256.nr
```diff
@@ -6,7 +6,7 @@ fn rotr32(a: u32, b: u32) -> u32 // 32-bit right rotation
 {
     // None of the bits overlap between `(a >> b)` and `(a << (32 - b))`
     // Addition is then equivalent to OR, with fewer constraints.
-    (a >> b) + (crate::wrapping_shift_left(a, 32 - b))
+    (a >> b) + (a << (32 - b))
 }
 
 fn ch(x: u32, y: u32, z: u32) -> u32 {
```

### noir_stdlib/src/sha512.nr
```diff
@@ -6,7 +6,7 @@ fn rotr64(a: u64, b: u64) -> u64 // 64-bit right rotation
 {
     // None of the bits overlap between `(a >> b)` and `(a << (64 - b))`
     // Addition is then equivalent to OR, with fewer constraints.
-    (a >> b) + (crate::wrapping_shift_left(a, 64 - b))
+    (a >> b) + (a << (64 - b))
 }
 
 fn sha_ch(x: u64, y: u64, z: u64) -> u64 {
```

### tooling/nargo_cli/tests/execution_success/bit_shifts_comptime/src/main.nr
```diff
@@ -10,6 +10,9 @@ fn main(x: u64) {
     assert(x >> 2 == 16);
 
     regression_2250();
+
+    //regression for 3481
+    assert(x << 63 == 0);
 }
 
 fn regression_2250() {
```
