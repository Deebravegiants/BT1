# [?] fix: check u128 ops overflow in SSA interpreter (#13469)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-08-26
Source: https://github.com/noir-lang/noir/commit/9198bab82bd38645303b4e9d8faa968392dd4cef
Type: security-commit

## Details
fix: check u128 ops overflow in SSA interpreter (#13469)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -24,6 +24,7 @@ use errors::{InternalError, InterpreterError, MAX_UNSIGNED_BIT_SIZE};
 use iter_extended::{try_vecmap, vecmap};
 use itertools::Itertools;
 use noirc_frontend::Shared;
+use num_bigint::BigUint;
 use rustc_hash::{FxHashMap as HashMap, FxHashSet as HashSet};
 use value::{ArrayValue, NumericValue, ReferenceValue, StorageIdentity};
 
@@ -1634,14 +1635,23 @@ fn evaluate_integer_binary(
 
         // Unsigned checked arithmetic. ACIR computes in the field and range-checks the result, so an
         // out-of-range operand or an overflowing result is rejected; Brillig does true fixed-width
-        // checked arithmetic. (They only diverge once values can exceed the field modulus, i.e.
-        // `u128`, but keeping them separate is faithful to both.)
+        // checked arithmetic. The one place the range check is insufficient is a `u128` product,
+        // whose true value can exceed the field modulus and be reduced back below 2^128: the
+        // circuit rejects it via the constraint the `check_u128_mul_overflow` pass inserts, so the
+        // interpreter decides that overflow on the unreduced product.
         Add { unchecked: false } | Sub { unchecked: false } | Mul { unchecked: false }
             if !lhs.is_signed() =>
         {
             if is_brillig {
                 eval_via_constant_binary_op(lhs_field, rhs_field, operator, typ, binary, &overflow)
             } else {
+                if matches!(operator, Mul { .. }) && bit_size == 128 {
+                    let product = BigUint::from_bytes_be(&lhs_field.to_be_bytes())
+                        * BigUint::from_bytes_be(&rhs_field.to_be_bytes());
+                    if product.bits() > 128 {
+                        return Err(overflow());
+                    }
+                }
                 let value = NumericValue::int_from_field(field_arith(), typ)?;
                 if value.is_in_range() { Ok(value) } else { Err(overflow()) }
             }
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -20,7 +20,7 @@ use crate::ssa::{
     },
 };
 
-use super::{Ssa, executes_with_no_errors, expect_error};
+use super::{Ssa, executes_with_no_errors, expect_error, expect_error_with_args};
 
 fn make_unfit(value: impl Into<FieldElement>, typ: NumericType) -> Value {
     Value::int_from_field(value.into(), typ).unwrap()
@@ -355,6 +355,75 @@ fn mul_overflow_signed() {
     assert!(matches!(error, InterpreterError::Overflow { .. }));
 }
 
+#[test]
+fn mul_overflow_u128_wrapping_past_modulus() {
+    // a = 2^127 + 12345 and b = ⌊p/a⌋ + 1: both fit in a u128, and a·b is the smallest multiple
+    // of a exceeding the modulus, so (a·b) mod p = a - (p mod a) passes a 128-bit range check.
+    let a = 170141183460469231731687303715884118073_u128;
+    let b = 128647529226366354083724114970452069444_u128;
+    let args = vec![
+        from_constant(a.into(), NumericType::unsigned(128)),
+        from_constant(b.into(), NumericType::unsigned(128)),
+    ];
+    for runtime in ["acir(inline)", "brillig(inline)"] {
+        let src = format!(
+            "
+            {runtime} fn main f0 {{
+              b0(v0: u128, v1: u128):
+                v2 = mul v0, v1
+                return v2
+            }}
+        "
+        );
+        let error = expect_error_with_args(&src, args.clone());
+        assert!(matches!(error, InterpreterError::Overflow { .. }), "{runtime}: {error:?}");
+    }
+}
+
+// Companion to [`mul_overflow_u128_wrapping_past_modulus`] with constant operands
+// (`u128::MAX` and `MAX_NON_OVERFLOWING_CONST_ARG + 1` from `check_u128_mul_overflow`).
+#[test]
+fn mul_overflow_u128_wrapping_past_modulus_constants() {
+    let error = expect_error(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mul u128 340282366920938463463374607431768211455, u128 64323764613183177041862057485226039390
+            return v0
+        }
+    ",
+    );
+    assert!(matches!(error, InterpreterError::Overflow { .. }), "{error:?}");
+}
+
+// Companion to [`mul_overflow_u128_wrapping_past_modulus`] pinning the non-wrapping cases, so the
+// wrapping case cannot be fixed by rejecting every u128 multiplication: a product that overflows
+// 128 bits without exceeding the modulus still errors, and an in-range product still succeeds.
+#[test]
+fn mul_overflow_u128_non_wrapping() {
+    let error = expect_error(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mul u128 340282366920938463463374607431768211455, u128 2
+            return v0
+        }
+    ",
+    );
+    assert!(matches!(error, InterpreterError::Overflow { .. }), "{error:?}");
+
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mul u128 3, u128 5
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, from_constant(15_u128.into(), NumericType::unsigned(128)));
+}
+
 #[test]
 fn mul_unchecked_unsigned() {
     let value = expect_value(
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/mod.rs
```diff
@@ -51,8 +51,13 @@ fn expect_value(src: &str) -> Value {
 
 #[track_caller]
 fn expect_error(src: &str) -> InterpreterError {
+    expect_error_with_args(src, Vec::new())
+}
+
+#[track_caller]
+fn expect_error_with_args(src: &str, args: Vec<Value>) -> InterpreterError {
     let ssa = Ssa::from_str(src).unwrap();
-    ssa.interpret(Vec::new()).unwrap_err()
+    ssa.interpret(args).unwrap_err()
 }
 
 #[track_caller]
```

### test_programs/execution_failure/u128_mul_wrapping_overflow/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "u128_mul_wrapping_overflow"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/u128_mul_wrapping_overflow/Prover.toml
```diff
@@ -0,0 +1,4 @@
+# a = 2^127 + 12345 and b = ⌊p/a⌋ + 1 (p is the BN254 scalar field modulus): both fit in a
+# u128, but their true product exceeds p and its mod-p reduction lands back below 2^128.
+a = "170141183460469231731687303715884118073"
+b = "128647529226366354083724114970452069444"
```

### test_programs/execution_failure/u128_mul_wrapping_overflow/src/main.nr
```diff
@@ -0,0 +1,7 @@
+// A checked u128 multiplication whose true product exceeds the field modulus, while the reduced
+// (mod-p) product still fits in 128 bits. The `check_u128_mul_overflow` SSA pass exists to reject
+// exactly this case, and the SSA interpreter must reject it too (noir-lang/noir-claude#1623):
+// both `nargo execute` and `nargo interpret` must report a multiplication overflow.
+fn main(a: u128, b: u128) -> pub u128 {
+    a * b
+}
```

### tooling/nargo_cli/tests/execute.rs
```diff
@@ -339,7 +339,12 @@ mod tests {
     }
 
     fn interpret_execution_failure(mut nargo: Command) {
-        nargo.assert().failure();
+        // The interpreter must fail at every SSA pass: a result that flips between passes means
+        // the interpreter disagrees with some pass's semantics, which is an interpreter or pass
+        // bug even in a program that is expected to fail. Printed output is allowed to differ
+        // between passes, because for programs that exhaust the interpreter's recursion limit the
+        // amount of output produced before the limit legitimately depends on inlining.
+        nargo.assert().failure().stdout(predicate::str::contains("Result changed.").not());
     }
 
     fn nargo_expand_execute(test_program_dir: PathBuf) {
```

### tooling/nargo_cli/tests/snapshots/execution_failure/u128_mul_wrapping_overflow/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: attempt to multiply with overflow
+  ┌─ src/main.nr:6:5
+  │
+6 │     a * b
+  │     -----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:6:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/u128_mul_wrapping_overflow/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: attempt to multiply with overflow
+  ┌─ src/main.nr:6:5
+  │
+6 │     a * b
+  │     -----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:6:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/u128_mul_wrapping_overflow/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Attempt to multiply with overflow
+  ┌─ src/main.nr:6:5
+  │
+6 │     a * b
+  │     -----
+  │
+
+Error interpreting main function
```
