# [?] fix(ssa)!: Signed shift overflow checks rhs < bit_size (#9685)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-08-29
Source: https://github.com/noir-lang/noir/commit/a38288aeba7ecd4a3c8e94040201f4fe5104f729
Type: security-commit

## Details
fix(ssa)!: Signed shift overflow checks rhs < bit_size (#9685)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -203,7 +203,7 @@ pub(crate) fn eval_constant_binary_op(
                     return Failure("attempt to divide by zero".to_string());
                 }
                 BinaryOp::Shr | BinaryOp::Shl => {
-                    if rhs >= (bit_size - 1) as i128 {
+                    if rhs >= bit_size as i128 {
                         let op = binary_op_function_name(operator);
                         return Failure(format!("attempt to {op} with overflow"));
                     } else {
```

### compiler/noirc_evaluator/src/ssa/opt/remove_bit_shifts.rs
```diff
@@ -256,24 +256,23 @@ impl Context<'_, '_, '_> {
 
         let assert_message = Some("attempt to bit-shift with overflow".to_owned());
 
-        let (bit_size, max_bit_size) = match rhs_type {
-            Type::Numeric(NumericType::Unsigned { bit_size }) => (bit_size, bit_size),
+        let bit_size = match rhs_type {
+            Type::Numeric(NumericType::Unsigned { bit_size }) => bit_size,
             Type::Numeric(NumericType::Signed { bit_size }) => {
                 assert!(bit_size > 1, "ICE - i1 is not a valid type");
-
-                (bit_size, bit_size - 1)
+                bit_size
             }
             _ => unreachable!("check_shift_overflow called with non-numeric type"),
         };
-        let bit_size_field = FieldElement::from(max_bit_size);
+        let bit_size_field = FieldElement::from(bit_size);
 
         let unsigned_typ = NumericType::unsigned(bit_size);
         let max = self.numeric_constant(bit_size_field, unsigned_typ);
         let rhs = self.insert_cast(rhs, unsigned_typ);
         let overflow = self.insert_binary(rhs, BinaryOp::Lt, max);
         self.insert_constrain(overflow, one, assert_message.map(Into::into));
 
-        max_bit_size
+        bit_size
     }
 
     pub(crate) fn field_constant(&mut self, constant: FieldElement) -> ValueId {
@@ -643,7 +642,7 @@ mod tests {
             acir(inline) fn main f0 {
               b0(v0: i32, v1: i32):
                 v2 = cast v1 as u32
-                v4 = lt v2, u32 31
+                v4 = lt v2, u32 32
                 constrain v4 == u1 1, "attempt to bit-shift with overflow"
                 v6 = cast v1 as Field
                 v8 = call to_le_bits(v6) -> [u1; 5]
@@ -743,7 +742,7 @@ mod tests {
             acir(inline) fn main f0 {
               b0(v0: i32, v1: i32):
                 v2 = cast v1 as u32
-                v4 = lt v2, u32 31
+                v4 = lt v2, u32 32
                 constrain v4 == u1 1, "attempt to bit-shift with overflow"
                 v6 = cast v1 as Field
                 v8 = call to_le_bits(v6) -> [u1; 5]
```

### docs/docs/noir/concepts/ops.md
```diff
@@ -65,7 +65,7 @@ fn main(x : Field) {
 
 Bit shifts left: `<<`, or right: `>>` require the right hand side operand to be less that the bit size `s` of the operands type:
 `x << y` or `x >> y` overflow if `x,y` are unsigned and `y >= s`
-`x << y` or `x >> y` overflow if `x,y` are signed and `y >= s-1`
+`x << y` or `x >> y` overflow if `x,y` are signed and `y >= s`
 
 ### Logical Operators
 
```

### test_programs/compile_failure/shl_signed_regression_9592/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "shl_signed_regression_9592"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/shl_signed_regression_9592/src/main.nr
```diff
@@ -0,0 +1,11 @@
+fn main() -> pub i64 {
+    comptime {
+        func_1()
+    }
+}
+unconstrained fn func_1() -> i64 {
+    (-1525866727742442465_i64 / -7342926532602101880_i64) << func_2()
+}
+unconstrained fn func_2() -> i64 {
+    -877061792390071735_i64
+}
```

### test_programs/execution_failure/shl_signed_regression_9592/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "shl_signed_regression_9592"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/shl_signed_regression_9592/src/main.nr
```diff
@@ -0,0 +1,11 @@
+fn main() -> pub i64 {
+    unsafe {
+        func_1()
+    }
+}
+unconstrained fn func_1() -> i64 {
+    (-1525866727742442465_i64 / -7342926532602101880_i64) << func_2()
+}
+unconstrained fn func_2() -> i64 {
+    -877061792390071735_i64
+}
```

### test_programs/execution_success/shl_signed_regression_9661/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "shl_signed_regression_9661"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/shl_signed_regression_9661/Prover.toml
```diff
@@ -0,0 +1 @@
+return = 7
\ No newline at end of file
```

### test_programs/execution_success/shl_signed_regression_9661/src/main.nr
```diff
@@ -0,0 +1,11 @@
+fn main() -> pub i8 {
+    // Safety: testing context
+    unsafe {
+        foo(7_i8)
+    }
+}
+
+unconstrained fn foo(a: i8) -> i8 {
+    let _ = 1_i8 << a;
+    a
+}
```

### test_programs/noir_test_success/bit_shifts/src/main.nr
```diff
@@ -93,9 +93,29 @@ fn test_bit_shifts00() {
     assert_eq(shift(2434, 11), a);
 }
 
+#[test]
+fn test_signed_shr_i8_rhs_bit_size_minus_one() {
+    assert_eq(2_i8 >> 7, 0)
+}
+
+#[test]
+fn test_signed_shl_i8_rhs_bit_size_minus_one() {
+    assert_eq(2_i8 << 7, 0)
+}
+
+#[test]
+fn test_signed_shr_i32_rhs_bit_size_minus_one() {
+    assert_eq(2_i32 >> 31, 0)
+}
+
+#[test]
+fn test_signed_shl_i32_rhs_bit_size_minus_one() {
+    assert_eq(2_i32 << 31, 0)
+}
+
 #[test(should_fail)]
 fn test_bit_shifts_overflow1() -> i8 {
-    2_i8 >> 7
+    2_i8 >> 8
 }
 
 #[test(should_fail)]
@@ -105,7 +125,7 @@ fn test_bit_shifts_overflow2() -> u8 {
 
 #[test(should_fail)]
 fn test_bit_shifts_overflow3() -> i32 {
-    2_i32 >> 31
+    2_i32 >> 32
 }
 
 #[test(should_fail)]
```

### tooling/nargo_cli/tests/snapshots/compile_failure/shl_signed_regression_9592/execute__tests__stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Attempt to bit-shift with overflow
+  ┌─ src/main.nr:7:5
+  │
+7 │     (-1525866727742442465_i64 / -7342926532602101880_i64) << func_2()
+  │     -----------------------------------------------------------------
+  │
+
+Aborting due to 1 previous error
```
